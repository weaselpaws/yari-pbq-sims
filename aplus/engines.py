"""Question-type widgets for the A+ simulator: fill, match, sequence, scenario.

Unlike the Project+/Network+/Security+ engines (which are steps in a fixed
quiz), A+ topics are open-ended practice pools — each widget owns its own
Check/New-round controls and reports results via callbacks, matching the
behavior of the original HTML prototype.
"""
import random

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QFrame,
)


def ip_to_int(ip):
    parts = [int(p) for p in ip.split(".")]
    n = 0
    for p in parts:
        n = n * 256 + p
    return n


def int_to_ip(n):
    return ".".join(str((n >> s) & 255) for s in (24, 16, 8, 0))


def mask_from_cidr(cidr):
    if cidr == 0:
        return 0
    return (0xFFFFFFFF << (32 - cidr)) & 0xFFFFFFFF


class FillEngine(QWidget):
    """Subnetting calculator: given a random IP/CIDR, fill in six fields."""

    FIELD_DEFS = [
        ("mask", "Subnet mask"), ("network", "Network address"),
        ("broadcast", "Broadcast address"), ("first", "First usable host"),
        ("last", "Last usable host"), ("hosts", "Usable hosts"),
    ]

    def __init__(self, topic, record_result, show_modal, parent=None):
        super().__init__(parent)
        self.topic = topic
        self.record_result = record_result
        self.show_modal = show_modal
        self.answer = {}
        self.inputs = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        prompt = QLabel("Given the network below, fill in every field.")
        prompt.setObjectName("prompt")
        layout.addWidget(prompt)

        self.given_label = QLabel()
        self.given_label.setObjectName("given")
        layout.addWidget(self.given_label)

        grid = QGridLayout()
        for row, (key, label) in enumerate(self.FIELD_DEFS):
            lbl = QLabel(label)
            lbl.setObjectName("fieldLabel")
            edit = QLineEdit()
            grid.addWidget(lbl, row // 2 * 2, row % 2)
            grid.addWidget(edit, row // 2 * 2 + 1, row % 2)
            self.inputs[key] = edit
        grid_wrap = QWidget()
        grid_wrap.setLayout(grid)
        layout.addWidget(grid_wrap)

        btn_row = QHBoxLayout()
        self.check_btn = QPushButton("Check answers")
        self.check_btn.setObjectName("btnPrimary")
        self.check_btn.clicked.connect(self._check)
        self.next_btn = QPushButton("New question ↻")
        self.next_btn.setObjectName("btnAction")
        self.next_btn.clicked.connect(self.generate)
        btn_row.addWidget(self.check_btn)
        btn_row.addWidget(self.next_btn)
        btn_row_wrap = QWidget()
        btn_row_wrap.setLayout(btn_row)
        layout.addWidget(btn_row_wrap)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        layout.addWidget(self.feedback)

        self.generate()

    def generate(self):
        a = 10 + random.randint(0, 2) * 20
        b = random.randint(0, 254)
        c = random.randint(0, 254)
        cidr = random.choice([24, 25, 26, 27, 28, 29])
        host_bits = 32 - cidr
        block_size = 2 ** host_bits
        base_int = ip_to_int(f"{a}.{b}.{c}.0")
        network = base_int - (base_int % block_size)
        broadcast = network + block_size - 1
        self.answer = {
            "mask": int_to_ip(mask_from_cidr(cidr)),
            "network": int_to_ip(network),
            "broadcast": int_to_ip(broadcast),
            "first": int_to_ip(network + 1),
            "last": int_to_ip(broadcast - 1),
            "hosts": str(max(block_size - 2, 0)),
        }
        self.given_label.setText(f"{int_to_ip(network + block_size // 3)}/{cidr}")
        self.feedback.setText("")
        for edit in self.inputs.values():
            edit.setText("")
            edit.setProperty("correct", False)
            edit.setProperty("wrong", False)
            edit.style().unpolish(edit)
            edit.style().polish(edit)

    def _check(self):
        all_correct = True
        wrong = []
        for key, label in self.FIELD_DEFS:
            edit = self.inputs[key]
            ok = edit.text().strip() == self.answer[key]
            edit.setProperty("correct", ok)
            edit.setProperty("wrong", not ok)
            edit.style().unpolish(edit)
            edit.style().polish(edit)
            if not ok:
                all_correct = False
                wrong.append(f"{label}: {self.answer[key]}")
        self.record_result(self.topic["id"], all_correct)
        if all_correct:
            self.feedback.setText("All fields correct.")
        else:
            self.feedback.setText("Some fields need another look.")
            self.show_modal("The correct values are:\n" + "\n".join(wrong))


class MatchEngine(QWidget):
    """Dropdown-based matching: pick the right definition/value for each term."""

    def __init__(self, topic, record_result, show_modal, parent=None):
        super().__init__(parent)
        self.topic = topic
        self.record_result = record_result
        self.show_modal = show_modal

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_layout = QVBoxLayout()
        list_wrap = QWidget()
        list_wrap.setLayout(self.list_layout)
        layout.addWidget(list_wrap)

        btn_row = QHBoxLayout()
        self.check_btn = QPushButton("Check answers")
        self.check_btn.setObjectName("btnPrimary")
        self.check_btn.clicked.connect(self._check)
        self.next_btn = QPushButton("New round ↻")
        self.next_btn.setObjectName("btnAction")
        self.next_btn.clicked.connect(self._new_round)
        btn_row.addWidget(self.check_btn)
        btn_row.addWidget(self.next_btn)
        btn_row_wrap = QWidget()
        btn_row_wrap.setLayout(btn_row)
        layout.addWidget(btn_row_wrap)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        layout.addWidget(self.feedback)

        self._new_round()

    def _new_round(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        pairs = list(self.topic["pairs"])
        random.shuffle(pairs)
        self.round = pairs[: min(8, len(pairs))]
        defs = [p[1] for p in self.round]
        random.shuffle(defs)

        self.combos = []
        for term, correct_def in self.round:
            row = QHBoxLayout()
            term_lbl = QLabel(term)
            term_lbl.setObjectName("matchTerm")
            term_lbl.setFixedWidth(160)
            combo = QComboBox()
            combo.addItem("select…", None)
            for d in defs:
                combo.addItem(d, d)
            row.addWidget(term_lbl)
            row.addWidget(combo, 1)
            row_wrap = QFrame()
            row_wrap.setObjectName("matchRow")
            row_wrap.setLayout(row)
            self.list_layout.addWidget(row_wrap)
            self.combos.append((row_wrap, combo, correct_def))
        self.feedback.setText("")

    def _check(self):
        all_correct = True
        wrong = []
        for row_wrap, combo, correct_def in self.combos:
            ok = combo.currentData() == correct_def
            row_wrap.setProperty("correct", ok)
            row_wrap.setProperty("wrong", not ok)
            row_wrap.style().unpolish(row_wrap)
            row_wrap.style().polish(row_wrap)
            if not ok:
                all_correct = False
                term = self.round[self.combos.index((row_wrap, combo, correct_def))][0]
                wrong.append(f"{term} → {correct_def}")
        self.record_result(self.topic["id"], all_correct)
        if all_correct:
            self.feedback.setText("All matches correct.")
        else:
            msg = "Correct pairs:\n" + "\n".join(wrong)
            if self.topic.get("explain"):
                msg += "\n\n" + self.topic["explain"]
            self.feedback.setText("Some matches are off.")
            self.show_modal(msg)


class SequenceEngine(QWidget):
    """Dropdown-based ordering: assign a position number to each step."""

    def __init__(self, topic, record_result, show_modal, parent=None):
        super().__init__(parent)
        self.topic = topic
        self.record_result = record_result
        self.show_modal = show_modal

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.list_layout = QVBoxLayout()
        list_wrap = QWidget()
        list_wrap.setLayout(self.list_layout)
        layout.addWidget(list_wrap)

        btn_row = QHBoxLayout()
        self.check_btn = QPushButton("Check order")
        self.check_btn.setObjectName("btnPrimary")
        self.check_btn.clicked.connect(self._check)
        self.next_btn = QPushButton("Shuffle ↻")
        self.next_btn.setObjectName("btnAction")
        self.next_btn.clicked.connect(self._shuffle)
        btn_row.addWidget(self.check_btn)
        btn_row.addWidget(self.next_btn)
        btn_row_wrap = QWidget()
        btn_row_wrap.setLayout(btn_row)
        layout.addWidget(btn_row_wrap)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        layout.addWidget(self.feedback)

        self._shuffle()

    def _shuffle(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        order = list(enumerate(self.topic["steps"]))
        random.shuffle(order)
        self.rows = []
        for correct_pos, (orig_idx, text) in enumerate(order):
            row = QHBoxLayout()
            combo = QComboBox()
            combo.addItem("#", None)
            for i in range(len(self.topic["steps"])):
                combo.addItem(str(i + 1), i + 1)
            txt_lbl = QLabel(text)
            txt_lbl.setWordWrap(True)
            row.addWidget(combo)
            row.addWidget(txt_lbl, 1)
            row_wrap = QFrame()
            row_wrap.setObjectName("seqRow")
            row_wrap.setLayout(row)
            self.list_layout.addWidget(row_wrap)
            self.rows.append((row_wrap, combo, orig_idx + 1))
        self.feedback.setText("")

    def _check(self):
        all_correct = True
        for row_wrap, combo, correct_pos in self.rows:
            ok = combo.currentData() == correct_pos
            row_wrap.setProperty("correct", ok)
            row_wrap.setProperty("wrong", not ok)
            row_wrap.style().unpolish(row_wrap)
            row_wrap.style().polish(row_wrap)
            if not ok:
                all_correct = False
        self.record_result(self.topic["id"], all_correct)
        if all_correct:
            self.feedback.setText("Correct order.")
        else:
            correct_list = "\n".join(f"{i+1}. {s}" for i, s in enumerate(self.topic["steps"]))
            msg = "Correct order:\n" + correct_list
            if self.topic.get("explain"):
                msg += "\n\n" + self.topic["explain"]
            self.feedback.setText("Order is off.")
            self.show_modal(msg)


class ScenarioEngine(QWidget):
    """Multiple-choice scenario bank: pick a random question, grade on click."""

    def __init__(self, topic, record_result, show_modal, parent=None):
        super().__init__(parent)
        self.topic = topic
        self.record_result = record_result
        self.show_modal = show_modal

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.prompt = QLabel()
        self.prompt.setObjectName("prompt")
        self.prompt.setWordWrap(True)
        layout.addWidget(self.prompt)

        self.opts_layout = QVBoxLayout()
        opts_wrap = QWidget()
        opts_wrap.setLayout(self.opts_layout)
        layout.addWidget(opts_wrap)

        self.next_btn = QPushButton("New question ↻")
        self.next_btn.setObjectName("btnAction")
        self.next_btn.clicked.connect(self._new_question)
        layout.addWidget(self.next_btn)

        self.feedback = QLabel()
        self.feedback.setWordWrap(True)
        layout.addWidget(self.feedback)

        self._new_question()

    def _new_question(self):
        self.q = random.choice(self.topic["questions"])
        self.prompt.setText(self.q["q"])
        self.feedback.setText("")
        while self.opts_layout.count():
            item = self.opts_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.opt_buttons = []
        for idx, opt in enumerate(self.q["opts"]):
            btn = QPushButton(opt)
            btn.setObjectName("scenarioOpt")
            btn.clicked.connect(lambda _=False, idx=idx: self._answer(idx))
            self.opts_layout.addWidget(btn)
            self.opt_buttons.append(btn)

    def _answer(self, idx):
        correct = idx == self.q["answer"]
        for btn in self.opt_buttons:
            btn.setEnabled(False)
        btn = self.opt_buttons[idx]
        btn.setProperty("chosenRight" if correct else "chosenWrong", True)
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        self.record_result(self.topic["id"], correct)
        if correct:
            self.feedback.setText("Correct.")
        else:
            self.feedback.setText("Not quite — see explanation.")
            self.show_modal(f"Correct answer: {self.q['opts'][self.q['answer']]}\n\n{self.q['explain']}")


ENGINES = {
    "fill": FillEngine,
    "match": MatchEngine,
    "sequence": SequenceEngine,
    "scenario": ScenarioEngine,
}
