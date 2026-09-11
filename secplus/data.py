"""Question bank for the YARI Security+ PBQ Simulator.

The first 8 questions are ported from
legacy-html/YARI Security+ PBQ Simulator.html. Questions 9-11 are new
simulation types (log/alert triage, firewall/ACL builder, Linux terminal)
added for the desktop port.
"""

QUESTIONS = [
    {
        "id": "seq1", "domain": "Security Operations", "engine": "sequencing", "title": "Sequencing — Incident Response Lifecycle",
        "scenario": "A phishing email leads to a compromised workstation. Place the NIST incident response phases in the correct order, from first to last.",
        "items": ["Preparation", "Identification", "Containment", "Eradication", "Recovery", "Lessons Learned"],
        "correct_order": [0, 1, 2, 3, 4, 5],
        "explanation": "NIST SP 800-61 defines the incident response lifecycle as Preparation, Identification, Containment, Eradication, Recovery, and Lessons Learned (post-incident activity). Containment comes before eradication — you stop the bleeding before you remove the cause.",
    },
    {
        "id": "seq2", "domain": "Threats, Vulnerabilities, and Mitigations", "engine": "sequencing", "title": "Sequencing — Vulnerability Management Lifecycle",
        "scenario": "Your team is standing up a vulnerability management program. Place the steps in the order they should occur.",
        "items": ["Identify and inventory assets", "Scan for vulnerabilities", "Assess and prioritize risk", "Remediate findings", "Verify and report"],
        "correct_order": [0, 1, 2, 3, 4],
        "explanation": "You can't scan what you don't know you have, so asset inventory comes first. Scanning surfaces findings, prioritization ranks them by risk, remediation fixes them, and verification confirms the fix actually worked before closing the loop with reporting.",
    },
    {
        "id": "match1", "domain": "Threats, Vulnerabilities, and Mitigations", "engine": "matching", "title": "Matching — Social Engineering Channels",
        "scenario": "Match each social engineering attack to the channel or defining trait it uses.",
        "terms": ["Phishing", "Vishing", "Smishing", "Whaling"],
        "answers": [
            "Fraudulent email trying to trick a user into an action",
            "Voice call impersonating a trusted party",
            "Fraudulent SMS/text message",
            "Phishing aimed specifically at executives",
        ],
        "correct_pairs": [0, 1, 2, 3],
        "explanation": "The attack names map to their channel: phishing = email, vishing = voice, smishing = SMS. Whaling is a phishing variant defined by its target (senior executives / \"big fish\"), not a different channel.",
    },
    {
        "id": "match2", "domain": "General Security Concepts", "engine": "matching", "title": "Matching — Security Control Types",
        "scenario": "Match each control type to an example of that control in practice.",
        "terms": ["Preventive", "Detective", "Corrective", "Deterrent"],
        "answers": [
            "Firewall rule blocking inbound traffic on an unused port",
            "SIEM alert firing on anomalous login behavior",
            "Restoring a system from backup after a ransomware event",
            "Warning banner displayed at login stating activity is monitored",
        ],
        "correct_pairs": [0, 1, 2, 3],
        "explanation": "Preventive controls stop an event before it happens (blocking a port). Detective controls identify an event in progress or after the fact (a SIEM alert). Corrective controls fix things after an incident (restoring from backup). Deterrent controls discourage an attempt without directly blocking it (a monitoring banner).",
    },
    {
        "id": "calc1", "domain": "Security Program Management", "engine": "calculation", "title": "Calculation — Annualized Loss Expectancy",
        "scenario": "A risk assessment finds that a single successful ransomware event would cost the organization $50,000 (SLE). Historical data puts the likelihood at once every 5 years, giving an ARO of 0.2. Calculate the Annualized Loss Expectancy (ALE).",
        "formula_hint": "ALE = SLE × ARO",
        "values": {"SLE": "$50,000", "ARO": "0.2"},
        "correct_answer": 10000,
        "explanation": "ALE = SLE × ARO = $50,000 × 0.2 = $10,000. This is the figure you'd compare against the annual cost of a control to decide whether it's worth implementing.",
    },
    {
        "id": "calc2", "domain": "Security Program Management", "engine": "calculation", "title": "Calculation — Annualized Loss Expectancy",
        "scenario": "A separate risk assessment estimates a single data-exposure incident would cost $8,000 (SLE), and the organization expects this type of event to occur about 3 times per year (ARO). Calculate the ALE.",
        "formula_hint": "ALE = SLE × ARO",
        "values": {"SLE": "$8,000", "ARO": "3"},
        "correct_answer": 24000,
        "explanation": "ALE = SLE × ARO = $8,000 × 3 = $24,000. Note ARO can be greater than 1 when an event is expected to happen more than once a year — it isn't a probability capped at 1.",
    },
    {
        "id": "class1", "domain": "Threats, Vulnerabilities, and Mitigations", "engine": "classification", "title": "Classification — Malware Type",
        "scenario": "An employee's workstation begins encrypting every file it can reach on local and mapped network drives, then displays a message demanding payment in cryptocurrency to restore access. What type of malware is this?",
        "options": ["Worm", "Ransomware", "Rootkit", "Logic bomb"],
        "correct_index": 1,
        "explanation": "Encrypting files and demanding payment for the decryption key is the defining behavior of ransomware. A worm self-propagates across a network without this extortion behavior; a rootkit hides its presence rather than encrypting data; a logic bomb triggers on a specific condition rather than encrypting broadly for ransom.",
    },
    {
        "id": "class2", "domain": "General Security Concepts", "engine": "classification", "title": "Classification — Control Category",
        "scenario": "The organization requires all new hires to complete a security awareness training course before their account is activated. What category of control is this?",
        "options": ["Technical", "Administrative", "Physical", "Compensating"],
        "correct_index": 1,
        "explanation": "Administrative controls are policies, procedures, and training — the human/process side of security. Technical controls are implemented through technology (firewalls, encryption); physical controls are tangible barriers (locks, badges); a compensating control is a substitute used when the primary control can't be applied.",
    },
    {
        "id": "log1", "domain": "Security Operations", "engine": "log_triage", "title": "Log Triage — Authentication Log",
        "scenario": "Review this authentication log feed. Flag every malicious entry, then classify the attack.",
        "log_lines": [
            {"text": "10:02:01  sshd[1122]: Accepted publickey for jdoe from 10.0.4.12 port 51322", "malicious": False},
            {"text": "10:02:44  sshd[1201]: Failed password for root from 203.0.113.44 port 41010", "malicious": True},
            {"text": "10:02:45  sshd[1202]: Failed password for root from 203.0.113.44 port 41011", "malicious": True},
            {"text": "10:02:45  sshd[1203]: Failed password for root from 203.0.113.44 port 41012", "malicious": True},
            {"text": "10:02:46  sshd[1204]: Failed password for admin from 203.0.113.44 port 41013", "malicious": True},
            {"text": "10:03:10  sshd[1250]: Accepted publickey for asmith from 10.0.4.19 port 52110", "malicious": False},
            {"text": "10:03:52  sshd[1301]: Failed password for admin from 203.0.113.44 port 41099", "malicious": True},
            {"text": "10:04:03  cron[900]: (root) CMD (/usr/bin/backup.sh)", "malicious": False},
        ],
        "attack_options": ["SQL injection", "Brute-force login attempt", "DNS tunneling", "Cross-site scripting"],
        "correct_attack_index": 1,
        "explanation": "Repeated failed logins for privileged accounts (root, admin) from a single external IP in rapid succession is the signature of a brute-force login attempt. The two successful publickey logins and the cron entry are unrelated, normal activity from internal hosts and should not be flagged.",
    },
    {
        "id": "fw1", "domain": "Security Architecture", "engine": "firewall", "title": "Firewall/ACL Builder — Perimeter Policy",
        "scenario": (
            "Build an ordered rule set that satisfies this policy: allow inbound HTTPS and DNS, "
            "block inbound Telnet, and deny everything else by default. Drag rules from the pool "
            "into the ruleset, in the order they should be evaluated."
        ),
        "rule_pool": [
            {"id": "allow_https", "label": "ALLOW  tcp   any → any:443  (HTTPS)", "proto": "tcp", "ports": [443], "action": "ALLOW"},
            {"id": "allow_dns", "label": "ALLOW  udp   any → any:53   (DNS)", "proto": "udp", "ports": [53], "action": "ALLOW"},
            {"id": "deny_telnet", "label": "DENY   tcp   any → any:23   (Telnet)", "proto": "tcp", "ports": [23], "action": "DENY"},
            {"id": "allow_telnet", "label": "ALLOW  tcp   any → any:23   (Telnet)", "proto": "tcp", "ports": [23], "action": "ALLOW"},
            {"id": "allow_all", "label": "ALLOW  any   any → any:any  (allow everything)", "proto": "any", "ports": "any", "action": "ALLOW"},
            {"id": "deny_all", "label": "DENY   any   any → any:any  (explicit deny-all)", "proto": "any", "ports": "any", "action": "DENY"},
        ],
        "default_action": "DENY",
        "test_packets": [
            {"desc": "Inbound TCP to port 443", "proto": "tcp", "port": 443, "expected": "ALLOW"},
            {"desc": "Inbound UDP to port 53", "proto": "udp", "port": 53, "expected": "ALLOW"},
            {"desc": "Inbound TCP to port 23 (Telnet)", "proto": "tcp", "port": 23, "expected": "DENY"},
            {"desc": "Inbound TCP to port 8080 (unlisted)", "proto": "tcp", "port": 8080, "expected": "DENY"},
        ],
        "explanation": (
            "The working rule set is: allow HTTPS, allow DNS, deny Telnet, deny all — evaluated top to "
            "bottom with first-match-wins. Including 'allow everything' anywhere above the Telnet deny, "
            "or before the deny-all, would let unwanted traffic straight through regardless of what's "
            "listed after it, which is exactly what the simulated packets above are designed to catch."
        ),
    },
    {
        "id": "term1", "domain": "Security Operations", "engine": "terminal", "title": "Linux Terminal — Find the Weak Permission",
        "scenario": (
            "A web server has been compromised. Use the simulated terminal below to inspect file "
            "permissions in the web root and find the misconfiguration."
        ),
        "prompt": "analyst@sec-host:/var/www/html$",
        "accepted_commands": ["ls -l", "ls -la", "ls -al"],
        "output": (
            "total 24\n"
            "-rw-r--r-- 1 www-data www-data  1420 Sep  2 10:14 index.html\n"
            "-rw-r--r-- 1 www-data www-data   889 Sep  2 10:14 style.css\n"
            "-rwxrwxrwx 1 www-data www-data  4096 Sep  9 03:22 upload.php\n"
            "-rw-r--r-- 1 www-data www-data   212 Aug 14 09:00 config.php\n"
        ),
        "followup_question": "Which file has the dangerous permission misconfiguration, and what's wrong with it?",
        "followup_answer": "upload.php is world-writable",
        "followup_accept_contains": ["upload.php", "777", "world-writable", "world writable"],
        "explanation": (
            "upload.php is set to 777 (rwxrwxrwx) — readable, writable, and executable by everyone on "
            "the system, including any other compromised account or process. Combined with it being a "
            "PHP script, an attacker (or another low-privileged process) could overwrite it with malicious "
            "code and have the web server execute it directly."
        ),
    },
]
