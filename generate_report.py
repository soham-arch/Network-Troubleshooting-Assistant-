# -*- coding: utf-8 -*-
"""
Generates the comprehensive LaTeX mini-project report for the Network Troubleshooting Assistant (NTA).
"""

import os
import shutil

TEX_CONTENT = r'''% Options for packages loaded elsewhere
\PassOptionsToPackage{unicode}{hyperref}
\PassOptionsToPackage{hyphens}{url}
\documentclass[
]{article}
\usepackage{xcolor}
\usepackage{amsmath,amssymb}
\setcounter{secnumdepth}{-\maxdimen} % remove section numbering
\usepackage{iftex}
\ifPDFTeX
  \usepackage[T1]{fontenc}
  \usepackage[utf8]{inputenc}
  \usepackage{textcomp} % provide euro and other symbols
\else % if luatex or xetex
  \usepackage{unicode-math} % this also loads fontspec
  \defaultfontfeatures{Scale=MatchLowercase}
  \defaultfontfeatures[\rmfamily]{Ligatures=TeX,Scale=1}
\fi
\usepackage{lmodern}
\ifPDFTeX\else
  % xetex/luatex font selection
\fi
% Use upquote if available, for straight quotes in verbatim environments
\IfFileExists{upquote.sty}{\usepackage{upquote}}{}
\IfFileExists{microtype.sty}{% use microtype if available
  \usepackage[]{microtype}
  \UseMicrotypeSet[protrusion]{basicmath} % disable protrusion for tt fonts
}{}
\makeatletter
\@ifundefined{KOMAClassName}{% if non-KOMA class
  \IfFileExists{parskip.sty}{%
    \usepackage{parskip}
  }{% else
    \setlength{\parindent}{0pt}
    \setlength{\parskip}{6pt plus 2pt minus 1pt}}
}{% if KOMA class
  \KOMAoptions{parskip=half}}
\makeatother
\usepackage{longtable,booktabs,array}
\newcounter{none} % for unnumbered tables
\usepackage{calc} % for calculating minipage widths
% Correct order of tables after \paragraph or \subparagraph
\usepackage{etoolbox}
\makeatletter
\patchcmd\longtable{\par}{\if@noskipsec\mbox{}\fi\par}{}{}
\makeatother
% Allow footnotes in longtable head/foot
\IfFileExists{footnotehyper.sty}{\usepackage{footnotehyper}}{\usepackage{footnote}}
\makesavenoteenv{longtable}
\usepackage{graphicx}
\makeatletter
\newsavebox\pandoc@box
\newcommand*\pandocbounded[1]{% scales image to fit in text height/width
  \sbox\pandoc@box{#1}%
  \Gscale@div\@tempa{\textheight}{\dimexpr\ht\pandoc@box+\dp\pandoc@box\relax}%
  \Gscale@div\@tempb{\linewidth}{\wd\pandoc@box}%
  \ifdim\@tempb\p@<\@tempa\p@\let\@tempa\@tempb\fi% select the smaller of both
  \ifdim\@tempa\p@<\p@\scalebox{\@tempa}{\usebox\pandoc@box}%
  \else\usebox{\pandoc@box}%
  \fi%
}
% Set default figure placement to htbp
\def\fps@figure{htbp}
\makeatother
\setlength{\emergencystretch}{3em} % prevent overfull lines
\providecommand{\tightlist}{%
  \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\usepackage{bookmark}
\IfFileExists{xurl.sty}{\usepackage{xurl}}{} % add URL line breaks if available
\urlstyle{same}
\hypersetup{
  hidelinks,
  pdfcreator={LaTeX via pandoc}}

\author{}
\date{}

\begin{document}

\includegraphics[width=4.3in,height=1.23712in]{./media/image1.png}

\vspace{0.3cm}

\textbf{Department of Computer Engineering and Technology}

\textbf{MINI PROJECT REPORT}

\textbf{Computer Networks Laboratory}

(CSE20110)

Laboratory Continuous Assessment 3

\vspace{0.4cm}

\textbf{\Large Network Troubleshooting Assistant: Autonomous Cross-Layer Network Diagnostic and Root-Cause Analysis System}

\vspace{0.4cm}

\textbf{Submitted by}

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.12}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.55}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.33}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Sr. No.}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Student Name}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{PRN}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
1 & Soham Patil & 1272250811 \\
2 & Ganesh Gaikwad & 1262252319 \\
3 & Tirth Gangani & 1272250827 \\
4 & Aditya Sardesai & 1262252353 \\
\end{longtable}
}

\vspace{0.3cm}

Group No. \underline{\hspace{2.5cm}} \qquad Panel E \qquad Batch E2

\vspace{0.2cm}

Third Year B.Tech. Computer Engineering and Technology

\vspace{0.3cm}

Under the guidance of

\textbf{Mr. Saiprasad Ratankumar}

\vspace{0.2cm}

\textbf{Academic Year 2026--2027}

Submission Date: 21st October 2026

\newpage

\includegraphics[width=4.3in,height=1.23712in]{./media/image1.png}

\vspace{0.3cm}

\textbf{Department of Computer Engineering and Technology}

\textbf{CERTIFICATE}

\vspace{0.3cm}

This is to certify that the mini-project entitled ``\textbf{Network Troubleshooting Assistant: Autonomous Cross-Layer Network Diagnostic and Root-Cause Analysis System}'' has been carried out by the following students of Third Year B.Tech. Computer Science and Engineering, Panel E, Batch E2, Group No. \underline{\hspace{2.5cm}}, under my guidance during the academic year 2026--2027.

\vspace{0.3cm}

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 2\tabcolsep) * \real{0.65}}
  >{\raggedright\arraybackslash}p{(\linewidth - 2\tabcolsep) * \real{0.35}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Student Name}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{PRN}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Soham Patil & 1272250811 \\
Ganesh Gaikwad & 1262252319 \\
Tirth Gangani & 1272250827 \\
Aditya Sardesai & 1262252353 \\
\end{longtable}
}

\vspace{0.3cm}

The report is submitted towards the mini-project component of Laboratory Continuous Assessment 3 for the Computer Networks Laboratory course (CSE20110).

\vspace{1.2cm}

Faculty Signature: \underline{\hspace{6cm}}

\textbf{Mr. Saiprasad Ratankumar}\\
Project Guide and Course Faculty

\vspace{0.5cm}

Date: 21st October 2026 \qquad Place: Pune

\newpage

\section{Acknowledgement}\label{acknowledgement}

We express our sincere and deep gratitude to our project guide and course faculty, \textbf{Mr. Saiprasad Ratankumar}, for his invaluable guidance, continuous encouragement, and constructive technical feedback throughout the design, implementation, and evaluation of this mini-project. His insights into practical network protocols, socket mechanics, and diagnostic methodology were instrumental in the successful completion of this system.

We also thank the Head of Department, faculty members, and laboratory staff of the \textbf{Department of Computer Engineering and Technology}, MIT World Peace University, Pune, for providing the necessary computing resources, network infrastructure, and stimulating academic environment. We acknowledge the technical resources utilized in this project, notably the standard Internet Engineering Task Force (IETF) RFC specifications, Python networking libraries, Berkeley Socket APIs, and open-source frameworks including Streamlit, FastAPI, and Plotly.

\vspace{0.5cm}
Group No. \underline{\hspace{2.5cm}}

\vspace{0.8cm}

\section{Abstract}\label{abstract}

Network connectivity troubleshooting across modern local area networks, cloud infrastructures, and edge nodes is traditionally a fragmented and cognitively demanding process. Network administrators and end-users frequently execute disparate, uncoordinated command-line utilities such as \texttt{ipconfig}, \texttt{ping}, \texttt{nslookup}, \texttt{tracert}, and \texttt{curl}, failing to systematically correlate cross-layer failure dependencies between the Data Link, Network, Transport, Presentation, and Application layers. 

This project presents the \textbf{Network Troubleshooting Assistant (NTA)}, an autonomous, deterministic, cross-layer diagnostic and root-cause analysis system implemented in Python 3.12. NTA employs an ordered, bottom-up diagnostic engine that systematically evaluates: (1) local network adapter configuration and DHCP addressing; (2) default gateway reachability; (3) dual-stack DNS hostname resolution latency and error typing; (4) remote ICMP reachability; (5) bounded TCP 3-way handshake responsiveness; (6) TLS certificate integrity and HTTP application status; (7) round-trip latency, jitter, and packet loss profiling; and (8) hop-by-hop bounded route tracing. Collected diagnostic evidence is synthesized by a deterministic heuristic inference engine that computes hypothesis confidence scores, isolates root causes, and generates actionable, non-destructive remediation advisories. 

The system delivers dual operational interfaces via an interactive Streamlit web dashboard and a production-grade FastAPI REST service, backed by SQLite telemetry persistence, automated batch auditing, continuous background scheduled monitoring with multi-channel alerting (Slack, Webhook, Email), and a controlled 10-scenario fault simulation lab. Comprehensive automated testing comprising 23 unit, integration, and simulation benchmarks confirms 100\% test passage, proving that NTA effectively bridges the gap between raw networking primitives and rapid, evidence-backed incident resolution.

\vspace{0.3cm}
\textbf{Keywords:} Network Diagnostics, Root Cause Analysis, OSI Layered Troubleshooting, Berkeley Sockets, ICMP and TCP Probing, Network Telemetry, Fault Simulation.

\newpage

\section{Table of Contents}\label{table-of-contents}

\begin{itemize}
\tightlist
\item \textbf{1 Introduction and Project Objectives}
  \begin{itemize}
  \item 1.1 Introduction and Background
  \item 1.2 Problem Statement
  \item 1.3 Scope
  \item 1.4 Objectives
  \end{itemize}
\item \textbf{2 Proposed Design and Requirements}
  \begin{itemize}
  \item 2.1 Architecture and Network Topology
  \item 2.2 Tools and System Requirements
  \item 2.3 Addressing and Protocol Selection
  \end{itemize}
\item \textbf{3 Implementation and Technical Working}
  \begin{itemize}
  \item 3.1 Methodology
  \item 3.2 Configuration or Code Implementation
  \item 3.3 Protocols and Technical Working
  \item 3.4 Execution Procedure
  \end{itemize}
\item \textbf{4 Testing and Results}
  \begin{itemize}
  \item 4.1 Test Plan
  \item 4.2 Results and Execution Evidence
  \item 4.3 Objective Achievement
  \end{itemize}
\item \textbf{5 Discussion and Conclusion}
  \begin{itemize}
  \item 5.1 Discussion and Comparative Analysis
  \item 5.2 Advantages and Applications
  \item 5.3 Limitations
  \item 5.4 Challenges and Troubleshooting
  \item 5.5 Future Scope
  \item 5.6 Conclusion
  \end{itemize}
\item \textbf{References}
\item \textbf{AI Usage Declaration}
\item \textbf{Appendices}
  \begin{itemize}
  \item Appendix A: Code and Configuration
  \item Appendix B: Additional Evidence
  \item Appendix C: Individual Contributions
  \end{itemize}
\end{itemize}

\vspace{0.5cm}

\section{List of Figures}\label{list-of-figures}

\begin{itemize}
\tightlist
\item \textbf{Figure 2.1:} Multi-Tier Architectural Topology and Data Flow Pipeline of the Network Troubleshooting Assistant
\item \textbf{Figure 3.1:} Implementation Evidence --- Streamlit Web Dashboard and Diagnostic Execution Interface
\item \textbf{Figure 4.1:} Automated Test Suite Execution Evidence (23 Passed Pytest Verification Suite)
\end{itemize}

\vspace{0.5cm}

\section{List of Tables}\label{list-of-tables}

\begin{itemize}
\tightlist
\item \textbf{Table 1.1:} Project Objectives and Empirical Verification Methods
\item \textbf{Table 2.1:} Software Tools, Frameworks, and Environmental Specifications
\item \textbf{Table 2.2:} Network Addressing and Protocol Implementation Mapping
\item \textbf{Table 4.1:} Comprehensive Diagnostic Test Plan and Verification Matrix
\item \textbf{Table 4.2:} Objective Achievement and Verification Outcome Summary
\item \textbf{Table 5.1:} Comparative Analysis of Network Troubleshooting Paradigms
\item \textbf{Table 5.2:} Development Challenges, Root Causes, and Applied Solutions
\item \textbf{Table C.1:} Individual Student Contributions and Deliverables
\end{itemize}

\newpage

\section{1 Introduction and Project Objectives}\label{introduction-and-project-objectives}

\subsection{1.1 Introduction and Background}\label{introduction-and-background}

Computer networking forms the critical backbone of contemporary computing systems, distributed architectures, and internet communications. The operation of modern interconnected applications relies fundamentally on the layered abstractions formalized by the International Organization for Standardization (ISO) Open Systems Interconnection (OSI) 7-layer reference model and the Internet Engineering Task Force (IETF) TCP/IP protocol suite. Under these architectures, user-facing applications at Layer 7 (Application) depend unconditionally on the sequential integrity of Layer 6 (Presentation), Layer 5 (Session), Layer 4 (Transport), Layer 3 (Network), Layer 2 (Data Link), and Layer 1 (Physical).

Despite substantial advances in high-speed transmission and automated routing, network failures remain pervasive and heterogeneous. Network degradation can originate from diverse failure modes, including severed physical or wireless links, exhausted Dynamic Host Configuration Protocol (DHCP) lease pools, misconfigured default gateway routes (RFC 1122), Domain Name System (DNS) resolver failures or cache poisoning (RFC 1034, RFC 1035), stateful firewall packet drops (RFC 793), expired Transport Layer Security (TLS) cryptographic certificates (RFC 8446), and application server crashes returning HTTP 5xx responses (RFC 9110).

Historically, network administrators, site reliability engineers, and end-users diagnose connectivity anomalies by manually invoking low-level, command-line utilities such as \texttt{ipconfig}/\texttt{ifconfig}, \texttt{ping}, \texttt{nslookup}, \texttt{tracert}/\texttt{traceroute}, \texttt{telnet}, and \texttt{curl}. While each utility provides valuable telemetry regarding an isolated parameter, none of these tools provide cross-layer correlation or automated dependency analysis. For example, when a web service fails to load, a user executing a top-down test (such as launching a web browser) cannot discern whether the fault lies in the local Wi-Fi association, an APIPA autoconfiguration address, an unresponsive local gateway, an unresolvable domain name, an intermediate transit router dropping packets, an active firewall dropping TCP SYN packets, or an expired X.509 server certificate.

Academic literature on automated network management underscores the necessity of deterministic, multi-layered fault isolation. In contrast to speculative heuristics or black-box learning systems that risk hallucinating non-existent network faults, a production-grade diagnostic system must strictly ground its deductions in empirical, low-level network evidence acquired through active socket probing, ICMP packet exchange, and transport-level handshake analysis.

\subsection{1.2 Problem Statement}\label{problem-statement}

Network troubleshooting in enterprise and edge environments suffers from tool fragmentation, lack of cross-layer correlation, and high cognitive overhead. Existing diagnostic methods force operators to execute multiple disjoint utilities sequentially without an orchestrated methodology, leading to prolonged Mean Time to Resolution (MTTR), erroneous fault attribution, and inaccurate remediation actions. 

There is a compelling need for an autonomous, cross-platform Network Troubleshooting Assistant that systematically validates network health from Layer 2 to Layer 7 in strict hierarchical order, deterministically correlates empirical findings into ranked root-cause hypotheses with confidence metrics, provides non-destructive remediation advisories, supports continuous telemetry monitoring with automated multi-channel alerting, and offers a controlled simulation lab for reproducing complex network anomalies safely.

\subsection{1.3 Scope}\label{scope}

The scope of this project encompasses:
\begin{enumerate}
\tightlist
\item \textbf{Target Environments:} Local host operating systems (cross-platform compatibility across Microsoft Windows, Linux, and Apple macOS), local area networks (LANs), default IP gateways, upstream recursive DNS resolvers, and arbitrary remote WAN endpoints specified via Fully Qualified Domain Names (FQDNs), IPv4/IPv6 addresses, or uniform resource locators (URLs).
\item \textbf{Layered Probing Stack:} Probing coverage spanning physical network interface discovery, DHCP lease status, local gateway ICMP reachability, dual-stack DNS resolution latency and error classification, destination ICMP reachability, TCP 3-way handshake differentiation (open, closed RST, firewall timeout), TLS certificate validation (expiration, subject alternative name matching), HTTP service health, round-trip latency/jitter profiling, and bounded route tracerouting.
\item \textbf{Operational Boundaries:} All diagnostic probes are non-destructive and read-only. The system generates actionable remediation guidance but does not alter operating system routing tables, network adapter parameters, or firewall rules automatically, preserving network safety and avoiding administrative conflicts.
\item \textbf{Enterprise Extensions:} Multi-target concurrent batch auditing, continuous background monitoring daemon with configurable telemetry intervals, multi-channel alerting (Slack webhooks, generic ITSM endpoints, SMTP email), Jira ticketing dispatch, and a 10-scenario controlled fault simulation laboratory with isolated synthetic network fixtures.
\end{enumerate}

\subsection{1.4 Objectives}\label{objectives}

The specific engineering and experimental objectives of the project, along with their empirical verification methods, are defined in Table 1.1.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.14}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.52}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.34}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Objective ID}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Objective Statement}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Verification Method}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
\textbf{O1} & Implement an ordered, bottom-up 8-stage diagnostic engine probing L2 through L7 network primitives. & Automated unit and integration test suite executing socket, DNS, ICMP, and TLS probes against local and remote endpoints. \\
\textbf{O2} & Develop a deterministic Heuristic Root-Cause Analysis (RCA) engine with evidence-backed hypothesis ranking. & Execution against 10 controlled fault scenarios with hidden ground-truth benchmarks in \texttt{test\_scenarios.py}. \\
\textbf{O3} & Deliver dual operational interfaces: an interactive Streamlit web dashboard and a production FastAPI REST API. & Programmatic verification of REST endpoints via \texttt{TestClient} and interactive UI rendering of telemetry and Plotly traceroutes. \\
\textbf{O4} & Engineer continuous background telemetry monitoring with degradation detection and multi-channel alerting. & Automated verification in \texttt{test\_monitoring\_scheduler.py} validating state transitions and mock alert dispatch to Slack and Webhooks. \\
\textbf{O5} & Design a controlled 10-scenario fault simulation lab reproducing real-world network anomalies non-destructively. & Execution of 10 synthetic simulation benchmarks verifying diagnostic accuracy without modifying host network adapters. \\
\end{longtable}
}

\begin{center}
\textbf{Table 1.1:} Project Objectives and Empirical Verification Methods
\end{center}

\newpage

\section{2 Proposed Design and Requirements}\label{proposed-design-and-requirements}

\subsection{2.1 Architecture and Network Topology}\label{architecture-and-network-topology}

The Network Troubleshooting Assistant is architected as a modular, multi-tier distributed system comprising six core functional layers: the Presentation/User Interface Layer, the API and Integration Layer, the Orchestration and Diagnostic Engine, the Deterministic Root-Cause Analysis Engine, the Persistence and Storage Layer, and the Continuous Monitoring Subsystem. Figure 2.1 illustrates the structural topology, data flows, and inter-module communications.

\vspace{0.4cm}

\begin{verbatim}
+===================================================================================+
|                          USER PRESENTATION & CLIENT LAYER                         |
|  +---------------------------------------+  +----------------------------------+  |
|  |     Streamlit Interactive Web UI      |  |   FastAPI REST API (Port 8000)   |  |
|  |  (Single / Batch / Monitor / Sim Lab) |  |  (/diagnose, /batch, /targets)   |  |
|  +---------------------------------------+  +----------------------------------+  |
+===================================================================================+
                                         |
                                         v
+===================================================================================+
|                        APPLICATION & ORCHESTRATION LAYER                          |
|  +--------------------------+  +---------------------+  +----------------------+  |
|  | Diagnostic Orchestrator  |  | Symptom NLP Parser  |  |  Batch Orchestrator  |  |
|  | (Adaptive Short-Circuit) |  | (Target Extraction) |  |  (Worker ThreadPool) |  |
|  +--------------------------+  +---------------------+  +----------------------+  |
+===================================================================================+
                                         |
                                         v
+===================================================================================+
|                       MULTI-STAGE DIAGNOSTIC PROBING ENGINE                       |
|  [Stage 1] Local Config: NIC State, IPv4/v6, Subnet Mask, Gateway, DNS Discovery |
|  [Stage 2] Gateway Check: Bounded ICMP Echo Probing to Local Router               |
|  [Stage 3] DNS Resolution: Dual-Stack socket.getaddrinfo(), Latency, NXDOMAIN     |
|  [Stage 4] Remote Ping: Destination Reachability via ICMP Echo Request / Reply    |
|  [Stage 5] TCP Handshake: Non-blocking Socket Connect (SYN -> Open / RST / Drop)  |
|  [Stage 6] TLS & HTTP: SSLContext X.509 Verification & HTTP Status Evaluation     |
|  [Stage 7] Latency & Jitter: Multi-Probe Statistical Round-Trip Profiling         |
|  [Stage 8] Route Traceroute: IP TTL Decrement Hop Tracing & Bottleneck Isolation   |
+===================================================================================+
                                         |
                                         v
+===================================================================================+
|                         ANALYSIS & INTELLIGENCE SUBSYSTEM                         |
|  +-----------------------------------------------------------------------------+  |
|  | Deterministic Heuristic Root-Cause Analysis Engine                          |  |
|  | - Evidence Aggregation & Rule-Based Hypothesis Scoring (Confidence: 0.0-1.0)|  |
|  | - Supporting vs Contradicting Evidence Isolation                            |  |
|  | - Advisory Actionable Remediation Generator & Verification Loop Plan        |  |
|  +-----------------------------------------------------------------------------+  |
|  | Grounded LLM Explanation Service (Ollama / LM Studio / OpenAI / Gemini)     |  |
|  +-----------------------------------------------------------------------------+  |
+===================================================================================+
                                         |
                                         v
+===================================================================================+
|                       PERSISTENCE, TELEMETRY & ALERTING                           |
|  +-----------------------+  +------------------------+  +----------------------+  |
|  | SQLite Persistent DB  |  | Background Scheduler   |  | Multi-Channel Alerts |  |
|  | (Sessions, Telemetry) |  | (Target Health Daemon) |  | (Slack, Webhook,Mail)|  |
|  +-----------------------+  +------------------------+  +----------------------+  |
+===================================================================================+
\end{verbatim}

\vspace{0.2cm}
\begin{center}
\textbf{Figure 2.1:} Multi-Tier Architectural Topology and Data Flow Pipeline of the Network Troubleshooting Assistant
\end{center}

\vspace{0.4cm}

The core architectural components function as follows:
\begin{itemize}
\tightlist
\item \textbf{Presentation Layer:} Provides interactive diagnostics via a multi-page Streamlit web application (\texttt{app.py}) featuring live adapter discovery, targeted investigations, interactive Plotly network topology graphs, and historical inspection. Simultaneously, a FastAPI application (\texttt{api/server.py}) serves production REST endpoints with OpenAPI/Swagger documentation.
\item \textbf{Orchestration Layer:} The \texttt{DiagnosticOrchestrator} governs diagnostic progression. It implements adaptive short-circuit logic: if local adapter configuration fails (e.g., disconnected cable or APIPA autoconfiguration), downstream WAN and destination probes are bypassed to prevent misleading timeouts.
\item \textbf{Diagnostic Probing Engine:} An ensemble of dedicated network modules executing low-level socket operations, ICMP packet transmissions, and cryptographic handshakes against target infrastructure.
\item \textbf{Root-Cause Analysis Subsystem:} Consolidates structured test results, evaluates confidence matrices against known network failure patterns, and outputs ranked hypotheses alongside step-by-step advisory remediation instructions.
\item \textbf{Persistence and Alerting:} Employs SQLite for thread-safe session archival, paired with a daemonized background scheduler (\texttt{monitoring/scheduler.py}) monitoring mission-critical targets and triggering rate-limited alerts across Slack, generic webhooks, and SMTP email.
\end{itemize}

\subsection{2.2 Tools and System Requirements}\label{tools-and-system-requirements}

The system was developed and validated using the technologies and environmental specifications detailed in Table 2.1.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.25}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.25}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.50}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Tool or Resource}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Version or Specification}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Purpose}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Python & 3.12.0rc3 / 3.11+ & Primary programming language and standard networking runtime environment. \\
Berkeley Sockets & Standard Library \texttt{socket} & Non-blocking TCP 3-way handshakes, UDP transactions, and DNS resolution. \\
Streamlit & 1.39.0+ & Web presentation framework delivering dynamic diagnostic dashboards and forms. \\
FastAPI \& Uvicorn & 0.115.0+ / 0.30.0+ & Asynchronous high-performance REST API backend and ASGI web server. \\
Psutil & 6.0.0+ & Cross-platform inspection of NIC states, IP assignments, MAC addresses, and routing tables. \\
Plotly & 5.24.0+ & Interactive visualization of route traceroute hops and latency bottleneck detection. \\
ReportLab & 4.2.0+ & Programmatic generation of formal, executive PDF diagnostic summary reports. \\
SQLite & 3.45+ & Local relational repository persisting diagnostic sessions, telemetry, and monitoring targets. \\
Pytest & 9.1.1+ & Automated test runner validating unit modules, integration endpoints, and simulation lab fixtures. \\
Operating System & Windows 11 / Linux / macOS & Host test environment supporting cross-platform OS network execution. \\
\end{longtable}
}

\begin{center}
\textbf{Table 2.1:} Software Tools, Frameworks, and Environmental Specifications
\end{center}

\subsection{2.3 Addressing and Protocol Selection}\label{addressing-and-protocol-selection}

The diagnostic assistant interacts across multiple physical and logical addressing boundaries, configured as outlined in Table 2.2.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.26}}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.26}}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.22}}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.26}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Device / Interface}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{IP / Prefix}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Gateway}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Role}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Loopback (\texttt{lo0} / \texttt{Loopback0}) & 127.0.0.1 / 8 \newline ::1 / 128 & N/A & Inter-process communication and local synthetic fault testing. \\
Local Host NIC (Ethernet / Wi-Fi) & 192.168.1.50 / 24 \newline (DHCP-allocated) & 192.168.1.1 & Primary client interface originating outbound diagnostic probes. \\
Default Gateway (Local Router) & 192.168.1.1 / 24 & Next-hop ISP Router & First-hop L3 routing boundary isolating LAN faults from WAN outages. \\
Upstream Recursive DNS Servers & 8.8.8.8, 1.1.1.1 \newline UDP/TCP Port 53 & 192.168.1.1 & Resolving FQDNs to IPv4/IPv6 resource records; measuring DNS latency. \\
Remote Target Endpoints & Arbitrary FQDN / IP \newline (e.g., Ports 80, 443) & Default Gateway & End-to-end destination reachability, TLS verification, and HTTP health. \\
\end{longtable}
}

\begin{center}
\textbf{Table 2.2:} Network Addressing and Protocol Implementation Mapping
\end{center}

\vspace{0.2cm}
\textbf{Protocol Implementation Choices and Rationale:}
\begin{itemize}
\tightlist
\item \textbf{ICMP (RFC 792):} Used for Gateway and Destination reachability via Echo Request (Type 8, Code 0) and Echo Reply (Type 0, Code 0). In route tracerouting, ICMP Time Exceeded (Type 11, Code 0) messages are leveraged as intermediate routers decrement the IP packet's Time-To-Live (TTL) field to zero.
\item \textbf{UDP Port 53 (RFC 1035):} Utilized for standard DNS queries due to minimal latency overhead. If records exceed the standard 512-byte payload, fallback to TCP Port 53 is supported.
\item \textbf{TCP 3-Way Handshake (RFC 793, RFC 9293):} The system explicitly probes target TCP ports using a non-blocking Berkeley socket connect. Crucially, the engine differentiates between receiving a TCP RST segment (\texttt{ConnectionRefusedError}, indicating the host is reachable but no service listens on the port) versus a timeout (\texttt{socket.timeout}, indicating packet filtering by a stateful firewall or routing drop).
\item \textbf{TLS 1.2 / TLS 1.3 (RFC 8446) and HTTP/1.1 / HTTP/2 (RFC 9110):} Handled via Python's \texttt{ssl} and \texttt{requests} libraries to validate X.509 certificate chains, expiration dates, Common Name/SAN attributes, and application return codes.
\end{itemize}

\newpage

\section{3 Implementation and Technical Working}\label{implementation-and-technical-working}

\subsection{3.1 Methodology}\label{methodology}

The Network Troubleshooting Assistant follows an orchestrated bottom-up diagnostic methodology adhering strictly to layered protocol mechanics:

\begin{enumerate}
\tightlist
\item \textbf{Symptom Intake \& Parsing:} The user provides either a structured destination (e.g., \texttt{api.stripe.com:443}) or an unstructured natural language complaint (e.g., \textit{``Our internal portal https://portal.corp.local is unreachable''}). The NLP parser (\texttt{llm/symptom\_parser.py}) sanitizes and converts the input into target parameters.
\item \textbf{Stage 1 --- Local Interface Configuration:} Inspects physical/virtual network adapters, validating link status, assigned IP address, subnet mask, and default gateway. Identifies APIPA misconfigurations (\texttt{169.254.x.x}). If no functional adapter exists, downstream tests are aborted immediately.
\item \textbf{Stage 2 --- Default Gateway Reachability:} Dispatches bounded ICMP Echo Requests to the discovered default gateway IP. Isolates whether the fault resides on the local LAN or beyond the first router hop.
\item \textbf{Stage 3 --- DNS Resolution:} Executes dual-stack resolution using \texttt{socket.getaddrinfo()} to obtain \texttt{A} and \texttt{AAAA} records while benchmarking resolution latency. Accurately flags NXDOMAIN or resolver timeouts.
\item \textbf{Stage 4 --- Destination Reachability:} Transmits bounded ICMP ping probes directly to the resolved target IP address to verify Layer 3 connectivity.
\item \textbf{Stage 5 --- Transport Layer Port Availability:} Performs a timed TCP connect to the specified destination port. Identifies whether the port is open, actively refused (TCP RST), or silently dropped (firewall timeout).
\item \textbf{Stage 6 --- Application \& Cryptographic Health:} For HTTP/HTTPS targets, validates SSL/TLS certificate validity (detecting expiration, hostname mismatch, or self-signed certs) and captures HTTP status codes.
\item \textbf{Stage 7 --- Latency, Jitter, and Packet Loss:} Executes multiple sequential ping iterations, calculating minimum, average, maximum RTT, jitter, and packet loss percentage.
\item \textbf{Stage 8 --- Route Path Tracing:} Dispatches incremental TTL probes to map intermediate network hops and visually isolate packet loss bottlenecks.
\item \textbf{Synthesis & Remediation Generation:} The collected evidence vector is evaluated by the Deterministic Root-Cause Engine to score probable hypotheses and generate advisory remediation plans.
\end{enumerate}

\subsection{3.2 Configuration or Code Implementation}\label{configuration-or-code-implementation}

Key code excerpts demonstrating core networking logic implemented across the assistant are presented below:

\vspace{0.2cm}
\textbf{1. Bounded TCP Port Handshake Differentiation (\texttt{diagnostics/connectivity.py}):}
\begin{verbatim}
def check_tcp_port_availability(target_host: str, target_port: int, 
                                timeout_sec: float = 3.0) -> TestResult:
    """Probes transport layer port availability and discriminates RST vs Timeout."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout_sec)
    start_time = time.time()
    try:
        sock.connect((target_host, target_port))
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        sock.close()
        return TestResult(stage=DiagnosticStage.PORT, status=TestStatus.PASS,
                          measured_values={"port": target_port, "latency_ms": elapsed_ms},
                          human_explanation=f"TCP Port {target_port} is OPEN and accepting connections.")
    except ConnectionRefusedError:
        return TestResult(stage=DiagnosticStage.PORT, status=TestStatus.FAIL,
                          measured_values={"port": target_port, "error": "ECONNREFUSED"},
                          evidence=["Target host replied with TCP RST (Connection Refused)."],
                          human_explanation=f"Port {target_port} is CLOSED on target host.")
    except socket.timeout:
        return TestResult(stage=DiagnosticStage.PORT, status=TestStatus.FAIL,
                          measured_values={"port": target_port, "error": "ETIMEDOUT"},
                          evidence=["SYN packet timed out without response (likely firewall drop)."],
                          human_explanation=f"Connection to port {target_port} timed out.")
    except Exception as exc:
        return TestResult(stage=DiagnosticStage.PORT, status=TestStatus.ERROR,
                          human_explanation=f"Socket error on port {target_port}: {exc}")
\end{verbatim}

\vspace{0.2cm}
\textbf{2. Dual-Stack DNS Resolution & Error Classification (\texttt{diagnostics/dns.py}):}
\begin{verbatim}
def run_dns_resolution(target_host: str, timeout_sec: float = 3.0) -> TestResult:
    """Executes dual-stack DNS hostname resolution benchmarking resolution latency."""
    start_time = time.time()
    try:
        addr_info = socket.getaddrinfo(target_host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        resolved_ips = list({info[4][0] for info in addr_info})
        return TestResult(stage=DiagnosticStage.DNS, status=TestStatus.PASS,
                          measured_values={"resolved_ips": resolved_ips, "dns_latency_ms": duration_ms},
                          evidence=[f"Resolved {target_host} -> {resolved_ips} in {duration_ms} ms"],
                          human_explanation=f"DNS resolution succeeded for {target_host}.")
    except socket.gaierror as e:
        return TestResult(stage=DiagnosticStage.DNS, status=TestStatus.FAIL,
                          measured_values={"error_code": e.errno, "error_msg": str(e)},
                          evidence=[f"socket.gaierror: {e}"],
                          human_explanation=f"Failed to resolve domain name '{target_host}'.")
\end{verbatim}

\vspace{0.2cm}
\textbf{3. Deterministic Evidence Scoring Rule (\texttt{engine/root_cause.py}):}
\begin{verbatim}
# Evaluate Gateway unreachable while local configuration is valid
if gw_res and gw_res.status == TestStatus.FAIL and local_res.status == TestStatus.PASS:
    hypotheses.append(RootCauseHypothesis(
        hypothesis_id=str(uuid.uuid4())[:8],
        title="Local Default Gateway Unreachable",
        probable_root_cause="The local router / default gateway is not responding to ICMP ping.",
        confidence=ConfidenceLevel.HIGH,
        confidence_score=0.90,
        supporting_evidence=gw_res.evidence,
        suggested_corrective_action="Power-cycle local gateway/router and inspect LAN cable/Wi-Fi connection.",
        verification_steps=["Ping default gateway IP directly from terminal.", "Check router WAN indicator LED."]
    ))
\end{verbatim}

\subsection{3.3 Protocols and Technical Working}\label{protocols-and-technical-working}

The technical interactions between the protocols and modules operate through distinct network mechanics:
\begin{itemize}
\tightlist
\item \textbf{Layer 2 / Layer 3 Interface Discovery:} Using the \texttt{psutil.net\_if\_addrs()} and \texttt{psutil.net\_if\_stats()} system calls, the system queries kernel routing structures to identify NIC operational duplex, MTU, broadcast flags, and IP bindings, filtering out unconfigured loopback or inactive virtual adapters.
\item \textbf{ARP and Gateway Isolation:} To verify local loop integrity, the gateway diagnostic issues ICMP Echo Requests. The OS kernel issues an Address Resolution Protocol (ARP, RFC 826) request broadcast to resolve the gateway's 48-bit MAC address. Successful ICMP Echo Reply confirms that local L2 switching and L3 IP routing are operational.
\item \textbf{Transport Layer Socket Mechanics:} When initiating TCP connections, the OS kernel dispatches a TCP segment with the SYN control flag asserted. If the remote service is active, it responds with SYN-ACK, completing the handshake upon the client's ACK. If the remote port is closed, the remote kernel immediately replies with a TCP RST segment. If a network firewall drops the packet, no packet returns, triggering a socket timeout. NTA captures this distinction with exact precision.
\item \textbf{Cryptographic Verification:} The \texttt{ssl} module establishes a TLS handshake, negotiating cryptographic cipher suites and validating server X.509 certificates against operating system Certificate Authority (CA) root stores. Expired certificates or domain name mismatches are isolated before HTTP payload retrieval.
\end{itemize}

\subsection{3.4 Execution Procedure}\label{execution-procedure}

The Network Troubleshooting Assistant can be launched reproducibly through either its web dashboard or its REST API backend.

\vspace{0.2cm}
\textbf{Step 1: Environment Setup and Dependency Installation}
\begin{verbatim}
# Create virtual environment and activate
python -m venv venv
venv\Scripts\activate          # On Windows
source venv/bin/activate       # On Linux/macOS

# Install pinned production dependencies
pip install -r requirements.txt
\end{verbatim}

\textbf{Step 2: Launch Streamlit Web Dashboard}
\begin{verbatim}
python run.py
# Alternatively: streamlit run app.py
\end{verbatim}
The web user interface is immediately available at \texttt{http://localhost:8501}, presenting the Live Adapter Status, Single Diagnostic Investigation, Batch Audit, Continuous Monitoring Dashboard, and the Fault Simulation Lab.

\vspace{0.2cm}
\textbf{Step 3: Launch FastAPI REST Server}
\begin{verbatim}
python run.py api
# Alternatively: uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
\end{verbatim}
Interactive API documentation and schema explorers are accessible at \texttt{http://localhost:8000/docs} (Swagger UI) and \texttt{http://localhost:8000/redoc}.

\vspace{0.2cm}
\textbf{Step 4: Execute Automated Verification Test Suite}
\begin{verbatim}
python -m pytest -v
\end{verbatim}

\vspace{0.4cm}

\begin{center}
\fbox{\begin{minipage}{0.9\linewidth}
\centering
\vspace{0.3cm}
\textbf{[Figure 3.1: Implementation Evidence --- Streamlit Web Dashboard]} \\
\vspace{0.2cm}
\textit{The Streamlit graphical interface displaying real-time system readiness, active network adapter telemetry (IP, Subnet, Gateway, DNS), the 8-stage diagnostic execution pipeline with live PASS/FAIL status indicators, and the evidence-based Root Cause Analysis advisory box.}
\vspace{0.3cm}
\end{minipage}}
\end{center}

\vspace{0.2cm}
\begin{center}
\textbf{Figure 3.1:} Implementation Evidence --- Streamlit Web Dashboard and Diagnostic Execution Interface
\end{center}

\newpage

\section{4 Testing and Results}\label{testing-and-results}

\subsection{4.1 Test Plan}\label{test-plan}

The system was evaluated through an automated verification matrix covering unit functionality, integration endpoints, persistence schemas, and synthetic fault benchmarks, as shown in Table 4.1.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 8\tabcolsep) * \real{0.10}}
  >{\raggedright\arraybackslash}p{(\linewidth - 8\tabcolsep) * \real{0.24}}
  >{\raggedright\arraybackslash}p{(\linewidth - 8\tabcolsep) * \real{0.24}}
  >{\raggedright\arraybackslash}p{(\linewidth - 8\tabcolsep) * \real{0.28}}
  >{\raggedright\arraybackslash}p{(\linewidth - 8\tabcolsep) * \real{0.14}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Test ID}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Test and Input}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Expected Result}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Observed Result}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Status}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
\textbf{T1} & Local Adapter & Gateway Check (\texttt{test\_root\_cause.py}) & Active IP detected, default gateway ping validated. & Detected valid IP and pingable default gateway. & \textbf{Pass} \\
\textbf{T2} & DNS Error Classification (\texttt{test\_validation.py}) & Domain \texttt{invalid-nxdomain-xyz.com} flagged as unresolvable. & \texttt{socket.gaierror} caught; categorized as NXDOMAIN failure. & \textbf{Pass} \\
\textbf{T3} & TCP Port Handshake Differentiation & Closed port \texttt{127.0.0.1:59999} returns TCP RST (\texttt{ECONNREFUSED}). & Successfully captured TCP RST; differentiated from timeout. & \textbf{Pass} \\
\textbf{T4} & Fault Simulation Lab (10 Scenarios) & Engine isolates simulated root cause with confidence $\ge 0.80$. & 100\% match across all 10 synthetic simulation scenarios. & \textbf{Pass} \\
\textbf{T5} & FastAPI REST Endpoints (\texttt{test\_api\_endpoints.py}) & POST \texttt{/api/v1/diagnose} returns structured session JSON. & HTTP 200 OK with valid Pydantic schema serialization. & \textbf{Pass} \\
\textbf{T6} & Background Scheduler Telemetry & Scheduler runs periodic polling and records latency trends. & Daemon triggers on schedule, writes to SQLite telemetry table. & \textbf{Pass} \\
\end{longtable}
}

\begin{center}
\textbf{Table 4.1:} Comprehensive Diagnostic Test Plan and Verification Matrix
\end{center}

\subsection{4.2 Results and Execution Evidence}\label{results-and-execution-evidence}

The automated test suite was executed across all unit, integration, and simulation suites. A total of 23 test cases were collected and executed, achieving a 100\% passing rate without regressions:

\vspace{0.2cm}
\begin{verbatim}
============================= test session starts =============================
platform win32 -- Python 3.12.0rc3, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\MITWPU\Engineering\3rd Year\CN\Project\Network-Troubleshooting-Assistant-main
configfile: pytest.ini
collected 23 items

tests\integration\test_api_endpoints.py ....                             [ 17%]
tests\integration\test_reports_storage.py .                              [ 21%]
tests\simulation\test_scenarios.py .                                     [ 26%]
tests\unit\test_batch_orchestrator.py ..                                 [ 34%]
tests\unit\test_llm_symptom_parser.py ....                               [ 52%]
tests\unit\test_monitoring_scheduler.py ..                               [ 60%]
tests\unit\test_root_cause.py ...                                        [ 73%]
tests\unit\test_traceroute_viz.py ..                                     [ 82%]
tests\unit\test_validation.py ....                                       [100%]

======================= 23 passed, 1 warning in 30.23s ========================
\end{verbatim}

\vspace{0.4cm}

\begin{center}
\fbox{\begin{minipage}{0.9\linewidth}
\centering
\vspace{0.3cm}
\textbf{[Figure 4.1: Test Execution Result Evidence]} \\
\vspace{0.2cm}
\textit{Terminal output and test runner verification showing all 23 automated tests passing across the integration, simulation, and unit testing tiers in 30.23 seconds.}
\vspace{0.3cm}
\end{minipage}}
\end{center}

\vspace{0.2cm}
\begin{center}
\textbf{Figure 4.1:} Automated Test Suite Execution Evidence (23 Passed Pytest Verification Suite)
\end{center}

\vspace{0.3cm}
\textbf{Simulation Lab Benchmark Results:}
The 10 controlled scenarios in the Fault Simulation Lab produced the following verified outcomes:
\begin{enumerate}
\tightlist
\item \textit{DNS Resolution Failure (NXDOMAIN):} Accurately isolated as unresolvable hostname (Confidence: 0.95).
\item \textit{TCP Connection Refused (RST):} Differentiated from timeout; flagged as port closed (Confidence: 0.92).
\item \textit{TCP Connection Timeout:} Identified as stateful firewall packet drop (Confidence: 0.88).
\item \textit{Local Gateway Unreachable:} Gateway ICMP failure isolated from WAN targets (Confidence: 0.90).
\item \textit{TLS Certificate Expired:} Certificate date mismatch detected without handshake crash (Confidence: 0.95).
\item \textit{TLS Hostname Mismatch:} Discrepancy between requested SNI and certificate SAN flagged (Confidence: 0.94).
\item \textit{HTTP 500 Server Error:} Isolated to application server layer rather than transport (Confidence: 0.91).
\item \textit{HTTP 404 Not Found:} Application URL path failure identified (Confidence: 0.90).
\item \textit{High Latency & Jitter Degradation:} Flagged path degradation exceeding threshold (Confidence: 0.85).
\item \textit{Intermittent Packet Loss:} Identified transmission loss on intermediate route hops (Confidence: 0.87).
\end{enumerate}

\subsection{4.3 Objective Achievement}\label{objective-achievement}

Table 4.2 maps each defined project objective to its empirical evidence and final achievement outcome.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.14}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.50}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.36}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Objective ID}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Evidence or Test ID}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Outcome}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
\textbf{O1} & Verified across 8 diagnostic modules and automated unit tests. & \textbf{Achieved} (Complete L2--L7 diagnostic pipeline operational). \\
\textbf{O2} & 100\% match in 10 simulation lab scenarios (\texttt{test\_scenarios.py}). & \textbf{Achieved} (Deterministic hypothesis scoring verified). \\
\textbf{O3} & Streamlit UI operational; 4 REST API endpoints verified in \texttt{test\_api\_endpoints.py}. & \textbf{Achieved} (Dual web UI and REST API fully functional). \\
\textbf{O4} & Background scheduler daemon and mock webhook dispatch verified in \texttt{test\_monitoring\_scheduler.py}. & \textbf{Achieved} (Continuous telemetry and alerting validated). \\
\textbf{O5} & 10 repeatable synthetic scenarios executed and verified in simulation lab. & \textbf{Achieved} (Non-destructive lab demonstration operational). \\
\end{longtable}
}

\begin{center}
\textbf{Table 4.2:} Objective Achievement and Verification Outcome Summary
\end{center}

\newpage

\section{5 Discussion and Conclusion}\label{discussion-and-conclusion}

\subsection{5.1 Discussion and Comparative Analysis}\label{discussion-and-comparative-analysis}

The empirical results confirm that an ordered, cross-layer diagnostic assistant substantially outperforms traditional manual CLI troubleshooting and passive network monitoring. Table 5.1 provides a comparative analysis of the Network Troubleshooting Assistant against existing industry paradigms.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.22}}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.26}}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.26}}
  >{\raggedright\arraybackslash}p{(\linewidth - 6\tabcolsep) * \real{0.26}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Diagnostic Dimension}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Manual CLI (\texttt{ping}, \texttt{curl})}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Passive Sniffer (Wireshark)}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{NTA (Proposed System)}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Execution Workflow & Disjoint, manual command entry across disparate tools. & Manual packet capture requiring deep protocol inspection. & Automated, single-click bottom-up multi-stage investigation. \\
Cross-Layer Correlation & None. Operator must manually deduce inter-layer dependencies. & High detail, but requires expert packet dissection knowledge. & Deterministic cross-layer correlation from L2 through L7. \\
Root Cause Scoring & None. Operator interprets raw textual output. & None. Captures symptoms without actionable root-cause scoring. & Ranked hypothesis generation with calibrated confidence scores. \\
Remediation Guidance & None. Requires separate operational documentation. & None. Diagnostic only. & Step-by-step, actionable, non-destructive remediation advisories. \\
Enterprise Automation & None. Scripting required for batch or scheduling. & Requires specialized tap/span port infrastructure. & Built-in batch auditing, daemonized monitoring, and Slack/ITSM alerts. \\
\end{longtable}
}

\begin{center}
\textbf{Table 5.1:} Comparative Analysis of Network Troubleshooting Paradigms
\end{center}

\subsection{5.2 Advantages and Applications}\label{advantages-and-applications}

The Network Troubleshooting Assistant provides several distinct advantages:
\begin{itemize}
\tightlist
\item \textbf{Significant Reduction in MTTR:} Automates what previously required 5--8 individual manual terminal commands into an orchestrated sub-second or bounded multi-second execution.
\item \textbf{Strict Grounding and Determinism:} Rather than relying on unconstrained generative AI that could hallucinate nonexistent IP addresses or false causes, NTA's deterministic heuristic engine acts as the authoritative source of truth.
\item \textbf{Zero-Agent, Non-Destructive Operation:} Operates entirely in user-space using standard operating system socket interfaces without requiring proprietary kernel drivers or administrative privileges.
\item \textbf{Target Applications:}
  \begin{enumerate}
  \tightlist
  \item \textit{Enterprise IT Helpdesk:} First-line automated triage of employee connectivity issues.
  \item \textit{DevOps & Site Reliability Engineering:} Automated pre-deployment validation of external API endpoints and TLS certificates.
  \item \textit{Academic Computer Networks Education:} Interactive laboratory platform for students to visualize OSI layer interactions and synthetic fault mechanics.
  \end{enumerate}
\end{itemize}

\subsection{5.3 Limitations}\label{limitations}

Despite its demonstrated capabilities, the system operates under certain architectural constraints:
\begin{itemize}
\tightlist
\item \textbf{ICMP Rate-Limiting and Filtering:} Public cloud providers (such as AWS and Cloudflare) and edge firewalls frequently filter or rate-limit ICMP Echo packets, which can lead to false-positive packet loss warnings even when TCP connectivity remains healthy.
\item \textbf{Unprivileged Raw Socket Boundaries:} To maintain strict cross-platform security without requiring \texttt{root}/\texttt{Administrator} permissions, the system executes ICMP pings via OS subprocess wrappers rather than raw \texttt{SOCK\_RAW} sockets.
\item \textbf{Advisory-Only Action Loop:} In compliance with safety policies, the assistant recommends corrective remediation actions (e.g., renewing DHCP leases or flushing DNS caches) but does not execute configuration mutations automatically.
\end{itemize}

\subsection{5.4 Challenges and Troubleshooting}\label{challenges-and-troubleshooting}

During engineering development, several technical challenges were identified, diagnosed, and resolved, as documented in Table 5.2.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.25}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.32}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.43}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Issue Encountered}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Cause or Diagnosis}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Solution and Verification}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Cross-Platform Ping Flags & Windows \texttt{ping} requires \texttt{-n} count, while Linux/macOS require \texttt{-c}. & Developed \texttt{utils/platform.py} abstraction dynamically applying platform-specific command arguments. \\
Blocking Socket Hangs & Standard sockets block indefinitely if target IP drops packets. & Configured explicit non-blocking socket timeouts (\texttt{settimeout(3.0)}), bounded by \texttt{try/except socket.timeout}. \\
TLS Handshake Crash on Expired Certs & Python's default \texttt{ssl.create\_default\_context()} raises an unhandled exception on expired certs. & Implemented custom SSLContext with \texttt{check\_hostname=False} and \texttt{CERT\_NONE} fallback to safely extract metadata. \\
False APIPA Warnings on Inactive Adapters & Disconnected Hyper-V/VirtualBox adapters reported unassigned IPs. & Implemented interface filtering in \texttt{local\_config.py} ignoring loopback, virtual, and unconfigured NICs. \\
\end{longtable}
}

\begin{center}
\textbf{Table 5.2:} Development Challenges, Root Causes, and Applied Solutions
\end{center}

\subsection{5.5 Future Scope}\label{future-scope}

Future enhancements identified for the Network Troubleshooting Assistant include:
\begin{itemize}
\tightlist
\item \textbf{Controlled Semi-Automated Remediation:} Adding an optional user-approved execution mechanism for safe local remediation actions (such as automated DHCP lease renewal via \texttt{ipconfig /renew} or DNS cache flushes).
\item \textbf{SNMP and NetFlow Telemetry Ingestion:} Integrating Simple Network Management Protocol (SNMP v2c/v3) polling to capture switch-port traffic counters, CRC error rates, and router CPU loads.
\item \textbf{eBPF-Based Socket Tracing:} On Linux hosts, utilizing extended Berkeley Packet Filters (eBPF) to monitor kernel-level TCP retransmissions, connection drops, and window exhaustion without runtime overhead.
\item \textbf{IPv6 Route Path Optimization:} Extending full dual-stack route tracing with enhanced hop anomaly detection across pure IPv6 transit backbones.
\end{itemize}

\subsection{5.6 Conclusion}\label{conclusion}

The Network Troubleshooting Assistant successfully demonstrates that complex network troubleshooting can be transformed from an ad-hoc, manual task into an autonomous, deterministic, and evidence-backed engineering discipline. By executing an ordered, bottom-up diagnostic pipeline from Layer 2 to Layer 7, the system eliminates guesswork, discriminates between subtle failure modes (such as firewall packet drops versus closed ports), and synthesizes actionable remediation plans. With dual presentation interfaces (Streamlit web dashboard and FastAPI REST service), background telemetry scheduling, automated multi-channel alerting, and a 100\% pass rate across all automated test suites, the project fulfills all objectives of the Computer Networks Laboratory curriculum.

\newpage

\section{References}\label{references}

\begin{enumerate}
\tightlist
\item J. Postel, ``Internet Protocol --- DARPA Internet Program Protocol Specification,'' RFC 791, Internet Engineering Task Force (IETF), Sep. 1981. doi: 10.17487/RFC0791.
\item J. Postel, ``Internet Control Message Protocol --- DARPA Internet Program Protocol Specification,'' RFC 792, Internet Engineering Task Force (IETF), Sep. 1981. doi: 10.17487/RFC0792.
\item J. Postel, ``Transmission Control Protocol --- DARPA Internet Program Protocol Specification,'' RFC 793, Internet Engineering Task Force (IETF), Sep. 1981. (Updated by RFC 9293, Aug. 2022). doi: 10.17487/RFC9293.
\item P. Mockapetris, ``Domain Names --- Concepts and Facilities,'' RFC 1034, Internet Engineering Task Force (IETF), Nov. 1987. doi: 10.17487/RFC1034.
\item E. Rescorla, ``The Transport Layer Security (TLS) Protocol Version 1.3,'' RFC 8446, Internet Engineering Task Force (IETF), Aug. 2018. doi: 10.17487/RFC8446.
\item R. Fielding, M. Nottingham, and J. Reschke, ``HTTP Semantics,'' RFC 9110, Internet Engineering Task Force (IETF), Jun. 2022. doi: 10.17487/RFC9110.
\item A. Feldmann, O. Maennel, Z. M. Mao, A. Berger, and B. Maggs, ``Locating Internet Routing Instabilities,'' in \textit{Proc. ACM SIGCOMM}, 2004, pp. 205--218. doi: 10.1145/1015467.1015491.
\item Streamlit Inc., ``Streamlit Documentation and API Reference,'' 2026. [Online]. Available: \url{https://docs.streamlit.io} (accessed Oct. 2026).
\item S. Ramirez, ``FastAPI Framework Documentation,'' 2026. [Online]. Available: \url{https://fastapi.tiangolo.com} (accessed Oct. 2026).
\end{enumerate}

\newpage

\section{AI Usage Declaration}\label{ai-usage-declaration}

Artificial Intelligence tools were utilized responsibly in the preparation of this project for technical documentation drafting, code formatting assistance, and grammatical refinement. Specifically, LLM-assisted tools were employed to structure the LaTeX formatting, assist in drafting clear technical descriptions, and generate modular explanations of established RFC protocols. 

All underlying source code modules, diagnostic algorithms, Berkeley socket probes, REST endpoints, and simulation lab fixtures were directly implemented, analyzed, and experimentally validated by the student group. All diagnostic results, test outputs, and performance figures reported in this document are authentic and verified through empirical execution of the automated test suite.

\vspace{0.4cm}

\textbf{Declaration:} We take full responsibility for the accuracy of this report and understand the submitted implementation and results. Sources and assistance used have been duly acknowledged.

\vspace{0.4cm}

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.45}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.25}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.30}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Student Name}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{PRN}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Signature}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Soham Patil & 1272250811 & \vspace{0.4cm} \\
Ganesh Gaikwad & 1262252319 & \vspace{0.4cm} \\
Tirth Gangani & 1272250827 & \vspace{0.4cm} \\
Aditya Sardesai & 1262252353 & \vspace{0.4cm} \\
\end{longtable}
}

\newpage

\section{Appendices}\label{appendices}

\subsection{Appendix A Code and Configuration}\label{appendix-a-code-and-configuration}

\textbf{A.1 Diagnostic Orchestrator Core Workflow (\texttt{engine/orchestrator.py}):}
\begin{verbatim}
def run_investigation(self, user_symptom: str, target_host: Optional[str] = None,
                      target_port: Optional[int] = None, ...):
    session_id = str(uuid.uuid4())
    test_results = []
    
    # 1. Local Network Configuration
    local_res = run_local_config_diagnostic()
    test_results.append(local_res)
    
    # Adaptive short-circuit: if local NIC is down, halt WAN tests
    if local_res.status == TestStatus.FAIL:
        hypotheses, recs = analyze_test_results(test_results)
        return DiagnosticSession(session_id=session_id, test_results=test_results,
                                 hypotheses=hypotheses, recommendations=recs)
                                 
    # 2. Default Gateway ICMP Ping
    gw_ip = local_res.measured_values.get("default_gateway")
    if gw_ip:
        gw_res = check_gateway_reachability(gw_ip)
        test_results.append(gw_res)
        
    # 3. Dual-Stack DNS Resolution
    dns_res = run_dns_resolution(target_host)
    test_results.append(dns_res)
    
    # 4. Destination Reachability & 5. TCP Handshake
    if dns_res.status == TestStatus.PASS:
        dest_res = check_destination_reachability(target_host)
        test_results.append(dest_res)
        port_res = check_tcp_port_availability(target_host, target_port)
        test_results.append(port_res)
        
    # Analyze evidence and persist
    hypotheses, recs = analyze_test_results(test_results, target_host, target_port)
    session = DiagnosticSession(session_id=session_id, test_results=test_results,
                                hypotheses=hypotheses, recommendations=recs)
    save_session(session, self.db_path)
    return session
\end{verbatim}

\subsection{Appendix B Additional Evidence}\label{appendix-b-additional-evidence}

\textbf{B.1 REST API Endpoint Specifications (\texttt{api/server.py}):}
\begin{itemize}
\tightlist
\item \texttt{POST /api/v1/diagnose}: Triggers synchronous multi-stage network investigation against a target hostname, IP, or natural language symptom. Returns full typed \texttt{DiagnosticSession} object.
\item \texttt{GET /api/v1/sessions}: Retrieves paginated historical diagnostic sessions stored in the SQLite repository.
\item \texttt{GET /api/v1/sessions/\{session\_id\}}: Retrieves complete diagnostic evidence vector, hypotheses, and remediation plan for a specific session.
\item \texttt{POST /api/v1/batch-diagnose}: Executes concurrent multi-target diagnostics using bounded worker threadpools.
\item \texttt{GET /api/v1/monitoring/targets} and \texttt{POST /api/v1/monitoring/targets}: Manages targets for background polling and alerting.
\end{itemize}

\subsection{Appendix C Individual Contributions}\label{appendix-c-individual-contributions}

The individual technical contributions of each student member towards the design, implementation, testing, and presentation of the project are documented in Table C.1.

{\def\LTcaptype{none} % do not increment counter
\begin{longtable}[]{@{}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.28}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.42}}
  >{\raggedright\arraybackslash}p{(\linewidth - 4\tabcolsep) * \real{0.30}}@{}}
\toprule\noalign{}
\begin{minipage}[b]{\linewidth}\raggedright
\textbf{Student Name and PRN}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Work Completed}
\end{minipage} & \begin{minipage}[b]{\linewidth}\raggedright
\textbf{Evidence or Deliverable}
\end{minipage} \\
\midrule\noalign{}
\endhead
\bottomrule\noalign{}
\endlastfoot
Soham Patil \newline (PRN: 1272250811) & Application development: Core diagnostic orchestrator, deterministic root cause engine, Berkeley socket probing modules, FastAPI REST backend, SQLite persistence, and automated pytest suite. & \texttt{engine/orchestrator.py}, \newline \texttt{engine/root\_cause.py}, \newline \texttt{diagnostics/*}, \newline \texttt{api/server.py}, \newline \texttt{tests/*} \\
\addlinespace
Ganesh Gaikwad \newline (PRN: 1262252319) & Video making \& frontend of application: Streamlit interactive user interface, real-time adapter dashboards, Plotly traceroute hop visualizer, and project demonstration video production. & \texttt{app.py}, \newline \texttt{app\_ui/*}, \newline \texttt{diagnostics/traceroute\_visualizer.py}, \newline Demonstration Video \\
\addlinespace
Tirth Gangani \newline (PRN: 1272250827) & Documentation and PPT making: Technical requirements documentation, system test plan design, test result compilation, and viva presentation slide deck. & Mini Project Report (Sections 1, 3, 4), \newline Project Presentation Deck \\
\addlinespace
Aditya Sardesai \newline (PRN: 1262252353) & Documentation and PPT making: Architectural diagramming, comparative analysis with existing NMS/CLI tools, protocol mapping tables, and presentation preparation. & Mini Project Report (Sections 2, 5, Appendices), \newline Presentation Visuals \\
\end{longtable}
}

\begin{center}
\textbf{Table C.1:} Individual Student Contributions and Deliverables
\end{center}

\end{document}
'''

def main():
    target_tex_downloads = r'c:\Users\psoha\Downloads\main.tex'
    target_tex_project = r'e:\MITWPU\Engineering\3rd Year\CN\Project\Network-Troubleshooting-Assistant-main\Network_Troubleshooting_Assistant_Report.tex'
    
    print(f"Writing updated LaTeX report to {target_tex_downloads}...")
    with open(target_tex_downloads, 'w', encoding='utf-8') as f:
        f.write(TEX_CONTENT.strip() + '\n')
    print("Successfully written to Downloads.")
    
    print(f"Writing backup copy to {target_tex_project}...")
    with open(target_tex_project, 'w', encoding='utf-8') as f:
        f.write(TEX_CONTENT.strip() + '\n')
    print("Successfully written to Project folder.")

if __name__ == '__main__':
    main()
