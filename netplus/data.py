"""Question bank for the YARI Network+ PBQ Simulator.

The first 8 questions are ported from
legacy-html/YARI Network+ PBQ Simulator.html. Questions 9-10 are new
simulation types (topology builder, CLI terminal) added for the desktop port.
"""

QUESTIONS = [
    {
        "id": "seq1", "domain": "Networking Concepts", "engine": "sequencing", "title": "Sequencing — OSI Model",
        "scenario": "Place the OSI model layers in order, starting from Layer 1 (Physical) and working up to Layer 7 (Application).",
        "items": ["Physical", "Data Link", "Network", "Transport", "Session", "Presentation", "Application"],
        "correct_order": [0, 1, 2, 3, 4, 5, 6],
        "explanation": 'Bottom to top: Physical, Data Link, Network, Transport, Session, Presentation, Application. A common mnemonic is "Please Do Not Throw Sausage Pizza Away." Knowing which layer a device or problem lives at is one of the most heavily tested Network+ skills.',
    },
    {
        "id": "seq2", "domain": "Networking Concepts", "engine": "sequencing", "title": "Sequencing — DHCP Lease Process",
        "scenario": "A workstation boots up and needs an IP address from the DHCP server. Place the steps of the DHCP process (DORA) in order.",
        "items": [
            "Discover — client broadcasts for a DHCP server",
            "Offer — server offers an available IP address",
            "Request — client requests the offered address",
            "Acknowledge — server confirms the lease",
        ],
        "correct_order": [0, 1, 2, 3],
        "explanation": "DORA: Discover, Offer, Request, Acknowledge. The client broadcasts first since it has no IP yet, the server offers a lease, the client explicitly requests it (so multiple DHCP servers know only one offer was accepted), and the server acknowledges to finalize the lease.",
    },
    {
        "id": "match1", "domain": "Networking Concepts", "engine": "matching", "title": "Matching — Well-Known Ports",
        "scenario": "Match each protocol to its well-known port number.",
        "terms": ["FTP", "SSH", "DNS", "HTTPS"],
        "answers": ["Port 21", "Port 22", "Port 53", "Port 443"],
        "correct_pairs": [0, 1, 2, 3],
        "explanation": "FTP uses port 21 for control (20 for data), SSH uses port 22, DNS uses port 53, and HTTPS uses port 443. These well-known ports show up constantly on the exam, both directly and buried inside troubleshooting scenarios.",
    },
    {
        "id": "match2", "domain": "Networking Concepts", "engine": "matching", "title": "Matching — Devices to OSI Layer",
        "scenario": "Match each network device to the OSI layer it primarily operates at.",
        "terms": ["Hub", "Switch", "Router", "NIC"],
        "answers": ["Layer 1 — Physical", "Layer 2 — Data Link", "Layer 3 — Network", "Layer 1/2 — Physical and Data Link"],
        "correct_pairs": [0, 1, 2, 3],
        "explanation": "A hub just repeats electrical signals with no addressing awareness (Layer 1). A switch forwards frames using MAC addresses (Layer 2). A router forwards packets using IP addresses (Layer 3). A NIC straddles both — it has a physical connection and a burned-in MAC address.",
    },
    {
        "id": "calc1", "domain": "Networking Concepts", "engine": "calculation", "title": "Calculation — Usable Hosts per Subnet",
        "scenario": "A subnet is assigned a /28 CIDR mask. Calculate the number of usable host addresses in that subnet.",
        "formula_hint": "Usable hosts = 2^(host bits) − 2",
        "values": {"CIDR": "/28", "Host bits": "32 − 28 = 4"},
        "correct_answer": 14,
        "explanation": "A /28 leaves 4 host bits (32 − 28 = 4). 2^4 = 16 total addresses, minus 2 for the network and broadcast addresses = 14 usable hosts.",
    },
    {
        "id": "calc2", "domain": "Networking Concepts", "engine": "calculation", "title": "Calculation — Usable Hosts per Subnet",
        "scenario": "A subnet is assigned a /26 CIDR mask. Calculate the number of usable host addresses in that subnet.",
        "formula_hint": "Usable hosts = 2^(host bits) − 2",
        "values": {"CIDR": "/26", "Host bits": "32 − 26 = 6"},
        "correct_answer": 62,
        "explanation": "A /26 leaves 6 host bits (32 − 26 = 6). 2^6 = 64 total addresses, minus 2 for the network and broadcast addresses = 62 usable hosts.",
    },
    {
        "id": "class1", "domain": "Network Troubleshooting", "engine": "classification", "title": "Classification — OSI Layer of the Fault",
        "scenario": "Two devices on the same VLAN can't communicate. You check and find one has a correctly assigned IP with the right subnet mask, but a technician recently swapped the patch cable into a port assigned to a different VLAN. What OSI layer is this fault at?",
        "options": ["Layer 1 — Physical", "Layer 2 — Data Link", "Layer 3 — Network", "Layer 4 — Transport"],
        "correct_index": 1,
        "explanation": "VLAN assignment is a Data Link (Layer 2) concept — switches use VLAN tags/port assignments to segment broadcast domains at Layer 2. The cable itself is fine (Layer 1 is working) and the IP addressing is correct (Layer 3 is fine), so the fault is the port's VLAN membership, which is Layer 2.",
    },
    {
        "id": "class2", "domain": "Networking Implementation", "engine": "classification", "title": "Classification — Network Topology",
        "scenario": "In this topology, every device connects to a central switch. If one device's cable is unplugged, the rest of the network is unaffected, but if the central switch fails, the entire segment goes down. What topology is this?",
        "options": ["Bus", "Ring", "Star", "Mesh"],
        "correct_index": 2,
        "explanation": "A star topology connects every device to a central point (a switch or hub). It isolates individual cable failures well, but the central device becomes a single point of failure — exactly the trade-off described here. A mesh topology, by contrast, would survive the loss of any single node.",
    },
    {
        "id": "topo1", "domain": "Networking Implementation", "engine": "topology", "title": "Topology Builder — Small Office LAN",
        "scenario": (
            "Wire this small office LAN: both workstations (PC-1, PC-2) connect to the Switch, "
            "the Switch connects to the Router, and the Router connects to the Internet (WAN)."
        ),
        "devices": ["PC-1", "PC-2", "Switch", "Router", "Internet (WAN)"],
        "required_links": [("PC-1", "Switch"), ("PC-2", "Switch"), ("Switch", "Router"), ("Router", "Internet (WAN)")],
        "explanation": "End devices always terminate on an access-layer switch, never directly on the router in this design. The switch aggregates the LAN up to the router, and the router is the boundary device to the WAN/Internet — exactly the topology CompTIA expects you to recognize and build.",
    },
    {
        "id": "term1", "domain": "Network Troubleshooting", "engine": "terminal", "title": "CLI Simulator — Diagnose the Connection",
        "scenario": (
            "A user reports they can't reach any websites. Use the simulated Windows command prompt below "
            "to check the workstation's IP configuration."
        ),
        "prompt": "C:\\Users\\jdoe>",
        "accepted_commands": ["ipconfig /all", "ipconfig"],
        "output": (
            "Windows IP Configuration\n\n"
            "Ethernet adapter Ethernet:\n\n"
            "   Connection-specific DNS Suffix  . : corp.local\n"
            "   IPv4 Address. . . . . . . . . . . : 169.254.34.12\n"
            "   Subnet Mask . . . . . . . . . . . : 255.255.0.0\n"
            "   Default Gateway . . . . . . . . . :\n"
        ),
        "followup_question": "Based on this output, what is most likely wrong with the workstation's network connection?",
        "followup_answer": "no dhcp",
        "followup_accept_contains": ["apipa", "dhcp", "169.254", "dora", "lease"],
        "explanation": (
            "169.254.x.x is an APIPA address — Windows assigns this automatically when it can't reach a "
            "DHCP server. The missing Default Gateway confirms it: the workstation never got a real lease, "
            "so it can only talk to other devices on the same local segment, not the internet."
        ),
    },
]
