"""YARI Security+ PBQ Simulator — PySide6 desktop port.

Ported from legacy-html/YARI Security+ PBQ Simulator.html, plus three new
simulation types: a log/alert triage console, a firewall/ACL rule builder,
and a Linux terminal simulator.
"""
import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame,
)

from data import QUESTIONS
from engines import ENGINES

STORAGE_PATH = Path.home() / ".yari_pbq" / "secplus.json"

ENGINE_LABELS = {
    "sequencing": "Sequencing", "matching": "Matching", "calculation": "Calculation",
    "classification": "Classification", "log_triage": "Log Triage",
    "firewall": "Firewall/ACL Builder", "terminal": "Linux Terminal",
}

STYLE = """
QWidget { background-color: #E8DFC8; color: #24211C; font-family: Consolas, 'Courier New', monospace; font-size: 13px; }
#header { background: #DCD0AE; border: 1px solid #C9BB94; border-radius: 8px; }
#caseId { color: #5C5644; font-size: 11px; }
#title { font-size: 22px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
#sub { color: #5C5644; font-size: 12px; }
#scoreText { font-size: 14px; }
QPushButton#resetBtn { background: none; border: 1px solid #5C5644; color: #5C5644; border-radius: 4px; padding: 5px 10px; }
QPushButton#resetBtn:hover { border-color: #A32B2B; color: #A32B2B; }
#fileTrack QLabel { }
#card { background: #E8DFC8; border: 1px solid #C9BB94; border-radius: 8px; padding: 18px; }
#engLabel { color: #8C6D1F; font-size: 10px; }
#qTitle { font-family: 'Segoe UI', sans-serif; font-weight: 600; font-size: 16px; }
#scenario { color: #5C5644; font-size: 12.5px; background: #DCD0AE; border-left: 3px solid #8C6D1F; border-radius: 0 4px 4px 0; padding: 10px; }
#hint { color: #5C5644; font-size: 11.5px; }
#colLabel { color: #5C5644; font-size: 11px; }
#seqPool { background: #DCD0AE; border: 1px dashed #C9BB94; border-radius: 6px; padding: 8px; }
QPushButton#seqChip { background: #DCD0AE; border: 1px solid #C9BB94; color: #24211C; border-radius: 5px; padding: 8px 10px; }
#seqSlot, #seqSlotCorrect, #seqSlotWrong { background: #DCD0AE; border: 1px dashed #C9BB94; border-radius: 5px; padding: 8px; }
#seqSlotCorrect { border: 1px solid #4C7A52; background: #E4EDE3; }
#seqSlotWrong { border: 1px solid #A32B2B; background: #F1E1DC; }
#seqNum { color: #8C6D1F; font-weight: 600; }
QPushButton#matchTerm { background: #DCD0AE; border: 1px solid #C9BB94; border-radius: 5px; padding: 10px; text-align: left; }
QPushButton#matchTerm[selected="true"] { border-color: #8C6D1F; background: #EFE7CF; }
QPushButton#matchTerm[locked="true"] { border-color: #4C7A52; background: #E4EDE3; color: #5C5644; }
QPushButton#opt { width: 100%; text-align: left; background: #DCD0AE; border: 1px solid #C9BB94; color: #24211C; border-radius: 5px; padding: 11px 14px; }
QPushButton#opt:hover { border-color: #8C6D1F; }
QPushButton#opt[selected="true"] { border-color: #8C6D1F; background: #EFE7CF; }
QPushButton#opt[locked="true"] { border-color: #4C7A52; background: #E4EDE3; }
QPushButton#opt[wrongFlash="true"] { border-color: #A32B2B; }
QPushButton#opt[correct="true"] { border-color: #4C7A52; background: #E4EDE3; }
QPushButton#opt[wrong="true"] { border-color: #A32B2B; background: #F1E1DC; }
#calcValue { color: #8C6D1F; }
QLineEdit { background: #E8DFC8; border: 1px solid #C9BB94; border-radius: 5px; padding: 8px; color: #24211C; font-family: Consolas, monospace; }
QLineEdit[correct="true"] { border-color: #4C7A52; }
QLineEdit[wrong="true"] { border-color: #A32B2B; }
QCheckBox#logLine { padding: 4px; }
QCheckBox#logLine[correct="true"] { color: #4C7A52; }
QCheckBox#logLine[wrong="true"] { color: #A32B2B; }
QComboBox { background: #E8DFC8; border: 1px solid #C9BB94; border-radius: 5px; padding: 6px; }
#rulePool { background: #DCD0AE; border: 1px dashed #C9BB94; border-radius: 6px; padding: 8px; }
#ruleSet { background: #E8DFC8; border: 1px solid #C9BB94; border-radius: 6px; padding: 6px; min-height: 30px; }
QPushButton#ruleChip { background: #DCD0AE; border: 1px solid #C9BB94; border-radius: 5px; padding: 8px 10px; text-align: left; }
QPushButton#ruleChipPlaced { background: #E4EDE3; border: 1px solid #4C7A52; border-radius: 5px; padding: 8px 10px; text-align: left; }
#simOk { color: #4C7A52; }
#simFail { color: #A32B2B; }
QPlainTextEdit#terminal { background: #171512; color: #4C7A52; border: 1px solid #C9BB94; border-radius: 5px; padding: 8px; font-family: Consolas, monospace; }
#terminalPrompt { color: #8C6D1F; }
QLineEdit#terminalInput { background: #171512; color: #4C7A52; border: 1px solid #C9BB94; }
QPushButton#submitBtn { background: #24211C; color: #E8DFC8; border: none; border-radius: 5px; padding: 10px 20px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
QPushButton#submitBtn:disabled { background: #C9BB94; color: #5C5644; }
QPushButton#nextBtn { background: #8C6D1F; color: #E8DFC8; border: none; border-radius: 5px; padding: 10px 20px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
#verdictPass { color: #4C7A52; border: 2px solid #4C7A52; border-radius: 4px; padding: 6px 12px; font-weight: 600; }
#verdictFail { color: #A32B2B; border: 2px solid #A32B2B; border-radius: 4px; padding: 6px 12px; font-weight: 600; }
#explain { color: #5C5644; font-size: 12px; background: #DCD0AE; border-left: 3px solid #5C5644; border-radius: 0 4px 4px 0; padding: 10px; }
#doneTitle { font-family: 'Segoe UI', sans-serif; font-weight: 600; font-size: 22px; }
#statBig { font-size: 40px; color: #8C6D1F; font-weight: 700; }
"""


def load_state():
    try:
        data = json.loads(STORAGE_PATH.read_text())
        if isinstance(data.get("results"), list) and len(data["results"]) == len(QUESTIONS):
            return data
    except Exception:
        pass
    return {"current": 0, "results": [None] * len(QUESTIONS)}


def save_state(state):
    try:
        STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORAGE_PATH.write_text(json.dumps(state))
    except Exception:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YARI Security+ PBQ Simulator")
        self.resize(780, 860)

        state = load_state()
        self.current = state["current"]
        self.results = state["results"]

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 18, 20, 18)

        header = QFrame()
        header.setObjectName("header")
        h = QVBoxLayout(header)
        top_row = QHBoxLayout()
        case_id = QLabel(f"FILE NO. SEC-PBQ-{len(QUESTIONS):02d}")
        case_id.setObjectName("caseId")
        top_row.addWidget(case_id)
        h.addLayout(top_row)
        title = QLabel("YARI Security+ PBQ Simulator")
        title.setObjectName("title")
        h.addWidget(title)
        sub = QLabel(f"{len(QUESTIONS)} performance-based questions · 7 question types")
        sub.setObjectName("sub")
        h.addWidget(sub)
        score_row = QHBoxLayout()
        self.score_label = QLabel()
        self.score_label.setObjectName("scoreText")
        reset_btn = QPushButton("Reset progress")
        reset_btn.setObjectName("resetBtn")
        reset_btn.clicked.connect(self._reset)
        score_row.addWidget(self.score_label)
        score_row.addStretch(1)
        score_row.addWidget(reset_btn)
        h.addLayout(score_row)
        root.addWidget(header)

        self.rail_layout = QHBoxLayout()
        rail_wrap = QFrame()
        rail_wrap.setObjectName("fileTrack")
        rail_wrap.setLayout(self.rail_layout)
        root.addWidget(rail_wrap)

        self.stage_layout = QVBoxLayout()
        stage_wrap = QWidget()
        stage_wrap.setLayout(self.stage_layout)
        root.addWidget(stage_wrap)
        root.addStretch(1)

        self.render()

    def _reset(self):
        self.current = 0
        self.results = [None] * len(QUESTIONS)
        save_state({"current": 0, "results": self.results})
        self.render()

    def _score(self):
        return sum(1 for r in self.results if r is True)

    def _clear(self, lay):
        while lay.count():
            item = lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def render_rail(self):
        self._clear(self.rail_layout)
        for i in range(len(QUESTIONS)):
            chip = QFrame()
            chip.setFixedHeight(6)
            if self.results[i] is True:
                color = "#8C6D1F"
            elif self.results[i] is False:
                color = "#7A1F1F"
            elif i == self.current:
                color = "#24211C"
            else:
                color = "#DCD0AE"
            chip.setStyleSheet(f"background:{color}; border-radius:3px;")
            self.rail_layout.addWidget(chip)

    def render(self):
        self.score_label.setText(f"Score: {self._score()} / {len(QUESTIONS)}")
        self.render_rail()
        self._clear(self.stage_layout)

        if self.current >= len(QUESTIONS):
            self.render_done()
            return

        q = QUESTIONS[self.current]
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        eng_label = QLabel(f"Question {self.current + 1} of {len(QUESTIONS)} — {ENGINE_LABELS[q['engine']]}")
        eng_label.setObjectName("engLabel")
        layout.addWidget(eng_label)

        title = QLabel(q["title"])
        title.setObjectName("qTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        scenario = QLabel(q["scenario"])
        scenario.setObjectName("scenario")
        scenario.setWordWrap(True)
        layout.addWidget(scenario)

        self.engine_widget = ENGINES[q["engine"]](q)
        layout.addWidget(self.engine_widget)

        self.controls_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("submitBtn")
        self.submit_btn.setEnabled(False)
        self.submit_btn.clicked.connect(lambda: self.finish_question(q))
        self.controls_layout.addStretch(1)
        self.controls_layout.addWidget(self.submit_btn)
        layout.addLayout(self.controls_layout)

        self.engine_widget.readyChanged.connect(self.submit_btn.setEnabled)

        self.stage_layout.addWidget(card)
        self.current_card = card

    def finish_question(self, q):
        correct = self.engine_widget.is_correct()
        self.engine_widget.lock()
        self.engine_widget.setEnabled(False)
        self.submit_btn.hide()

        self.results[self.current] = correct
        save_state({"current": self.current, "results": self.results})
        self.score_label.setText(f"Score: {self._score()} / {len(QUESTIONS)}")
        self.render_rail()

        verdict = QLabel("VERIFIED CORRECT" if correct else "FLAGGED — REVIEW")
        verdict.setObjectName("verdictPass" if correct else "verdictFail")
        self.current_card.layout().addWidget(verdict, alignment=Qt.AlignLeft)

        explain = QLabel("Why: " + q["explanation"])
        explain.setObjectName("explain")
        explain.setWordWrap(True)
        self.current_card.layout().addWidget(explain)

        next_btn = QPushButton("Close case file" if self.current == len(QUESTIONS) - 1 else "Next file →")
        next_btn.setObjectName("nextBtn")

        def go_next():
            self.current += 1
            save_state({"current": self.current, "results": self.results})
            self.render()

        next_btn.clicked.connect(go_next)
        self.current_card.layout().addWidget(next_btn, alignment=Qt.AlignLeft)

    def _build_domain_breakdown(self):
        by_domain = {}
        for i, q in enumerate(QUESTIONS):
            d = by_domain.setdefault(q["domain"], {"correct": 0, "total": 0})
            d["total"] += 1
            if self.results[i] is True:
                d["correct"] += 1
        ranked = sorted(by_domain.items(), key=lambda kv: kv[1]["correct"] / kv[1]["total"], reverse=True)

        wrap = QFrame()
        wrap.setObjectName("card")
        layout = QVBoxLayout(wrap)
        heading = QLabel("DOMAIN BREAKDOWN")
        heading.setObjectName("engLabel")
        layout.addWidget(heading)

        if len(ranked) > 1:
            best_pct = ranked[0][1]["correct"] / ranked[0][1]["total"]
            worst_pct = ranked[-1][1]["correct"] / ranked[-1][1]["total"]
            if best_pct > worst_pct:
                summary = QLabel(f"Strongest: {ranked[0][0]}  ·  Needs review: {ranked[-1][0]}")
                summary.setObjectName("sub")
                summary.setWordWrap(True)
                layout.addWidget(summary)

        for domain, d in ranked:
            pct = round(d["correct"] / d["total"] * 100)
            row = QHBoxLayout()
            name = QLabel(domain)
            name.setWordWrap(True)
            row.addWidget(name, 1)
            score_lbl = QLabel(f"{d['correct']} / {d['total']}  ({pct}%)")
            score_lbl.setObjectName("verdictPass" if pct >= 80 else ("verdictFail" if pct < 50 else "sub"))
            row.addWidget(score_lbl)
            row_wrap = QWidget()
            row_wrap.setLayout(row)
            layout.addWidget(row_wrap)

        return wrap

    def render_done(self):
        score = self._score()
        pct = round(score / len(QUESTIONS) * 100)
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        h2 = QLabel("Case file closed")
        h2.setObjectName("doneTitle")
        layout.addWidget(h2)

        stat = QLabel(f"{score} / {len(QUESTIONS)}")
        stat.setObjectName("statBig")
        layout.addWidget(stat)

        msg = (
            "That's a strong result — you're reading these scenarios the way SY0-701 actually tests them. "
            "Review anything you missed, then try again for a clean file."
            if pct >= 80 else
            "Solid first pass. Reset progress and run it again once you've reviewed the flagged items — "
            "repetition on PBQ-style questions is what makes the exam format stop feeling unfamiliar."
        )
        msg_label = QLabel(msg)
        msg_label.setObjectName("sub")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        layout.addWidget(self._build_domain_breakdown())

        btn_row = QHBoxLayout()
        again_btn = QPushButton("Run it again")
        again_btn.setObjectName("nextBtn")
        again_btn.clicked.connect(self._reset)
        btn_row.addWidget(again_btn)

        flagged = [i for i, r in enumerate(self.results) if r is False]
        if flagged:
            review_btn = QPushButton(f"Review flagged questions ({len(flagged)})")
            review_btn.setObjectName("resetBtn")
            review_btn.clicked.connect(lambda: self._start_review(flagged))
            btn_row.addWidget(review_btn)
        btn_row.addStretch(1)
        btn_row_wrap = QWidget()
        btn_row_wrap.setLayout(btn_row)
        layout.addWidget(btn_row_wrap)

        self.stage_layout.addWidget(card)
        self.current_card = card

    def _start_review(self, flagged):
        self.review_flagged = flagged
        self.review_pos = 0
        self.render_review()

    def render_review(self):
        self._clear(self.stage_layout)
        qi = self.review_flagged[self.review_pos]
        q = QUESTIONS[qi]

        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)

        eng_label = QLabel(
            f"Reviewing flagged {self.review_pos + 1} of {len(self.review_flagged)} "
            f"— Question {qi + 1}: {ENGINE_LABELS[q['engine']]}"
        )
        eng_label.setObjectName("engLabel")
        layout.addWidget(eng_label)

        title = QLabel(q["title"])
        title.setObjectName("qTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        scenario = QLabel(q["scenario"])
        scenario.setObjectName("scenario")
        scenario.setWordWrap(True)
        layout.addWidget(scenario)

        verdict = QLabel("FLAGGED — REVIEW")
        verdict.setObjectName("verdictFail")
        layout.addWidget(verdict, alignment=Qt.AlignLeft)

        explain = QLabel("Why: " + q["explanation"])
        explain.setObjectName("explain")
        explain.setWordWrap(True)
        layout.addWidget(explain)

        nav_row = QHBoxLayout()
        prev_btn = QPushButton("← Previous flagged")
        prev_btn.setObjectName("resetBtn")
        prev_btn.setEnabled(self.review_pos > 0)
        prev_btn.clicked.connect(self._review_prev)
        nav_row.addWidget(prev_btn)
        nav_row.addStretch(1)
        back_btn = QPushButton("Back to results")
        back_btn.setObjectName("resetBtn")
        back_btn.clicked.connect(self.render)
        nav_row.addWidget(back_btn)
        next_btn = QPushButton("Next flagged →")
        next_btn.setObjectName("nextBtn")
        next_btn.setEnabled(self.review_pos < len(self.review_flagged) - 1)
        next_btn.clicked.connect(self._review_next)
        nav_row.addWidget(next_btn)
        nav_wrap = QWidget()
        nav_wrap.setLayout(nav_row)
        layout.addWidget(nav_wrap)

        self.stage_layout.addWidget(card)
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
