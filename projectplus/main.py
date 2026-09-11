"""YARI Project+ PBQ Simulator — PySide6 desktop port.

Ported from legacy-html/YARI_ProjectPlus_PBQ_Simulator.html.
"""
import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QProgressBar,
)

from data import QUESTIONS
from engines import ENGINES

APP_TITLE = "Project+ PBQ Simulator"
STORAGE_PATH = Path.home() / ".yari_pbq" / "projectplus.json"

STYLE = """
QWidget { background-color: #0B2545; color: #F4F1E8; font-family: 'Segoe UI', sans-serif; font-size: 14px; }
#header { border-bottom: 1px solid #1E4976; }
#brandInst { color: #B9C6D6; font-size: 11px; }
#brandTitle { font-size: 20px; font-weight: 600; }
#progressLabel { color: #E8A33D; font-family: Consolas, monospace; font-size: 12px; }
QProgressBar { border: none; background: #1E4976; border-radius: 2px; max-height: 4px; }
QProgressBar::chunk { background-color: #E8A33D; border-radius: 2px; }
#card { background: #12345C; border: 1px solid #1E4976; border-radius: 6px; padding: 10px; }
#engineTag { color: #E8A33D; border: 1px solid #B87F2A; border-radius: 3px; padding: 3px 8px; font-family: Consolas, monospace; font-size: 11px; }
#prompt { font-size: 16px; }
#sub { color: #B9C6D6; font-size: 12.5px; }
#feedbackCorrect { background: #173A2E; color: #6FA98A; border: 1px solid #6FA98A; border-radius: 4px; padding: 8px; }
#feedbackIncorrect { background: #3A1F1A; color: #E76F51; border: 1px solid #E76F51; border-radius: 4px; padding: 8px; }
QPushButton { font-weight: 600; padding: 9px 16px; border-radius: 5px; border: 1px solid transparent; }
#btnPrimary { background: #E8A33D; color: #0B2545; }
#btnPrimary:disabled { background: #1E4976; color: #B9C6D6; }
#btnGhost { background: transparent; color: #B9C6D6; border: 1px solid #1E4976; }
#seqAnswer, #seqPool { background: #163C68; border: 1px solid #1E4976; border-radius: 5px; }
#seqPool { background: transparent; border-style: dashed; }
#chip, #chipPlaced, #chipActive { background: #163C68; border: 1px solid #1E4976; border-radius: 4px; padding: 8px 12px; }
#chipPlaced { background: #0B2545; border-color: #B87F2A; }
#chipActive { border-color: #E8A33D; }
#chipCorrect { color: #6FA98A; padding: 8px 12px; }
#chipWrong { color: #E76F51; padding: 8px 12px; }
#colLabel { color: #B9C6D6; font-size: 11px; }
QPushButton#matchItem { background: #163C68; border: 1px solid #1E4976; border-radius: 4px; padding: 10px; text-align: left; }
QPushButton#matchItem[selected="true"] { border-color: #E8A33D; background: #1B4470; }
QPushButton#matchItem[locked="true"] { border-color: #6FA98A; background: #173A2E; color: #B9C6D6; }
QPushButton#matchItem[wrongFlash="true"] { border-color: #E76F51; }
#calcLabel { color: #B9C6D6; }
#calcValue { color: #E8A33D; font-family: Consolas, monospace; }
#calcFieldLabel { color: #B9C6D6; }
QLineEdit { background: #0B2545; border: 1px solid #1E4976; border-radius: 4px; padding: 6px; color: #F4F1E8; font-family: Consolas, monospace; }
QLineEdit[correct="true"] { border-color: #6FA98A; }
QLineEdit[wrong="true"] { border-color: #E76F51; }
#bucket { border: 1px dashed #1E4976; border-radius: 5px; padding: 6px; }
#bucketLabel { color: #B9C6D6; font-size: 11px; }
#scoreBig { font-size: 40px; color: #E8A33D; font-family: Consolas, monospace; }
#breakdownRow { border-bottom: 1px solid #1E4976; padding-bottom: 4px; }
"""


def load_progress():
    try:
        data = json.loads(STORAGE_PATH.read_text())
        if isinstance(data.get("index"), int) and data["index"] < len(QUESTIONS):
            return data
    except Exception:
        pass
    return {"index": 0, "score": 0, "results": []}


def save_progress(state):
    try:
        STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORAGE_PATH.write_text(json.dumps(state))
    except Exception:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"YARI {APP_TITLE}")
        self.resize(720, 780)

        state = load_progress()
        self.index = state["index"]
        self.score = state["score"]
        self.results = state["results"]
        self.engine_widget = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(24, 20, 24, 20)

        header = QWidget()
        header.setObjectName("header")
        hlayout = QHBoxLayout(header)
        brand_col = QVBoxLayout()
        inst = QLabel("YELLOWHAMMER APPLIED RESEARCH INSTITUTE")
        inst.setObjectName("brandInst")
        title = QLabel(APP_TITLE)
        title.setObjectName("brandTitle")
        brand_col.addWidget(inst)
        brand_col.addWidget(title)
        brand_wrap = QWidget()
        brand_wrap.setLayout(brand_col)
        hlayout.addWidget(brand_wrap)
        hlayout.addStretch(1)
        self.progress_label = QLabel()
        self.progress_label.setObjectName("progressLabel")
        hlayout.addWidget(self.progress_label, alignment=Qt.AlignBottom)
        root.addWidget(header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximum(len(QUESTIONS))
        root.addWidget(self.progress_bar)
        root.addSpacing(10)

        self.stage = QVBoxLayout()
        stage_wrap = QWidget()
        stage_wrap.setLayout(self.stage)
        root.addWidget(stage_wrap)
        root.addStretch(1)

        self.render()

    def clear_stage(self):
        while self.stage.count():
            item = self.stage.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def update_progress(self):
        shown = min(self.index + 1, len(QUESTIONS))
        self.progress_label.setText(f"Q{shown} / {len(QUESTIONS)}")
        self.progress_bar.setValue(min(self.index, len(QUESTIONS)))

    def render(self):
        self.update_progress()
        self.clear_stage()
        if self.index >= len(QUESTIONS):
            self.render_results()
            return
        q = QUESTIONS[self.index]

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)

        tag = QLabel(q["tag"])
        tag.setObjectName("engineTag")
        tag.setFixedWidth(tag.sizeHint().width() + 4)
        card_layout.addWidget(tag, alignment=Qt.AlignLeft)

        prompt = QLabel(q["prompt"])
        prompt.setObjectName("prompt")
        prompt.setWordWrap(True)
        card_layout.addWidget(prompt)

        if q.get("sub"):
            sub = QLabel(q["sub"])
            sub.setObjectName("sub")
            sub.setWordWrap(True)
            card_layout.addWidget(sub)

        engine_cls = ENGINES[q["engine"]]
        self.engine_widget = engine_cls(q)
        card_layout.addWidget(self.engine_widget)

        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        self.feedback_label.hide()
        card_layout.addWidget(self.feedback_label)

        controls = QHBoxLayout()
        self.skip_btn = QPushButton("Skip")
        self.skip_btn.setObjectName("btnGhost")
        self.skip_btn.clicked.connect(lambda: self.finish_question(False, q, skipped=True))
        self.check_btn = QPushButton("Check answer")
        self.check_btn.setObjectName("btnPrimary")
        self.check_btn.setEnabled(False)
        self.check_btn.clicked.connect(lambda: self.finish_question(self.engine_widget.is_correct(), q))
        controls.addWidget(self.skip_btn)
        controls.addStretch(1)
        controls.addWidget(self.check_btn)
        card_layout.addLayout(controls)
        self.controls_layout = controls

        self.engine_widget.readyChanged.connect(self.check_btn.setEnabled)

        self.stage.addWidget(card)
        self.current_card = card

    def finish_question(self, correct, q, skipped=False):
        self.engine_widget.lock()
        self.check_btn.setEnabled(False)
        self.check_btn.hide()
        self.skip_btn.hide()

        self.feedback_label.show()
        if skipped:
            self.feedback_label.setText("Skipped. Moving to the next question.")
            self.feedback_label.setObjectName("feedbackIncorrect")
        elif correct:
            self.score += 1
            self.feedback_label.setText("Correct.")
            self.feedback_label.setObjectName("feedbackCorrect")
        else:
            self.feedback_label.setText("Not quite — review this topic before moving on.")
            self.feedback_label.setObjectName("feedbackIncorrect")
        self.feedback_label.style().unpolish(self.feedback_label)
        self.feedback_label.style().polish(self.feedback_label)

        self.results.append({"tag": q["tag"], "correct": bool(correct) and not skipped})

        next_btn = QPushButton("See results" if self.index == len(QUESTIONS) - 1 else "Next question")
        next_btn.setObjectName("btnPrimary")

        def go_next():
            self.index += 1
            save_progress({"index": self.index, "score": self.score, "results": self.results})
            self.render()

        next_btn.clicked.connect(go_next)
        self.controls_layout.addWidget(next_btn)

    def render_results(self):
        total = len(QUESTIONS)
        pct = round((self.score / total) * 100) if total else 0
        by_tag = {}
        for r in self.results:
            d = by_tag.setdefault(r["tag"], {"correct": 0, "total": 0})
            d["total"] += 1
            if r["correct"]:
                d["correct"] += 1

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        tag = QLabel("RESULTS")
        tag.setObjectName("engineTag")
        tag.setFixedWidth(tag.sizeHint().width() + 4)
        layout.addWidget(tag, alignment=Qt.AlignLeft)

        h2 = QLabel("Practice set complete")
        h2.setObjectName("brandTitle")
        layout.addWidget(h2)

        score_big = QLabel(f"{self.score}/{total}")
        score_big.setObjectName("scoreBig")
        layout.addWidget(score_big)

        pct_label = QLabel(f"{pct}% correct")
        pct_label.setObjectName("sub")
        layout.addWidget(pct_label)

        for tag_name, d in by_tag.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(tag_name))
            row.addStretch(1)
            row.addWidget(QLabel(f"{d['correct']} / {d['total']}"))
            row_wrap = QFrame()
            row_wrap.setObjectName("breakdownRow")
            row_wrap.setLayout(row)
            layout.addWidget(row_wrap)

        restart_btn = QPushButton("Restart")
        restart_btn.setObjectName("btnGhost")

        def restart():
            self.index = 0
            self.score = 0
            self.results = []
            save_progress({"index": 0, "score": 0, "results": []})
            self.render()

        restart_btn.clicked.connect(restart)

        btn_row = QHBoxLayout()
        btn_row.addWidget(restart_btn)

        flagged = [i for i, r in enumerate(self.results) if not r["correct"]]
        if flagged:
            review_btn = QPushButton(f"Review flagged questions ({len(flagged)})")
            review_btn.setObjectName("btnGhost")
            review_btn.clicked.connect(lambda: self._start_review(flagged))
            btn_row.addWidget(review_btn)
        btn_row.addStretch(1)
        btn_row_wrap = QWidget()
        btn_row_wrap.setLayout(btn_row)
        layout.addWidget(btn_row_wrap)

        self.stage.addWidget(card)
        self.current_card = card

    def _start_review(self, flagged):
        self.review_flagged = flagged
        self.review_pos = 0
        self.render_review()

    def render_review(self):
        self.clear_stage()
        qi = self.review_flagged[self.review_pos]
        q = QUESTIONS[qi]

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        tag = QLabel(f"REVIEWING {self.review_pos + 1} OF {len(self.review_flagged)} — Q{qi + 1}: {q['tag']}")
        tag.setObjectName("engineTag")
        layout.addWidget(tag, alignment=Qt.AlignLeft)

        prompt = QLabel(q["prompt"])
        prompt.setObjectName("prompt")
        prompt.setWordWrap(True)
        layout.addWidget(prompt)

        feedback = QLabel("Not answered correctly — revisit this topic before your next attempt.")
        feedback.setObjectName("feedbackIncorrect")
        feedback.setWordWrap(True)
        layout.addWidget(feedback)

        nav_row = QHBoxLayout()
        prev_btn = QPushButton("← Previous flagged")
        prev_btn.setObjectName("btnGhost")
        prev_btn.setEnabled(self.review_pos > 0)
        prev_btn.clicked.connect(self._review_prev)
        nav_row.addWidget(prev_btn)
        nav_row.addStretch(1)
        back_btn = QPushButton("Back to results")
        back_btn.setObjectName("btnGhost")
        back_btn.clicked.connect(self.render_results)
        nav_row.addWidget(back_btn)
        next_btn = QPushButton("Next flagged →")
        next_btn.setObjectName("btnPrimary")
        next_btn.setEnabled(self.review_pos < len(self.review_flagged) - 1)
        next_btn.clicked.connect(self._review_next)
        nav_row.addWidget(next_btn)
        layout.addLayout(nav_row)

        self.stage.addWidget(card)
        self.current_card = card

    def _review_prev(self):
        self.review_pos -= 1
        self.render_review()

    def _review_next(self):
        self.review_pos += 1
        self.render_review()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
