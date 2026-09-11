"""Question bank for the YARI A+ PBQ Simulator, ported from
legacy-html/YARI_A+_PBQ_Simulator.html."""

TOPICS = {
    "core1": [
        {
            "id": "subnetting", "title": "Subnetting", "type": "fill",
            "desc": "Calculate mask, network, broadcast, host range, and usable hosts from a given IP/CIDR.",
        },
        {
            "id": "ports", "title": "Ports & protocols", "type": "match",
            "desc": "Match each protocol to its port number(s).",
            "pairs": [
                ("FTP", "20 / 21"), ("SSH", "22"), ("Telnet", "23"), ("SMTP", "25"), ("DNS", "53"),
                ("DHCP", "67 / 68"), ("HTTP", "80"), ("POP3", "110"), ("IMAP", "143"), ("SNMP", "161 / 162"),
                ("LDAP", "389"), ("HTTPS", "443"), ("SMB", "445"), ("RDP", "3389"),
            ],
            "explain": "Memory aid: FTP=20/21 · SSH=22 · Telnet=23 · SMTP=25 · DNS=53 · DHCP=67/68 · HTTP=80 · POP3=110 · IMAP=143 · SNMP=161/162 · LDAP=389 · HTTPS=443 · SMB=445 · RDP=3389.",
        },
        {
            "id": "cables", "title": "Cables & connectors", "type": "match",
            "desc": "Match each connector to what it is used for.",
            "pairs": [
                ("RJ-45", "Ethernet — Cat5e/6/6a, wired LAN"),
                ("RJ-11", "Telephone line"),
                ("F-Type", "Coaxial — cable TV / cable modem"),
                ("HDMI", "Digital video + audio"),
                ("DisplayPort", "Digital video + audio, daisy-chainable"),
                ("VGA", "Analog video only — legacy"),
                ("DVI-D", "Digital video only, no analog"),
                ("USB-C (USB4/TB4)", "Up to 40 Gbps, video + data + power"),
            ],
            "explain": "VGA is the only fully analog connector in this set — no digital signal, no audio. DVI-D drops the analog pins that DVI-I keeps.",
        },
        {
            "id": "dora", "title": "DHCP DORA order", "type": "sequence",
            "desc": "Put the DHCP lease process in the correct order.",
            "steps": [
                "Discover — client broadcasts for a DHCP server",
                "Offer — server offers an available IP",
                "Request — client broadcasts acceptance of the offer",
                "Acknowledge — server confirms and finalizes the lease",
            ],
            "explain": "DORA: Discover, Offer, Request, Acknowledge. The client broadcasts twice — once to find a server (Discover) and once to accept an offer (Request), which also tells other DHCP servers to withdraw their offers.",
        },
        {
            "id": "raid", "title": "RAID selection", "type": "scenario",
            "desc": "Pick the correct RAID level for each scenario.",
            "questions": [
                {
                    "q": "You have exactly 2 drives and need simple redundancy — if one drive fails, the system keeps running. Capacity is not a concern.",
                    "opts": ["RAID 0", "RAID 1", "RAID 5", "RAID 10"], "answer": 1,
                    "explain": "RAID 1 (mirroring) needs only 2 drives and tolerates 1 failure. RAID 0 has zero redundancy. RAID 5 needs a minimum of 3 drives. RAID 10 needs 4.",
                },
                {
                    "q": "You need the best balance of speed and fault tolerance with 3 drives, and can accept losing capacity to parity.",
                    "opts": ["RAID 0", "RAID 1", "RAID 5", "RAID 10"], "answer": 2,
                    "explain": "RAID 5 (striping with parity) is the standard balance of speed and redundancy with a 3-drive minimum, tolerating 1 drive failure.",
                },
                {
                    "q": "Maximum read/write speed is the priority, and you are fine with zero fault tolerance.",
                    "opts": ["RAID 0", "RAID 1", "RAID 5", "RAID 10"], "answer": 0,
                    "explain": "RAID 0 (striping only) has no redundancy — any single drive failure loses all data — but it is the fastest RAID level.",
                },
                {
                    "q": "You have 4 drives, need the best combination of performance and fault tolerance, and cost is not the deciding factor.",
                    "opts": ["RAID 0", "RAID 1", "RAID 5", "RAID 10"], "answer": 3,
                    "explain": "RAID 10 (mirror + stripe) needs an even number of drives (minimum 4), gives the best performance plus redundancy, at the cost of losing half your capacity.",
                },
            ],
        },
        {
            "id": "printer", "title": "Laser printer process", "type": "sequence",
            "desc": "Put the 7-step laser printing process in order.",
            "steps": [
                "Processing — RIP converts the print job to a bitmap",
                "Charging — primary corona applies negative charge to drum",
                "Exposing — laser neutralizes charge to form the latent image",
                "Developing — toner sticks to the neutralized areas",
                "Transferring — toner moves from drum to paper",
                "Fusing — heat and pressure bond toner to paper",
                "Cleaning — residual toner is scraped from the drum",
            ],
            "explain": 'Mnemonic: "Please Create Exposed Developers That Fuse Cleanly." Processing always comes first — it is pure data prep before anything physical happens. Cleaning is always last, resetting the drum for the next job.',
        },
    ],
    "core2": [
        {
            "id": "troubleshooting", "title": "Troubleshooting methodology", "type": "sequence",
            "desc": "Put the CompTIA 6-step troubleshooting process in order.",
            "steps": [
                "Identify the problem",
                "Establish a theory of probable cause",
                "Test the theory to determine cause",
                "Establish a plan of action and implement it",
                "Verify full system functionality",
                "Document findings, actions, and outcomes",
            ],
            "explain": "This exact order is exam-critical. Note step 5 verifies with the USER, not just yourself — and documentation is always last, after the fix is confirmed working.",
        },
        {
            "id": "malware", "title": "Malware identification", "type": "match",
            "desc": "Match each malware type to how it behaves.",
            "pairs": [
                ("Virus", "Attaches to a file — needs a host file and user action to spread"),
                ("Worm", "Self-replicates across the network with no user action needed"),
                ("Trojan", "Disguised as legitimate software, opens a backdoor"),
                ("Ransomware", "Encrypts files and demands payment"),
                ("Rootkit", "Hides at the OS/kernel level — extremely hard to detect"),
                ("Spyware", "Silently monitors activity and steals data"),
                ("Keylogger", "Records every keystroke"),
                ("Fileless malware", "Runs in memory only — no file for antivirus to scan"),
            ],
            "explain": "The key exam distinction: a virus needs a host file and user action; a worm spreads on its own over the network with no user interaction required.",
        },
        {
            "id": "wireless", "title": "Wireless security — worst to best", "type": "sequence",
            "desc": "Order these Wi-Fi security protocols from weakest to strongest.",
            "steps": [
                "WEP — RC4, broken, crackable in minutes",
                "WPA — TKIP, a temporary fix for WEP, still weak",
                "WPA2-Personal — AES-CCMP, PSK, acceptable standard",
                "WPA3-Personal — AES-192+SAE, best available for home use",
            ],
            "explain": "WEP was deprecated in 2004 and is trivially crackable. WPA was a stopgap using TKIP, which is also vulnerable. WPA2 introduced AES-CCMP as the real standard. WPA3 replaces the PSK handshake with SAE, closing offline dictionary attacks.",
        },
        {
            "id": "commands", "title": "Windows command line", "type": "match",
            "desc": "Match each command to what it does.",
            "pairs": [
                ("ipconfig /all", "Shows full IP configuration detail"),
                ("ping -t", "Continuously tests connectivity to a host"),
                ("tracert", "Shows each network hop to a destination"),
                ("nslookup", "Queries DNS to resolve a hostname"),
                ("netstat -an", "Shows all active connections, numeric form"),
                ("sfc /scannow", "Scans and repairs corrupted system files"),
                ("chkdsk /f /r", "Checks the disk for errors and bad sectors"),
                ("bootrec /fixmbr", "Rewrites a corrupted Master Boot Record"),
            ],
            "explain": "sfc protects Windows system files; chkdsk protects the disk itself; bootrec repairs the boot process. Knowing which layer each command operates on is the key exam distinction.",
        },
    ],
}
