"""Question-engine widgets for the Network+ simulator.

sequencing / matching / calculation / classification port the original
HTML engines. topology and terminal are new simulation types.

Common interface:
  - readyChanged(bool): can the current answer be submitted yet
  - is_correct() -> bool
  - lock(): disable further interaction, called after submission
"""
import random
import textwrap

from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem, QPlainTextEdit,
)


def _wrapped(text, width=48):
    return "\n".join(textwrap.wrap(text, width=width)) or text


class SequencingEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, q, parent=None):
        super().__init__(parent)
        self.q = q
        self.order = []  # chosen item indices, in order
        self.pool_order = list(range(len(q["items"])))
        random.shuffle(self.pool_order)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pool_layout = QHBoxLayout()
        pool_wrap = QFrame()
        pool_wrap.setObjectName("seqPool")
        pool_wrap.setLayout(self.pool_layout)
        layout.addWidget(pool_wrap)

        self.slots_layout = QVBoxLayout()
        slots_wrap = QWidget()
        slots_wrap.setLayout(self.slots_layout)
        layout.addWidget(slots_wrap)

        self._build_pool()
        self._build_slots()

    def _clear(self, lay):
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _build_pool(self):
        self._clear(self.pool_layout)
        for idx in self.pool_order:
            if idx in self.order:
                continue
            btn = QPushButton(_wrapped(self.q["items"][idx], 30))
            btn.setObjectName("seqChip")
            btn.clicked.connect(lambda _=False, idx=idx: self._pick(idx))
            self.pool_layout.addWidget(btn)
        self.pool_layout.addStretch(1)

    def _build_slots(self):
        self._clear(self.slots_layout)
        for i in range(len(self.q["items"])):
            if i < len(self.order):
                btn = QPushButton(f"{i+1}.  {self.q['items'][self.order[i]]}")
                btn.setObjectName("seqSlot")
                btn.setToolTip("Click to remove")
                btn.clicked.connect(lambda _=False, i=i: self._unpick(i))
            else:
                btn = QPushButton(f"{i+1}.  —")
                btn.setObjectName("seqSlot")
                btn.setEnabled(False)
            self.slots_layout.addWidget(btn)

    def _pick(self, idx):
        self.order.append(idx)
        self._build_pool()
        self._build_slots()
        self.readyChanged.emit(len(self.order) == len(self.q["items"]))

    def _unpick(self, position):
        self.order.pop(position)
        self._build_pool()
        self._build_slots()
        self.readyChanged.emit(len(self.order) == len(self.q["items"]))

    def is_correct(self):
        return self.order == self.q["correct_order"]

    def lock(self):
        self._clear(self.slots_layout)
        correct = self.q["correct_order"]
        for i in range(len(self.q["items"])):
            row = QHBoxLayout()
            num = QLabel(f"{i+1}.")
            num.setObjectName("seqNum")
            row.addWidget(num)
            filled = self.order[i] if i < len(self.order) else None
            text = QLabel(self.q["items"][filled] if filled is not None else "—")
            text.setWordWrap(True)
            row.addWidget(text, 1)
            row_wrap = QFrame()
            ok = filled == correct[i] if i < len(correct) else False
            row_wrap.setObjectName("seqSlotCorrect" if ok else "seqSlotWrong")
            row_wrap.setLayout(row)
            self.slots_layout.addWidget(row_wrap)


class MatchingEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, q, parent=None):
        super().__init__(parent)
        self.q = q
        self.pairing = {}  # term index -> answer index
        self.active_term = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.terms_layout = QVBoxLayout()
        self.answers_layout = QVBoxLayout()
        terms_wrap = QWidget()
        terms_wrap.setLayout(self.terms_layout)
        answers_wrap = QWidget()
        answers_wrap.setLayout(self.answers_layout)
        layout.addWidget(terms_wrap, 1)
        layout.addWidget(answers_wrap, 1)

        self.term_buttons = []
        for i, term in enumerate(q["terms"]):
            btn = QPushButton(term)
            btn.setObjectName("matchTerm")
            btn.clicked.connect(lambda _=False, i=i: self._pick_term(i))
            self.terms_layout.addWidget(btn)
            self.term_buttons.append(btn)

        self.answer_order = list(range(len(q["answers"])))
        random.shuffle(self.answer_order)
        self.answer_buttons = {}
        for ai in self.answer_order:
            btn = QPushButton(f"{chr(65+ai)}.  " + _wrapped(q["answers"][ai], 44))
            btn.setObjectName("opt")
            btn.clicked.connect(lambda _=False, ai=ai: self._pick_answer(ai))
            self.answers_layout.addWidget(btn)
            self.answer_buttons[ai] = btn

    def _refresh_term_style(self):
        for i, btn in enumerate(self.term_buttons):
            if i in self.pairing:
                continue
            btn.setProperty("selected", i == self.active_term)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _pick_term(self, i):
        if i in self.pairing:
            return
        self.active_term = i
        self._refresh_term_style()

    def _pick_answer(self, ai):
        if self.active_term is None:
            return
        ti = self.active_term
        if ti in self.pairing:
            return
        if self.q["correct_pairs"][ti] == ai:
            self.pairing[ti] = ai
            self.term_buttons[ti].setText(f"{self.q['terms'][ti]}   ✓ {chr(65+ai)}")
            self.term_buttons[ti].setProperty("locked", True)
            self.term_buttons[ti].style().unpolish(self.term_buttons[ti])
            self.term_buttons[ti].style().polish(self.term_buttons[ti])
            self.answer_buttons[ai].setProperty("locked", True)
            self.answer_buttons[ai].style().unpolish(self.answer_buttons[ai])
            self.answer_buttons[ai].style().polish(self.answer_buttons[ai])
            self.active_term = None
            self._refresh_term_style()
            self.readyChanged.emit(len(self.pairing) == len(self.q["terms"]))
        else:
            btn = self.answer_buttons[ai]
            btn.setProperty("wrongFlash", True)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

            def clear():
                btn.setProperty("wrongFlash", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

            QTimer.singleShot(350, clear)

    def is_correct(self):
        return len(self.pairing) == len(self.q["terms"])

    def lock(self):
        for btn in self.term_buttons:
            btn.setEnabled(False)
        for btn in self.answer_buttons.values():
            btn.setEnabled(False)


class CalculationEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, q, parent=None):
        super().__init__(parent)
        self.q = q
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        grid = QGridLayout()
        for row, (label, value) in enumerate(q["values"].items()):
            l1 = QLabel(label)
            l2 = QLabel(str(value))
            l2.setObjectName("calcValue")
            grid.addWidget(l1, row, 0)
            grid.addWidget(l2, row, 1)
        grid_wrap = QWidget()
        grid_wrap.setLayout(grid)
        layout.addWidget(grid_wrap)

        hint = QLabel("Formula: " + q["formula_hint"])
        hint.setObjectName("hint")
        layout.addWidget(hint)

        row = QHBoxLayout()
        row.addWidget(QLabel("Answer ="))
        self.input = QLineEdit()
        self.input.setPlaceholderText("0")
        self.input.setFixedWidth(130)
        self.input.textChanged.connect(lambda t: self.readyChanged.emit(t.strip() != ""))
        row.addWidget(self.input)
        row.addStretch(1)
        row_wrap = QWidget()
        row_wrap.setLayout(row)
        layout.addWidget(row_wrap)

    def is_correct(self):
        try:
            return abs(float(self.input.text()) - self.q["correct_answer"]) < 0.01
        except ValueError:
            return False

    def lock(self):
        self.input.setEnabled(False)
        ok = self.is_correct()
        self.input.setProperty("correct", ok)
        self.input.setProperty("wrong", not ok)
        self.input.style().unpolish(self.input)
        self.input.style().polish(self.input)


class ClassificationEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, q, parent=None):
        super().__init__(parent)
        self.q = q
        self.chosen = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = []
        for i, opt in enumerate(q["options"]):
            btn = QPushButton(f"{chr(65+i)}.  {opt}")
            btn.setObjectName("opt")
            btn.clicked.connect(lambda _=False, i=i: self._pick(i))
            layout.addWidget(btn)
            self.buttons.append(btn)

    def _pick(self, i):
        self.chosen = i
        for j, btn in enumerate(self.buttons):
            btn.setProperty("selected", j == i)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self.readyChanged.emit(True)

    def is_correct(self):
        return self.chosen == self.q["correct_index"]

    def lock(self):
        for j, btn in enumerate(self.buttons):
            btn.setEnabled(False)
            if j == self.q["correct_index"]:
                btn.setProperty("correct", True)
            elif j == self.chosen:
                btn.setProperty("wrong", True)
            btn.style().unpolish(btn)
            btn.style().polish(btn)


class TopologyEngine(QWidget):
    """Click one device, then another, to wire a connection between them."""

    readyChanged = Signal(bool)

    def __init__(self, q, parent=None):
        super().__init__(parent)
        self.q = q
        self.links = set()  # frozenset({deviceA, deviceB})
        self.selected = None
        self.node_items = {}
        self.line_items = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        hint = QLabel("Click a device, then click the device you want to wire it to. Click the same pair again to remove that link.")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints())
        self.view.setFixedHeight(220)
        self.view.setStyleSheet("background: #141618; border: 1px solid #3E4245; border-radius: 6px;")
        layout.addWidget(self.view)

        clear_btn = QPushButton("Clear all links")
        clear_btn.setObjectName("linkClear")
        clear_btn.clicked.connect(self._clear_links)
        layout.addWidget(clear_btn, alignment=Qt.AlignLeft)

        self._layout_devices()

    def _layout_devices(self):
        n = len(self.q["devices"])
        spacing = 140
        for i, name in enumerate(self.q["devices"]):
            x = 20 + (i // 2) * spacing
            y = 20 if i % 2 == 0 else 130
            rect = QGraphicsRectItem(0, 0, 110, 44)
            rect.setPos(x, y)
            rect.setBrush(QColor("#2A2D30"))
            rect.setPen(QPen(QColor("#3E7CB1"), 1.5))
            rect.setFlag(rect.GraphicsItemFlag.ItemIsSelectable, False)
            self.scene.addItem(rect)
            text = QGraphicsTextItem(name)
            text.setDefaultTextColor(QColor("#E8E9EA"))
            text.setPos(x + 6, y + 12)
            self.scene.addItem(text)
            self.node_items[name] = rect

        cols = (n + 1) // 2
        self.scene.setSceneRect(0, 0, max(20 + cols * spacing, 400), 200)
        self.view.mousePressEvent = self._on_scene_click

    def _center(self, name):
        rect = self.node_items[name]
        r = rect.rect()
        p = rect.pos()
        return p.x() + r.width() / 2, p.y() + r.height() / 2

    def _on_scene_click(self, event):
        pos = self.view.mapToScene(event.pos())
        clicked = None
        for name, rect in self.node_items.items():
            if rect.sceneBoundingRect().contains(pos):
                clicked = name
                break
        if clicked is None:
            return
        if self.selected is None:
            self.selected = clicked
            self.node_items[clicked].setPen(QPen(QColor("#D97D3D"), 2.5))
        elif clicked == self.selected:
            self.node_items[clicked].setPen(QPen(QColor("#3E7CB1"), 1.5))
            self.selected = None
        else:
            self._add_link(self.selected, clicked)
            self.node_items[self.selected].setPen(QPen(QColor("#3E7CB1"), 1.5))
            self.selected = None

    def _add_link(self, a, b):
        key = frozenset((a, b))
        if key in self.links:
            self._remove_link(key)
            return
        self.links.add(key)
        x1, y1 = self._center(a)
        x2, y2 = self._center(b)
        line = QGraphicsLineItem(x1, y1, x2, y2)
        line.setPen(QPen(QColor("#5FA65F"), 2))
        self.scene.addItem(line)
        self.line_items[key] = line
        self.readyChanged.emit(len(self.links) > 0)

    def _remove_link(self, key):
        line = self.line_items.pop(key, None)
        if line is not None:
            self.scene.removeItem(line)
        self.links.discard(key)
        self.readyChanged.emit(len(self.links) > 0)

    def _clear_links(self):
        for line in self.line_items.values():
            self.scene.removeItem(line)
        self.line_items = {}
        self.links = set()
        self.readyChanged.emit(False)

    def is_correct(self):
        required = {frozenset(pair) for pair in self.q["required_links"]}
        return self.links == required

    def lock(self):
        self.view.setEnabled(False)
        required = {frozenset(pair) for pair in self.q["required_links"]}
        for key, line in self.line_items.items():
            ok = key in required
            line.setPen(QPen(QColor("#5FA65F") if ok else QColor("#C1524A"), 2))
        for pair in required:
            if pair not in self.line_items:
                a, b = tuple(pair)
                x1, y1 = self._center(a)
                x2, y2 = self._center(b)
                line = QGraphicsLineItem(x1, y1, x2, y2)
                pen = QPen(QColor("#C1524A"), 2, Qt.DashLine)
                line.setPen(pen)
                self.scene.addItem(line)


class TerminalEngine(QWidget):
    """Simulated command-line: type a diagnostic command, then answer a
    follow-up question about the (canned) output it produces."""

    readyChanged = Signal(bool)

    def __init__(self, q, parent=None):
        super().__init__(parent)
        self.q = q
        self.command_correct = False
        self.followup_shown = False
        self.followup_correct = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.term = QPlainTextEdit()
        self.term.setReadOnly(True)
        self.term.setObjectName("terminal")
        self.term.setFixedHeight(160)
        self.term.setPlainText(q["prompt"] + " ")
        layout.addWidget(self.term)

        cmd_row = QHBoxLayout()
        prompt_lbl = QLabel(q["prompt"])
        prompt_lbl.setObjectName("terminalPrompt")
        self.cmd_input = QLineEdit()
        self.cmd_input.setObjectName("terminalInput")
        self.cmd_input.setPlaceholderText("Type a command and press Enter")
        self.cmd_input.returnPressed.connect(self._run_command)
        cmd_row.addWidget(prompt_lbl)
        cmd_row.addWidget(self.cmd_input, 1)
        cmd_row_wrap = QWidget()
        cmd_row_wrap.setLayout(cmd_row)
        layout.addWidget(cmd_row_wrap)

        self.followup_wrap = QWidget()
        fu_layout = QVBoxLayout(self.followup_wrap)
        fu_layout.setContentsMargins(0, 8, 0, 0)
        fu_label = QLabel(q["followup_question"])
        fu_label.setWordWrap(True)
        fu_label.setObjectName("hint")
        self.fu_input = QLineEdit()
        self.fu_input.textChanged.connect(self._on_followup_changed)
        fu_layout.addWidget(fu_label)
        fu_layout.addWidget(self.fu_input)
        self.followup_wrap.hide()
        layout.addWidget(self.followup_wrap)

    def _run_command(self):
        typed = self.cmd_input.text().strip()
        self.term.appendPlainText(f"{self.q['prompt']} {typed}")
        normalized = typed.lower().rstrip()
        accepted = [c.lower() for c in self.q["accepted_commands"]]
        if normalized in accepted:
            self.command_correct = True
            self.term.appendPlainText(self.q["output"])
            self.cmd_input.setEnabled(False)
            self.followup_wrap.show()
        else:
            self.term.appendPlainText("'" + typed + "' is not recognized as an internal or external command.\n")
        self.cmd_input.clear()

    def _on_followup_changed(self, text):
        text = text.strip().lower()
        expected = self.q["followup_answer"].lower()
        accept_contains = [s.lower() for s in self.q.get("followup_accept_contains", [])]
        self.followup_correct = text == expected or any(s in text for s in accept_contains)
        self.readyChanged.emit(bool(text))

    def is_correct(self):
        return self.command_correct and self.followup_correct

    def lock(self):
        self.cmd_input.setEnabled(False)
        self.fu_input.setEnabled(False)
        self.fu_input.setProperty("correct", self.followup_correct)
        self.fu_input.setProperty("wrong", not self.followup_correct)
        self.fu_input.style().unpolish(self.fu_input)
        self.fu_input.style().polish(self.fu_input)


ENGINES = {
    "sequencing": SequencingEngine,
    "matching": MatchingEngine,
    "calculation": CalculationEngine,
    "classification": ClassificationEngine,
    "topology": TopologyEngine,
    "terminal": TerminalEngine,
}
