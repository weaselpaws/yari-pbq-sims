"""YARI A+ PBQ Simulator — PySide6 desktop port (Core 1 & Core 2).

Ported from legacy-html/YARI_A+_PBQ_Simulator.html.
"""
import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QMessageBox,
)

from data import TOPICS
from engines import ENGINES

STORAGE_PATH = Path.home() / ".yari_pbq" / "aplus.json"

STYLE = """
QWidget { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; font-size: 13.5px; }
#sidebar { background: #161b22; border-right: 1px solid #30363d; }
#brandText { color: #8b949e; font-family: Consolas, monospace; font-size: 13px; }
#sectLabel { color: #8b949e; font-size: 11px; font-weight: 600; margin-top: 10px; }
QPushButton#topicBtn { text-align: left; background: transparent; border: 1px solid transparent; border-radius: 6px; padding: 8px 10px; }
QPushButton#topicBtn:hover { background: #1c2129; }
QPushButton#topicBtn[active="true"] { background: #3d2f0f; border-color: #f0b429; color: #f0b429; }
#topicTitle { font-size: 20px; font-weight: 600; }
#overall { color: #8b949e; font-family: Consolas, monospace; font-size: 13px; }
#subtitle { color: #8b949e; font-size: 13px; margin-bottom: 10px; }
#card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 18px; }
#prompt { font-size: 15px; }
#given { font-family: Consolas, monospace; font-size: 20px; font-weight: 600; color: #f0b429; }
#fieldLabel { color: #8b949e; font-size: 12px; }
QLineEdit { background: #1c2129; border: 1px solid #30363d; border-radius: 6px; padding: 8px; color: #c9d1d9; font-family: Consolas, monospace; }
QLineEdit[correct="true"] { border-color: #3fb950; }
QLineEdit[wrong="true"] { border-color: #f85149; }
QComboBox { background: #1c2129; border: 1px solid #30363d; border-radius: 6px; padding: 6px; color: #c9d1d9; }
#matchTerm { font-family: Consolas, monospace; }
#matchRow[correct="true"] QComboBox { border-color: #3fb950; }
#matchRow[wrong="true"] QComboBox { border-color: #f85149; }
#seqRow[correct="true"] QComboBox { border-color: #3fb950; }
#seqRow[wrong="true"] QComboBox { border-color: #f85149; }
QPushButton#btnPrimary { background: #3d2f0f; border: 1px solid #f0b429; color: #f0b429; border-radius: 6px; padding: 9px 14px; font-weight: 600; }
QPushButton#btnAction { background: transparent; border: 1px solid #30363d; color: #c9d1d9; border-radius: 6px; padding: 9px 14px; }
QPushButton#btnAction:hover { background: #1c2129; }
QPushButton#scenarioOpt { text-align: left; background: #1c2129; border: 1px solid #30363d; border-radius: 6px; padding: 10px 12px; }
QPushButton#scenarioOpt:hover { border-color: #f0b429; }
QPushButton#scenarioOpt[chosenRight="true"] { border-color: #3fb950; background: #122117; }
QPushButton#scenarioOpt[chosenWrong="true"] { border-color: #f85149; background: #2a1315; }
"""


def load_scores():
    try:
        return json.loads(STORAGE_PATH.read_text())
    except Exception:
        return {}


def save_scores(scores):
    try:
        STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STORAGE_PATH.write_text(json.dumps(scores))
    except Exception:
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YARI A+ PBQ Simulator — Core 1 & Core 2")
        self.resize(1000, 700)

        self.scores = load_scores()
        self.section = "core1"
        self.topic_id = TOPICS["core1"][0]["id"]

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Sidebar ----
        sidebar = QScrollArea()
        sidebar.setObjectName("sidebar")
        sidebar.setWidgetResizable(True)
        sidebar.setFixedWidth(260)
        sidebar_inner = QWidget()
        self.sidebar_layout = QVBoxLayout(sidebar_inner)
        self.sidebar_layout.setContentsMargins(16, 20, 16, 20)
        brand = QLabel("YARI // PBQ SIMULATOR")
        brand.setObjectName("brandText")
        self.sidebar_layout.addWidget(brand)
        self.nav_container = QVBoxLayout()
        nav_wrap = QWidget()
        nav_wrap.setLayout(self.nav_container)
        self.sidebar_layout.addWidget(nav_wrap)
        self.sidebar_layout.addStretch(1)
        sidebar.setWidget(sidebar_inner)
        root.addWidget(sidebar)

        # ---- Main area ----
        main_wrap = QWidget()
        main_layout = QVBoxLayout(main_wrap)
        main_layout.setContentsMargins(40, 32, 40, 32)

        header_row = QHBoxLayout()
        self.topic_title = QLabel("Loading…")
        self.topic_title.setObjectName("topicTitle")
        header_row.addWidget(self.topic_title)
        header_row.addStretch(1)
        domain_summary_btn = QPushButton("Domain summary")
        domain_summary_btn.setObjectName("btnAction")
        domain_summary_btn.clicked.connect(self.show_domain_summary)
        header_row.addWidget(domain_summary_btn)
        self.overall_label = QLabel()
        self.overall_label.setObjectName("overall")
        header_row.addWidget(self.overall_label)
        main_layout.addLayout(header_row)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setWordWrap(True)
        main_layout.addWidget(self.subtitle)

        self.card_area = QVBoxLayout()
        card_wrap = QWidget()
        card_wrap.setLayout(self.card_area)
        main_layout.addWidget(card_wrap)
        main_layout.addStretch(1)

        root.addWidget(main_wrap, 1)

        self.render_nav()
        self.render_overall()
        self.load_topic()

    def find_topic(self, topic_id):
        for t in TOPICS["core1"] + TOPICS["core2"]:
            if t["id"] == topic_id:
                return t
        return None

    def record_result(self, topic_id, correct):
        s = self.scores.get(topic_id, {"correct": 0, "total": 0})
        s["total"] += 1
        if correct:
            s["correct"] += 1
        self.scores[topic_id] = s
        save_scores(self.scores)
        self.render_nav()
        self.render_overall()

    def render_nav(self):
        while self.nav_container.count():
            item = self.nav_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for section, heading in (("core1", "A+ Core 1 · 220-1201"), ("core2", "A+ Core 2 · 220-1202")):
            label = QLabel(heading)
            label.setObjectName("sectLabel")
            self.nav_container.addWidget(label)
            for t in TOPICS[section]:
                s = self.scores.get(t["id"])
                score_text = f"{s['correct']}/{s['total']}" if s else "—"
                btn = QPushButton(f"{t['title']}          {score_text}")
                btn.setObjectName("topicBtn")
                btn.setProperty("active", t["id"] == self.topic_id)
                btn.clicked.connect(lambda _=False, sec=section, tid=t["id"]: self._select_topic(sec, tid))
                self.nav_container.addWidget(btn)

    def _select_topic(self, section, topic_id):
        self.section = section
        self.topic_id = topic_id
        self.render_nav()
        self.load_topic()

    def render_overall(self):
        c = sum(s["correct"] for s in self.scores.values())
        t = sum(s["total"] for s in self.scores.values())
        self.overall_label.setText(f"overall {c}/{t}" if t else "")

    def show_modal(self, text):
        box = QMessageBox(self)
        box.setWindowTitle("Not quite")
        box.setText(text)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()

    def show_domain_summary(self):
        by_domain = {}
        for t in TOPICS["core1"] + TOPICS["core2"]:
            s = self.scores.get(t["id"])
            if not s or s["total"] == 0:
                continue
            d = by_domain.setdefault(t["domain"], {"correct": 0, "total": 0})
            d["correct"] += s["correct"]
            d["total"] += s["total"]

        box = QMessageBox(self)
        box.setWindowTitle("Domain Summary")
        if not by_domain:
            box.setText("No questions answered yet — try a few topics first.")
        else:
            ranked = sorted(by_domain.items(), key=lambda kv: kv[1]["correct"] / kv[1]["total"], reverse=True)
            lines = []
            if len(ranked) > 1:
                best_pct = ranked[0][1]["correct"] / ranked[0][1]["total"]
                worst_pct = ranked[-1][1]["correct"] / ranked[-1][1]["total"]
                if best_pct > worst_pct:
                    lines.append(f"Strongest: {ranked[0][0]}   ·   Needs review: {ranked[-1][0]}\n")
            for domain, d in ranked:
                pct = round(d["correct"] / d["total"] * 100)
                lines.append(f"{domain}: {d['correct']} / {d['total']}  ({pct}%)")
            box.setText("\n".join(lines))
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()

    def load_topic(self):
        topic = self.find_topic(self.topic_id)
        self.topic_title.setText(topic["title"])
        self.subtitle.setText(topic["desc"])

        while self.card_area.count():
            item = self.card_area.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        engine_cls = ENGINES[topic["type"]]
        widget = engine_cls(topic, self.record_result, self.show_modal)
        widget.setObjectName("card")
        self.card_area.addWidget(widget)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
