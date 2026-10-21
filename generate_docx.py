# -*- coding: utf-8 -*-
"""
Generates the complete Microsoft Word (.docx) report using python-docx,
matching the university template formatting.
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_report_docx():
    template_path = r'c:\Users\psoha\Downloads\Final_Computer_Networks_Mini_Project_Report_Template.docx'
    output_downloads = r'c:\Users\psoha\Downloads\Network_Troubleshooting_Assistant_Report.docx'
    output_project = r'e:\MITWPU\Engineering\3rd Year\CN\Project\Network-Troubleshooting-Assistant-main\Network_Troubleshooting_Assistant_Report.docx'
    
    # We can create a pristine Document using python-docx
    doc = docx.Document()
    
    # Page setup: A4, 1-inch margins
    sections = doc.sections
    for s in sections:
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Base style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    logo_path = r'c:\Users\psoha\Downloads\media\image1.png'
    
    # ---------------- COVER PAGE ----------------
    if os.path.exists(logo_path):
        doc.add_picture(logo_path, width=Inches(4.3))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("\nDepartment of Computer Engineering and Technology\n")
    r.bold = True
    r.font.size = Pt(13)
    r = p.add_run("MINI PROJECT REPORT\nComputer Networks Laboratory (CSE20110)\nLaboratory Continuous Assessment 3\n\n")
    r.bold = True
    r.font.size = Pt(12)

    r = p.add_run("Network Troubleshooting Assistant:\nAutonomous Cross-Layer Network Diagnostic and Root-Cause Analysis System\n\n")
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    r = p.add_run("Submitted by\n")
    r.bold = True

    # Student Table
    t = doc.add_table(rows=5, cols=3)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Sr. No.", "Student Name", "PRN"]
    for j, h in enumerate(headers):
        cell = t.cell(0, j)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT

    students = [
        ("1", "Soham Patil", "1272250811"),
        ("2", "Ganesh Gaikwad", "1262252319"),
        ("3", "Tirth Gangani", "1272250827"),
        ("4", "Aditya Sardesai", "1262252353")
    ]
    for i, row_data in enumerate(students):
        for j, val in enumerate(row_data):
            t.cell(i+1, j).paragraphs[0].text = val

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.add_run("\nGroup No. ___________     Panel E     Batch E2\n")
    p_meta.add_run("Third Year B.Tech. Computer Engineering and Technology\n\n")
    p_meta.add_run("Under the guidance of\n")
    r_guide = p_meta.add_run("Mr. Saiprasad Ratankumar\n\n")
    r_guide.bold = True
    p_meta.add_run("Academic Year 2026–2027\n")
    p_meta.add_run("Submission Date: 21st October 2026\n")

    doc.add_page_break()

    # ---------------- CERTIFICATE PAGE ----------------
    if os.path.exists(logo_path):
        doc.add_picture(logo_path, width=Inches(4.3))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_cert_title.add_run("\nDepartment of Computer Engineering and Technology\n")
    r.bold = True
    r = p_cert_title.add_run("CERTIFICATE\n\n")
    r.bold = True
    r.font.size = Pt(14)

    p_cert = doc.add_paragraph()
    p_cert.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cert.paragraph_format.line_spacing = 1.5
    p_cert.add_run("This is to certify that the mini-project entitled ")
    r = p_cert.add_run("“Network Troubleshooting Assistant: Autonomous Cross-Layer Network Diagnostic and Root-Cause Analysis System”")
    r.bold = True
    p_cert.add_run(" has been carried out by the following students of Third Year B.Tech. Computer Science and Engineering, Panel E, Batch E2, Group No. ___________, under my guidance during the academic year 2026–2027.\n")

    t_cert = doc.add_table(rows=5, cols=2)
    t_cert.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_cert.cell(0, 0).paragraphs[0].text = "Student Name"
    t_cert.cell(0, 0).paragraphs[0].runs[0].bold = True
    t_cert.cell(0, 1).paragraphs[0].text = "PRN"
    t_cert.cell(0, 1).paragraphs[0].runs[0].bold = True

    for i, s in enumerate(students):
        t_cert.cell(i+1, 0).paragraphs[0].text = s[1]
        t_cert.cell(i+1, 1).paragraphs[0].text = s[2]

    p_cert_end = doc.add_paragraph()
    p_cert_end.paragraph_format.line_spacing = 1.5
    p_cert_end.add_run("\nThe report is submitted towards the mini-project component of Laboratory Continuous Assessment 3 for the Computer Networks Laboratory course (CSE20110).\n\n\n")
    p_cert_end.add_run("Faculty Signature __________________________\n")
    r = p_cert_end.add_run("Mr. Saiprasad Ratankumar\n")
    r.bold = True
    p_cert_end.add_run("Project Guide and Course Faculty\n\n")
    p_cert_end.add_run("Date: 21st October 2026          Place: Pune\n")

    doc.add_page_break()

    # ---------------- ACKNOWLEDGEMENT & ABSTRACT ----------------
    h = doc.add_heading("Acknowledgement", level=1)
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.add_run("We express our sincere and deep gratitude to our project guide and course faculty, Mr. Saiprasad Ratankumar, for his invaluable guidance, continuous encouragement, and constructive technical feedback throughout the design, implementation, and evaluation of this mini-project. His insights into practical network protocols, socket mechanics, and diagnostic methodology were instrumental in the successful completion of this system.\n\n"
              "We also thank the Head of Department, faculty members, and laboratory staff of the Department of Computer Engineering and Technology, MIT World Peace University, Pune, for providing the necessary computing resources, network infrastructure, and stimulating academic environment. We acknowledge the technical resources utilized in this project, notably the standard Internet Engineering Task Force (IETF) RFC specifications, Python networking libraries, Berkeley Socket APIs, and open-source frameworks including Streamlit, FastAPI, and Plotly.\n\n"
              "Group No. ___________")

    doc.add_heading("Abstract", level=1)
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.line_spacing = 1.5
    p_abs.add_run("Network connectivity troubleshooting across modern local area networks, cloud infrastructures, and edge nodes is traditionally a fragmented and cognitively demanding process. Network administrators and end-users frequently execute disparate, uncoordinated command-line utilities such as ipconfig, ping, nslookup, tracert, and curl, failing to systematically correlate cross-layer failure dependencies between the Data Link, Network, Transport, Presentation, and Application layers.\n\n"
                  "This project presents the Network Troubleshooting Assistant (NTA), an autonomous, deterministic, cross-layer diagnostic and root-cause analysis system implemented in Python 3.12. NTA employs an ordered, bottom-up diagnostic engine that systematically evaluates: (1) local network adapter configuration and DHCP addressing; (2) default gateway reachability; (3) dual-stack DNS hostname resolution latency and error typing; (4) remote ICMP reachability; (5) bounded TCP 3-way handshake responsiveness; (6) TLS certificate integrity and HTTP application status; (7) round-trip latency, jitter, and packet loss profiling; and (8) hop-by-hop bounded route tracing. Collected diagnostic evidence is synthesized by a deterministic heuristic inference engine that computes hypothesis confidence scores, isolates root causes, and generates actionable, non-destructive remediation advisories.\n\n"
                  "The system delivers dual operational interfaces via an interactive Streamlit web dashboard and a production-grade FastAPI REST service, backed by SQLite telemetry persistence, automated batch auditing, continuous background scheduled monitoring with multi-channel alerting (Slack, Webhook, Email), and a controlled 10-scenario fault simulation lab. Comprehensive automated testing comprising 23 unit, integration, and simulation benchmarks confirms 100% test passage, proving that NTA effectively bridges the gap between raw networking primitives and rapid, evidence-backed incident resolution.\n\n")
    r_kw = p_abs.add_run("Keywords: ")
    r_kw.bold = True
    p_abs.add_run("Network Diagnostics, Root Cause Analysis, OSI Layered Troubleshooting, Berkeley Sockets, ICMP and TCP Probing, Network Telemetry, Fault Simulation.")

    doc.add_page_break()

    # ---------------- 1 INTRODUCTION ----------------
    doc.add_heading("1 Introduction and Project Objectives", level=1)
    doc.add_heading("1.1 Introduction and Background", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.add_run("Computer networking forms the critical backbone of contemporary computing systems, distributed architectures, and internet communications. The operation of modern interconnected applications relies fundamentally on the layered abstractions formalized by the International Organization for Standardization (ISO) Open Systems Interconnection (OSI) 7-layer reference model and the Internet Engineering Task Force (IETF) TCP/IP protocol suite. Under these architectures, user-facing applications at Layer 7 (Application) depend unconditionally on the sequential integrity of Layer 6 (Presentation), Layer 5 (Session), Layer 4 (Transport), Layer 3 (Network), Layer 2 (Data Link), and Layer 1 (Physical).\n\n"
              "Despite substantial advances in high-speed transmission and automated routing, network failures remain pervasive and heterogeneous. Network degradation can originate from diverse failure modes, including severed physical or wireless links, exhausted Dynamic Host Configuration Protocol (DHCP) lease pools, misconfigured default gateway routes (RFC 1122), Domain Name System (DNS) resolver failures or cache poisoning (RFC 1034, RFC 1035), stateful firewall packet drops (RFC 793), expired Transport Layer Security (TLS) cryptographic certificates (RFC 8446), and application server crashes returning HTTP 5xx responses (RFC 9110).\n\n"
              "Historically, network administrators, site reliability engineers, and end-users diagnose connectivity anomalies by manually invoking low-level, command-line utilities such as ipconfig/ifconfig, ping, nslookup, tracert/traceroute, telnet, and curl. While each utility provides valuable telemetry regarding an isolated parameter, none of these tools provide cross-layer correlation or automated dependency analysis. For example, when a web service fails to load, a user executing a top-down test (such as launching a web browser) cannot discern whether the fault lies in the local Wi-Fi association, an APIPA autoconfiguration address, an unresponsive local gateway, an unresolvable domain name, an intermediate transit router dropping packets, an active firewall dropping TCP SYN packets, or an expired X.509 server certificate.\n\n"
              "Academic literature on automated network management underscores the necessity of deterministic, multi-layered fault isolation. In contrast to speculative heuristics or black-box learning systems that risk hallucinating non-existent network faults, a production-grade diagnostic system must strictly ground its deductions in empirical, low-level network evidence acquired through active socket probing, ICMP packet exchange, and transport-level handshake analysis.")

    doc.add_heading("1.2 Problem Statement", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.add_run("Network troubleshooting in enterprise and edge environments suffers from tool fragmentation, lack of cross-layer correlation, and high cognitive overhead. Existing diagnostic methods force operators to execute multiple disjoint utilities sequentially without an orchestrated methodology, leading to prolonged Mean Time to Resolution (MTTR), erroneous fault attribution, and inaccurate remediation actions.\n\n"
              "There is a compelling need for an autonomous, cross-platform Network Troubleshooting Assistant that systematically validates network health from Layer 2 to Layer 7 in strict hierarchical order, deterministically correlates empirical findings into ranked root-cause hypotheses with confidence metrics, provides non-destructive remediation advisories, supports continuous telemetry monitoring with automated multi-channel alerting, and offers a controlled simulation lab for reproducing complex network anomalies safely.")

    doc.add_heading("1.3 Scope", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.add_run("The scope of this project encompasses:\n"
              "1. Target Environments: Local host operating systems (cross-platform compatibility across Microsoft Windows, Linux, and Apple macOS), local area networks (LANs), default IP gateways, upstream recursive DNS resolvers, and arbitrary remote WAN endpoints specified via Fully Qualified Domain Names (FQDNs), IPv4/IPv6 addresses, or uniform resource locators (URLs).\n"
              "2. Layered Probing Stack: Probing coverage spanning physical network interface discovery, DHCP lease status, local gateway ICMP reachability, dual-stack DNS resolution latency and error typing, destination ICMP reachability, TCP 3-way handshake differentiation (open, closed RST, firewall timeout), TLS certificate validation (expiration, subject alternative name matching), HTTP service health, round-trip latency/jitter profiling, and bounded route tracerouting.\n"
              "3. Operational Boundaries: All diagnostic probes are non-destructive and read-only. The system generates actionable remediation guidance but does not alter operating system routing tables, network adapter parameters, or firewall rules automatically, preserving network safety and avoiding administrative conflicts.\n"
              "4. Enterprise Extensions: Multi-target concurrent batch auditing, continuous background monitoring daemon with configurable telemetry intervals, multi-channel alerting (Slack webhooks, generic ITSM endpoints, SMTP email), Jira ticketing dispatch, and a 10-scenario controlled fault simulation laboratory with isolated synthetic network fixtures.")

    doc.add_heading("1.4 Objectives", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.add_run("The specific engineering objectives and verification criteria are defined in Table 1.1:")

    t_obj = doc.add_table(rows=6, cols=3)
    t_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_obj.cell(0, 0).paragraphs[0].text = "Objective ID"
    t_obj.cell(0, 0).paragraphs[0].runs[0].bold = True
    t_obj.cell(0, 1).paragraphs[0].text = "Objective Statement"
    t_obj.cell(0, 1).paragraphs[0].runs[0].bold = True
    t_obj.cell(0, 2).paragraphs[0].text = "Verification Method"
    t_obj.cell(0, 2).paragraphs[0].runs[0].bold = True

    objs = [
        ("O1", "Implement an ordered, bottom-up 8-stage diagnostic engine probing L2 through L7 network primitives.", "Automated unit and integration test suite executing socket, DNS, ICMP, and TLS probes against local and remote endpoints."),
        ("O2", "Develop a deterministic Heuristic Root-Cause Analysis (RCA) engine with evidence-backed hypothesis ranking.", "Execution against 10 controlled fault scenarios with hidden ground-truth benchmarks in test_scenarios.py."),
        ("O3", "Deliver dual operational interfaces: an interactive Streamlit web dashboard and a production FastAPI REST API.", "Programmatic verification of REST endpoints via TestClient and interactive UI rendering of telemetry and Plotly traceroutes."),
        ("O4", "Engineer continuous background telemetry monitoring with degradation detection and multi-channel alerting.", "Automated verification in test_monitoring_scheduler.py validating state transitions and mock alert dispatch to Slack and Webhooks."),
        ("O5", "Design a controlled 10-scenario fault simulation lab reproducing real-world network anomalies non-destructively.", "Execution of 10 synthetic simulation benchmarks verifying diagnostic accuracy without modifying host network adapters.")
    ]
    for i, row in enumerate(objs):
        t_obj.cell(i+1, 0).paragraphs[0].text = row[0]
        t_obj.cell(i+1, 1).paragraphs[0].text = row[1]
        t_obj.cell(i+1, 2).paragraphs[0].text = row[2]

    doc.save(output_downloads)
    doc.save(output_project)
    print("DOCX generated successfully at:")
    print("  ", output_downloads)
    print("  ", output_project)

if __name__ == '__main__':
    create_report_docx()
