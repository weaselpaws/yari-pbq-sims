"""Reusable question-engine widgets: sequence, match, calc, classify.

Each engine widget exposes:
  - readyChanged(bool): emitted whenever the "can this be checked yet" state changes
  - is_correct() -> bool: grade the current answer
  - lock(): disable further interaction (called after checking)
"""
import random
import textwrap

from PySide6.QtCore import Signal


def _wrapped(text, width=44):
    """QPushButton doesn't auto-wrap; insert manual newlines for long labels."""
    return "\n".join(textwrap.wrap(text, width=width)) or text
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QSizePolicy,
)


class ChipButton(QPushButton):
    def __init__(self, text, object_name="chip"):
        super().__init__(text)
        self.setObjectName(object_name)
        from PySide6.QtCore import Qt
        self.setCursor(Qt.PointingHandCursor)


class FlowLayout(QHBoxLayout):
    """Simple wrapping row; for our short item counts a QGridLayout wrap is
    overkill, so we just let a QHBoxLayout wrap via a container widget grid."""


def _wrap_row():
    from PySide6.QtWidgets import QGridLayout
    container = QWidget()
    grid = QGridLayout(container)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(8)
    return container, grid


class SequenceEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, question, parent=None):
        super().__init__(parent)
        self.q = question
        self.picked = []  # list of item strings, in chosen order
        self.locked = False

        self.shuffled = list(question["items"])
        random.shuffle(self.shuffled)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.answer_box = QFrame()
        self.answer_box.setObjectName("seqAnswer")
        self.answer_layout = QHBoxLayout(self.answer_box)
        self.answer_layout.setContentsMargins(8, 8, 8, 8)
        self.answer_layout.addStretch(1)

        self.pool_box = QFrame()
        self.pool_box.setObjectName("seqPool")
        self.pool_layout = QHBoxLayout(self.pool_box)
        self.pool_layout.setContentsMargins(8, 8, 8, 8)
        self.pool_layout.addStretch(1)

        layout.addWidget(self.answer_box)
        layout.addWidget(self.pool_box)
        self._render()

    def _clear_layout(self, lay):
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render(self):
        self._clear_layout(self.pool_layout)
        self._clear_layout(self.answer_layout)

        for item in self.shuffled:
            if item in self.picked:
                continue
            btn = ChipButton(item)

            def make_pick(it=item):
                def _pick():
                    if self.locked:
                        return
                    self.picked.append(it)
                    self._render()
                    self.readyChanged.emit(len(self.picked) == len(self.q["items"]))
                return _pick

            btn.clicked.connect(make_pick())
            self.pool_layout.addWidget(btn)
        self.pool_layout.addStretch(1)

        for i, item in enumerate(self.picked):
            btn = ChipButton(f"{i+1}.  {item}", object_name="chipPlaced")

            def make_unpick(idx=i):
                def _unpick():
                    if self.locked:
                        return
                    self.picked.pop(idx)
                    self._render()
                    self.readyChanged.emit(len(self.picked) == len(self.q["items"]))
                return _unpick

            btn.clicked.connect(make_unpick())
            self.answer_layout.addWidget(btn)
        self.answer_layout.addStretch(1)

    def is_correct(self):
        return self.picked == self.q["answer"]

    def lock(self):
        self.locked = True
        correct_order = self.q["answer"]
        self._clear_layout(self.answer_layout)
        for i, item in enumerate(self.picked):
            ok = i < len(correct_order) and item == correct_order[i]
            lbl = QLabel(f"{i+1}.  {item}")
            lbl.setObjectName("chipCorrect" if ok else "chipWrong")
            self.answer_layout.addWidget(lbl)
        self.answer_layout.addStretch(1)
        self.pool_box.hide()


class MatchEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, question, parent=None):
        super().__init__(parent)
        self.q = question
        self.locked_pairs = {}  # left index -> right index
        self.left_sel = None

        self.right_order = list(range(len(question["right"])))
        random.shuffle(self.right_order)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.left_col = QVBoxLayout()
        self.right_col = QVBoxLayout()
        left_wrap = QWidget()
        left_wrap.setLayout(self.left_col)
        right_wrap = QWidget()
        right_wrap.setLayout(self.right_col)

        left_label = QLabel("TERM")
        left_label.setObjectName("colLabel")
        right_label = QLabel("DEFINITION")
        right_label.setObjectName("colLabel")

        left_outer = QVBoxLayout()
        left_outer.addWidget(left_label)
        left_outer.addWidget(left_wrap)
        right_outer = QVBoxLayout()
        right_outer.addWidget(right_label)
        right_outer.addWidget(right_wrap)

        left_container = QWidget()
        left_container.setLayout(left_outer)
        right_container = QWidget()
        right_container.setLayout(right_outer)

        layout.addWidget(left_container, 1)
        layout.addWidget(right_container, 1)

        self.left_buttons = []
        for li, label in enumerate(question["left"]):
            btn = QPushButton(label)
            btn.setObjectName("matchItem")
            btn.clicked.connect(lambda _=False, li=li: self._pick_left(li))
            self.left_col.addWidget(btn)
            self.left_buttons.append(btn)

        self.right_buttons = {}
        for ri in self.right_order:
            btn = QPushButton(_wrapped(question["right"][ri]))
            btn.setObjectName("matchItem")
            btn.clicked.connect(lambda _=False, ri=ri: self._pick_right(ri))
            self.right_col.addWidget(btn)
            self.right_buttons[ri] = btn

    def _pick_left(self, li):
        if self.left_sel is not None and self.left_sel in self.locked_pairs:
            pass
        if li in self.locked_pairs:
            return
        self.left_sel = li
        for i, btn in enumerate(self.left_buttons):
            if i in self.locked_pairs:
                continue
            btn.setProperty("selected", i == li)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _pick_right(self, ri):
        if self.left_sel is None:
            return
        li = self.left_sel
        if li in self.locked_pairs:
            return
        if self.q["pairs"].get(li) == ri:
            self.locked_pairs[li] = ri
            self.left_buttons[li].setProperty("locked", True)
            self.left_buttons[li].setProperty("selected", False)
            self.left_buttons[li].style().unpolish(self.left_buttons[li])
            self.left_buttons[li].style().polish(self.left_buttons[li])
            self.right_buttons[ri].setProperty("locked", True)
            self.right_buttons[ri].style().unpolish(self.right_buttons[ri])
            self.right_buttons[ri].style().polish(self.right_buttons[ri])
            self.left_sel = None
            self.readyChanged.emit(len(self.locked_pairs) == len(self.q["left"]))
        else:
            btn = self.right_buttons[ri]
            btn.setProperty("wrongFlash", True)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

            from PySide6.QtCore import QTimer

            def clear_flash():
                btn.setProperty("wrongFlash", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

            QTimer.singleShot(350, clear_flash)

    def is_correct(self):
        # Completion requires every pair locked correctly by construction.
        return len(self.locked_pairs) == len(self.q["left"])

    def lock(self):
        for btn in self.left_buttons:
            btn.setEnabled(False)
        for btn in self.right_buttons.values():
            btn.setEnabled(False)


class CalcEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, question, parent=None):
        super().__init__(parent)
        self.q = question
        self.inputs = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        table = QGridLayout()
        for row, (label, value) in enumerate(question["table"]):
            l1 = QLabel(label)
            l1.setObjectName("calcLabel")
            l2 = QLabel(value)
            l2.setObjectName("calcValue")
            table.addWidget(l1, row, 0)
            table.addWidget(l2, row, 1)
        table_wrap = QWidget()
        table_wrap.setLayout(table)
        layout.addWidget(table_wrap)

        for field in question["fields"]:
            row = QHBoxLayout()
            lbl = QLabel(field["label"])
            lbl.setObjectName("calcFieldLabel")
            edit = QLineEdit()
            edit.setPlaceholderText("0")
            edit.setFixedWidth(110)
            edit.textChanged.connect(self._check_filled)
            row.addWidget(lbl)
            row.addStretch(1)
            row.addWidget(edit)
            row_wrap = QWidget()
            row_wrap.setLayout(row)
            layout.addWidget(row_wrap)
            self.inputs[field["id"]] = edit

    def _check_filled(self):
        filled = all(e.text().strip() != "" for e in self.inputs.values())
        self.readyChanged.emit(filled)

    def is_correct(self):
        try:
            for field in self.q["fields"]:
                val = float(self.inputs[field["id"]].text())
                if abs(val - field["answer"]) > field.get("tolerance", 0):
                    return False
            return True
        except ValueError:
            return False

    def lock(self):
        for edit in self.inputs.values():
            edit.setEnabled(False)
        for field in self.q["fields"]:
            edit = self.inputs[field["id"]]
            try:
                val = float(edit.text())
                ok = abs(val - field["answer"]) <= field.get("tolerance", 0)
            except ValueError:
                ok = False
            edit.setProperty("correct", ok)
            edit.setProperty("wrong", not ok)
            edit.style().unpolish(edit)
            edit.style().polish(edit)


class ClassifyEngine(QWidget):
    readyChanged = Signal(bool)

    def __init__(self, question, parent=None):
        super().__init__(parent)
        self.q = question
        self.picked = None
        self.assign = {}  # item index -> bucket index

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.pool_layout = QHBoxLayout()
        pool_wrap = QWidget()
        pool_wrap.setLayout(self.pool_layout)
        layout.addWidget(pool_wrap)

        self.buckets_layout = QGridLayout()
        buckets_wrap = QWidget()
        buckets_wrap.setLayout(self.buckets_layout)
        layout.addWidget(buckets_wrap)

        self.bucket_frames = []
        cols = 2
        for bi, label in enumerate(question["buckets"]):
            frame = QFrame()
            frame.setObjectName("bucket")
            v = QVBoxLayout(frame)
            title = QLabel(label.upper())
            title.setObjectName("bucketLabel")
            v.addWidget(title)
            frame.mousePressEvent = lambda e, bi=bi: self._drop(bi)
            self.buckets_layout.addWidget(frame, bi // cols, bi % cols)
            self.bucket_frames.append((frame, v))

        self._render()

    def _clear(self, lay):
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _render(self):
        self._clear(self.pool_layout)
        for ii, item in enumerate(self.q["items"]):
            if ii in self.assign:
                continue
            btn = QPushButton(_wrapped(item["text"]))
            btn.setObjectName("chipActive" if self.picked == ii else "chip")
            btn.clicked.connect(lambda _=False, ii=ii: self._pick(ii))
            self.pool_layout.addWidget(btn)
        self.pool_layout.addStretch(1)

        for bi, (frame, v) in enumerate(self.bucket_frames):
            while v.count() > 1:
                item = v.takeAt(1)
                w = item.widget()
                if w:
                    w.deleteLater()
            for ii, item in enumerate(self.q["items"]):
                if self.assign.get(ii) == bi:
                    btn = QPushButton(_wrapped(item["text"]))
                    btn.setObjectName("chipPlaced")
                    btn.clicked.connect(lambda _=False, ii=ii: self._remove(ii))
                    v.addWidget(btn)

    def _pick(self, ii):
        self.picked = ii
        self._render()

    def _drop(self, bi):
        if self.picked is None:
            return
        self.assign[self.picked] = bi
        self.picked = None
        self._render()
        self.readyChanged.emit(len(self.assign) == len(self.q["items"]))

    def _remove(self, ii):
        del self.assign[ii]
        self._render()
        self.readyChanged.emit(len(self.assign) == len(self.q["items"]))

    def is_correct(self):
        return all(self.assign.get(ii) == item["bucket"] for ii, item in enumerate(self.q["items"]))

    def lock(self):
        for frame, _ in self.bucket_frames:
            frame.mousePressEvent = lambda e: None


ENGINES = {
    "sequence": SequenceEngine,
    "match": MatchEngine,
    "calc": CalcEngine,
    "classify": ClassifyEngine,
}
