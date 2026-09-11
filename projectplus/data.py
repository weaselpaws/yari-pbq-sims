"""Question bank for the YARI Project+ PBQ Simulator, ported from the
original HTML prototype (legacy-html/YARI_ProjectPlus_PBQ_Simulator.html)."""

QUESTIONS = [
    # 1. Sequencing — process groups
    {
        "engine": "sequence",
        "tag": "SEQUENCING",
        "prompt": "Arrange the five process groups in the order they occur across a project's life cycle.",
        "sub": "Tap each item in the correct order. Tap a placed item to undo it.",
        "items": ["Executing", "Closing", "Initiating", "Monitoring & Controlling", "Planning"],
        "answer": ["Initiating", "Planning", "Executing", "Monitoring & Controlling", "Closing"],
    },
    # 2. Sequencing — change control
    {
        "engine": "sequence",
        "tag": "SEQUENCING",
        "prompt": "Put the steps of a standard change control process in order.",
        "sub": "Tap each item in the correct order.",
        "items": [
            "Update the baseline and communicate the change",
            "Submit a change request",
            "Change Control Board reviews and decides",
            "Assess impact on scope, schedule, and cost",
        ],
        "answer": [
            "Submit a change request",
            "Assess impact on scope, schedule, and cost",
            "Change Control Board reviews and decides",
            "Update the baseline and communicate the change",
        ],
    },
    # 3. Matching — terms
    {
        "engine": "match",
        "tag": "MATCHING",
        "prompt": "Match each term to its correct definition.",
        "sub": "Tap a term, then tap its matching definition.",
        "left": ["Float", "Critical Path", "Scope Creep", "Baseline"],
        "right": [
            "The longest sequence of dependent tasks that determines the shortest possible project duration",
            "Uncontrolled expansion of project scope without corresponding adjustments to time, cost, or resources",
            "The approved version of a project plan used as a fixed point of comparison",
            "The amount of time a task can slip without delaying the project finish date",
        ],
        "pairs": {0: 3, 1: 0, 2: 1, 3: 2},
    },
    # 4. Matching — tools
    {
        "engine": "match",
        "tag": "MATCHING",
        "prompt": "Match each project management tool to its primary purpose.",
        "sub": "Tap a tool, then tap its matching purpose.",
        "left": ["Gantt Chart", "RACI Matrix", "Risk Register", "Fishbone Diagram"],
        "right": [
            "Identifies who is Responsible, Accountable, Consulted, and Informed for each task",
            "Visualizes task schedules and durations as horizontal bars across a timeline",
            "Traces a problem back to its root cause across categories like people, process, and equipment",
            "Logs identified risks along with their probability, impact, and response plan",
        ],
        "pairs": {0: 1, 1: 0, 2: 3, 3: 2},
    },
    # 5. Calculation — EVM
    {
        "engine": "calc",
        "tag": "CALCULATION",
        "prompt": "Using the earned value data below, calculate the Cost Performance Index (CPI) and Schedule Performance Index (SPI).",
        "sub": "CPI = EV ÷ AC  ·  SPI = EV ÷ PV  ·  Round to 2 decimal places.",
        "table": [
            ("Planned Value (PV)", "$40,000"),
            ("Earned Value (EV)", "$36,000"),
            ("Actual Cost (AC)", "$30,000"),
        ],
        "fields": [
            {"id": "cpi", "label": "CPI", "answer": 1.20, "tolerance": 0.02},
            {"id": "spi", "label": "SPI", "answer": 0.90, "tolerance": 0.02},
        ],
    },
    # 6. Calculation — critical path / float
    {
        "engine": "calc",
        "tag": "CALCULATION",
        "prompt": "A project has two paths from start to finish: Path A takes 22 days, Path B takes 17 days.",
        "sub": "Enter the critical path duration, and the total float available on Path B.",
        "table": [("Path A duration", "22 days"), ("Path B duration", "17 days")],
        "fields": [
            {"id": "cp", "label": "Critical path (days)", "answer": 22, "tolerance": 0},
            {"id": "float", "label": "Float on Path B (days)", "answer": 5, "tolerance": 0},
        ],
    },
    # 7. Classification — knowledge areas
    {
        "engine": "classify",
        "tag": "CLASSIFICATION",
        "prompt": "Sort each scenario into the knowledge area it best represents.",
        "sub": "Tap a scenario, then tap the bucket it belongs in.",
        "items": [
            {"text": "The client adds three new deliverables mid-project without adjusting the deadline", "bucket": 0},
            {"text": "The team debates whether to escalate a vendor delay to the sponsor immediately or wait for the weekly update", "bucket": 1},
            {"text": "A key supplier's parts cost rises 15%, pushing the project over its approved budget", "bucket": 2},
        ],
        "buckets": ["Scope", "Communications", "Cost"],
    },
    # 8. Classification — process groups
    {
        "engine": "classify",
        "tag": "CLASSIFICATION",
        "prompt": "Sort each activity into the process group it belongs to.",
        "sub": "Tap an activity, then tap the bucket it belongs in.",
        "items": [
            {"text": "Drafting the project charter and identifying stakeholders", "bucket": 0},
            {"text": "Comparing actual progress against the schedule baseline and issuing status reports", "bucket": 1},
            {"text": "Releasing project resources and archiving lessons learned", "bucket": 2},
        ],
        "buckets": ["Initiating", "Monitoring & Controlling", "Closing"],
    },
]
