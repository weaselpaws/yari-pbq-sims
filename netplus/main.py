"""YARI Network+ PBQ Simulator — PySide6 desktop port.

Ported from legacy-html/YARI Network+ PBQ Simulator.html, plus two new
simulation types: a topology builder and a CLI terminal simulator.
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

STORAGE_PATH = Path.home() / ".yari_pbq" / "netplus.json"

ENGINE_LABELS = {
    "sequencing": "Sequencing", "matching": "Matching", "calculation": "Calculation",
    "classification": "Classification", "topology": "Topology Builder", "terminal": "CLI Simulator",
}

STYLE = """
QWidget { background-color: #1B1D1F; color: #E8E9EA; font-family: Consolas, 'Courier New', monospace; font-size: 13px; }
#header { background: #2A2D30; border: 1px solid #3E4245; border-radius: 6px; }
#unitId { color: #8D9296; font-size: 11px; }
#title { font-size: 22px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
#sub { color: #8D9296; font-size: 12px; }
#scoreText { font-size: 14px; }
QPushButton#resetBtn { background: none; border: 1px solid #8D9296; color: #8D9296; border-radius: 4px; padding: 5px 10px; }
QPushButton#resetBtn:hover { border-color: #C1524A; color: #C1524A; }
#portRail { background: #141618; border: 1px solid #3E4245; border-radius: 6px; }
.portLabel { color: #8D9296; font-size: 9px; }
#card { background: #2A2D30; border: 1px solid #3E4245; border-radius: 6px; padding: 18px; }
#engLabel { color: #D97D3D; font-size: 10px; }
#qTitle { font-family: 'Segoe UI', sans-serif; font-weight: 600; font-size: 17px; }
#scenario { color: #8D9296; font-size: 12.5px; background: #141618; border-left: 3px solid #3E7CB1; border-radius: 0 4px 4px 0; padding: 10px; }
#hint { color: #8D9296; font-size: 11.5px; }
#seqPool { background: #141618; border: 1px dashed #3E4245; border-radius: 6px; padding: 8px; }
QPushButton#seqChip { background: #141618; border: 1px solid #3E4245; color: #E8E9EA; border-radius: 5px; padding: 8px 10px; }
#seqSlot, #seqSlotCorrect, #seqSlotWrong { background: #141618; border: 1px dashed #3E4245; border-radius: 5px; padding: 8px; }
#seqSlotCorrect { border: 1px solid #5FA65F; background: #1E2B1E; }
#seqSlotWrong { border: 1px solid #C1524A; background: #2B1E1D; }
#seqNum { color: #D97D3D; font-weight: 600; }
QPushButton#matchTerm { background: #141618; border: 1px solid #3E4245; border-radius: 5px; padding: 10px; text-align: left; }
QPushButton#matchTerm[selected="true"] { border-color: #3E7CB1; background: #213041; }
QPushButton#matchTerm[locked="true"] { border-color: #5FA65F; background: #1E2B1E; color: #8D9296; }
QPushButton#opt { width: 100%; text-align: left; background: #141618; border: 1px solid #3E4245; color: #E8E9EA; border-radius: 5px; padding: 11px 14px; }
QPushButton#opt:hover { border-color: #3E7CB1; }
QPushButton#opt[selected="true"] { border-color: #3E7CB1; background: #213041; }
QPushButton#opt[locked="true"] { border-color: #5FA65F; background: #1E2B1E; }
QPushButton#opt[wrongFlash="true"] { border-color: #C1524A; }
QPushButton#opt[correct="true"] { border-color: #5FA65F; background: #1E2B1E; }
QPushButton#opt[wrong="true"] { border-color: #C1524A; background: #2B1E1D; }
#calcValue { color: #D97D3D; }
QLineEdit { background: #141618; border: 1px solid #3E4245; border-radius: 5px; padding: 8px; color: #E8E9EA; font-family: Consolas, monospace; }
QLineEdit[correct="true"] { border-color: #5FA65F; }
QLineEdit[wrong="true"] { border-color: #C1524A; }
QPushButton#linkClear { background: none; border: none; color: #8D9296; text-decoration: underline; }
QPlainTextEdit#terminal { background: #0A0B0C; color: #5FA65F; border: 1px solid #3E4245; border-radius: 5px; padding: 8px; }
#terminalPrompt { color: #3E7CB1; }
QLineEdit#terminalInput { background: #0A0B0C; color: #5FA65F; border: 1px solid #3E4245; }
QPushButton#submitBtn { background: #3E7CB1; color: #fff; border: none; border-radius: 5px; padding: 10px 20px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
QPushButton#submitBtn:disabled { background: #3E4245; color: #8D9296; }
QPushButton#nextBtn { background: #D97D3D; color: #211205; border: none; border-radius: 5px; padding: 10px 20px; font-weight: 600; font-family: 'Segoe UI', sans-serif; }
#verdictPass { color: #B7D9B7; background: #1E2B1E; border: 1px solid #5FA65F; border-radius: 4px; padding: 6px 12px; font-weight: 600; }
#verdictFail { color: #E3B5B1; background: #2B1E1D; border: 1px solid #C1524A; border-radius: 4px; padding: 6px 12px; font-weight: 600; }
#explain { color: #8D9296; font-size: 12px; background: #141618; border-left: 3px solid #8D9296; border-radius: 0 4px 4px 0; padding: 10px; }
#doneTitle { font-family: 'Segoe UI', sans-serif; font-weight: 600; font-size: 22px; }
#statBig { font-size: 40px; color: #D97D3D; font-weight: 700; }
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
        self.setWindowTitle("YARI Network+ PBQ Simulator")
        self.resize(780, 820)

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
        unit = QLabel("PATCH PANEL — 10 PORTS")
        unit.setObjectName("unitId")
        top_row.addWidget(unit)
        h.addLayout(top_row)
        title = QLabel("YARI Network+ PBQ Simulator")
        title.setObjectName("title")
        h.addWidget(title)
        sub = QLabel(f"{len(QUESTIONS)} performance-based questions · 6 question types")
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
        rail_wrap.setObjectName("portRail")
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
            lbl = QLabel(str(i + 1))
            lbl.setProperty("class", "portLabel")
            lbl.setAlignment(Qt.AlignCenter)
            if self.results[i] is True:
                color = "#5FA65F"
            elif self.results[i] is False:
                color = "#C1524A"
            elif i == self.current:
                color = "#3E7CB1"
            else:
                color = "#333739"
            lbl.setStyleSheet(f"background:{color}; border-radius:2px; padding:6px 2px; color:#141618; font-weight:600;")
            self.rail_layout.addWidget(lbl)

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

        eng_label = QLabel(f"Port {self.current + 1} of {len(QUESTIONS)} — {ENGINE_LABELS[q['engine']]}")
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

        verdict = QLabel("LINK UP — CORRECT" if correct else "LINK DOWN — REVIEW")
        verdict.setObjectName("verdictPass" if correct else "verdictFail")
        self.current_card.layout().addWidget(verdict, alignment=Qt.AlignLeft)

        explain = QLabel("Why: " + q["explanation"])
        explain.setObjectName("explain")
        explain.setWordWrap(True)
        self.current_card.layout().addWidget(explain)

        next_btn = QPushButton("Close panel" if self.current == len(QUESTIONS) - 1 else "Next port →")
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
            row.addWidget(name)
            row.addStretch(1)
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

        h2 = QLabel("Panel fully patched")
        h2.setObjectName("doneTitle")
        layout.addWidget(h2)

        stat = QLabel(f"{score} / {len(QUESTIONS)}")
        stat.setObjectName("statBig")
        layout.addWidget(stat)

        msg = (
            "Strong run — you're handling OSI layers, addressing math, and device roles the way N10-009 "
            "actually tests them. Review anything flagged, then run it again clean."
            if pct >= 80 else
            "Solid first pass. Reset progress and run it again once you've reviewed the flagged ports — "
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
            f"— Port {qi + 1}: {ENGINE_LABELS[q['engine']]}"
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

        verdict = QLabel("LINK DOWN — REVIEW")
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
