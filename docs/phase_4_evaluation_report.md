# Phase 4 — Real Email Ingestion & Testing Evaluation Report

**Date:** 2026-10-27
**Target Senders:** `ANJALI.UPADHYAY43@nmims.in`, `LAKSH.GUPTA28@nmims.in`
**Total Processed Items:** 347 real academic notices

---

## Executive Summary & Dataset Analytics

During Phase 4, the Campus AI backend connected to Gmail via OAuth 2.0, identified email threads from both target senders, and automatically unpacked and decoded **344 individual attached notices** (`.eml` forwarded circulars). Each notice was processed through our NLP pipeline, running classification, importance scoring, regex entity extraction, and automated timetable change synthesis into the SQLite database.

### 1. Predicted Category Breakdown
| Academic Category | Count | Percentage | Typical Subject Matter |
|---|---|---|---|
| **EXAM** | 81 | 23.3% | Re-examination schedules, seating plans, hall ticket mandates, postponement notices |
| **GENERAL** | 75 | 21.6% | University closures, holiday circulars, library access, student guidelines |
| **EVENT** | 65 | 18.7% | Webinars, student council recruitment, orientation sessions, Bloomberg series |
| **ATTENDANCE** | 43 | 12.4% | Bi-weekly/monthly attendance percentages, debarment advisories, internship NOCs |
| **ACADEMIC** | 37 | 10.7% | Elective allocations, curriculum notices, semester subject distributions |
| **CLASSROOM / TIMETABLE** | 20 | 5.8% | Lab venue shifts, classroom relocations, timetable revisions |
| **ASSIGNMENT** | 8 | 2.3% | Problem statements, Moodle submissions, project deadlines |
| **FEES & REGISTRATION** | 11 | 3.2% | Term fee deadlines, payment receipts, portal registrations |
| **WORKSHOP & PLACEMENT** | 6 | 1.7% | Meta SkillsBuild, Java training, career drives |
| **ADMINISTRATIVE** | 1 | 0.3% | Summer vacation library hours |
| **TOTAL** | **347** | **100.0%** | |

### 2. Importance Distribution
| Priority Level | Count | Share | System Action Triggered |
|---|---|---|---|
| **HIGH** | 227 | 65.4% | Surfaced directly on Dashboard, pushes immediate schedule proposal |
| **MEDIUM** | 98 | 28.2% | Stored in standard notice feed with amber badge |
| **LOW** | 22 | 6.3% | Archived for informational reference with green badge |

### 3. Named Entity Extraction Performance
Across all 347 real notices, the regex and rule-based entity extractor extracted and normalized:
- **Times (`TIME`):** **441** temporal expressions (e.g., `10:00 AM`, `02:00 PM`, `05:30 PM`).
- **Dates (`DATE`):** **282** calendar dates normalized into ISO `YYYY-MM-DD` format.
- **Venues & Classrooms (`ROOM`):** **171** rooms and laboratories (e.g., `Lab 21`, `Lab 25`, `Room 204`, `Room 302`, `Online`).
- **Course Subjects (`SUBJECT`):** **163** identified course subjects (e.g., `Physics`, `Artificial Intelligence`, `Operating Systems`, `Computer Networks`).

### 4. Automated Timetable Proposals
- **Proposals Generated:** **115 actionable timetable updates** were automatically identified from class reschedule, cancellation, and venue shift circulars, and inserted into the `events` table with `status="PROPOSED"`.
- Students can review, confirm, or reject each proposal with a single tap in the Android app or web client.

---

## Detailed Ingested Notices & NLP Predictions


| ID | Source | Subject | Category | Confidence | Priority | Detected Change | Entities |
|---|---|---|---|---|---|---|---|
| 4 | Attachment: Undertaking form for students awaiting for the re-exam /revaluation result reg..eml | Undertaking form for students awaiting f | **EXAM** | 12.0% | MEDIUM | None |  |
| 5 | Attachment: RE: Seating Plan  for Even  semester  Re-Exam - June 2026.eml | RE: Seating Plan  for Even  semester  Re | **EXAM** | 13.2% | HIGH | None | DATE:2026-07-09, DATE:2026-07-09, DATE:2026-06-29 |
| 6 | Attachment: RE: Problem Statements for Innovative Solutions.eml | RE: Problem Statements for Innovative So | **ASSIGNMENT** | 13.1% | MEDIUM | None | DATE:2026-07-20, DATE:2026-07-20 |
| 7 | Attachment: Postponement of examinations.eml | Postponement of examinations  | **EXAM** | 14.8% | HIGH | YES: The revised Schedule Change (New Date) | DATE:2026-07-07, DATE:2026-07-07, SUBJECT:The revised |
| 8 | Attachment: Postponement of exams/ re-exams.eml | Postponement of exams/ re-exams | **EXAM** | 14.8% | HIGH | YES: The revised Schedule Change (New Date) | DATE:2026-07-06, DATE:2026-07-06, SUBJECT:The revised |
| 9 | Attachment: Professional Development Program under META SkillsBuild | Narsee Monjee Institute of Management Studies (NMIMS).eml | Professional Development Program under M | **EVENT** | 10.9% | MEDIUM | None | ROOM:Online, ROOM:online, SUBJECT:Periodic assessments and |
| 10 | Attachment: Payment of Fees for Acad .Year 2026-2027.eml | Payment of Fees for Acad .Year 2026-2027 | **FEES** | 12.7% | MEDIUM | None | DATE:2026-07-03, DATE:2026-07-03, DATE:2026-07-17 |
| 11 | Attachment: Java Workshop Notification for B Tech & MBA Tech AI Semester V Students (2026-2027).eml | Java Workshop Notification for B Tech &  | **WORKSHOP** | 12.8% | MEDIUM | None | DATE:2026-07-06, DATE:2026-07-10, TIME:10:00 AM |
| 12 | Attachment: Open Elective 1 & 2 allocation -B Tech & MBA Tech-AI-Sem V (2026-27).eml | Open Elective 1 & 2 allocation -B Tech & | **EVENT** | 10.9% | MEDIUM | None |  |
| 13 | Attachment: New Library E-Resource: WARC Database Now Available (Campus Access Only).eml | New Library E-Resource: WARC Database No | **EVENT** | 10.7% | HIGH | None | ROOM:room discussions |
| 14 | Attachment: New Library E-Resource: STATISTA (Campus License) Now Available.eml | New Library E-Resource: STATISTA (Campus | **EVENT** | 11.1% | LOW | None | ROOM:room teaching, ROOM:online |
| 15 | Attachment: MUST-READ BOOKS !!.eml | MUST-READ BOOKS !! | **EXAM** | 10.8% | HIGH | None | ROOM:Online |
| 16 | Attachment: Id card Mandatory & Important instructions for MPSTME   Re-Examination scheduled from 29th June 2026  onwards.eml | Id card Mandatory & Important instructio | **EXAM** | 14.4% | HIGH | None | DATE:2026-06-29, DATE:2026-06-29, DATE:2026-06-29 |
| 17 | Attachment: Institutional Nomination Notice for ANJALI UPADHYAY - 70512400043 | SVKM’s NMIMS (Narsee Monjee Institute of Management Studies).eml | Institutional Nomination Notice for ANJA | **EXAM** | 11.4% | MEDIUM | None |  |
| 18 | Attachment: Build With AI 2026 – Session Link & Reminder.eml | Build With AI 2026 – Session Link & Remi | **EXAM** | 11.2% | HIGH | None | DATE:2026-06-20, TIME:06:00 PM, TIME:06:00 PM |
| 19 | Attachment: Monthly Thematic e-Books Display on " World Refugee Day " on 20th June 2026.eml | Monthly Thematic e-Books Display on " Wo | **EXAM** | 11.6% | HIGH | None | DATE:2026-06-20, DATE:2026-06-20, DATE:2026-06-20 |
| 20 | Attachment: Narsee Monjee Institute of Management Studies (NMIMS) Final Notice: Professional Development Program under META SkillsBuild.eml | Narsee Monjee Institute of Management St | **ATTENDANCE** | 10.5% | MEDIUM | None | ROOM:Online, ROOM:online |
| 21 | Attachment: Participation Notice — National Career & Development Drive - SVKM’s NMIMS (Narsee Monjee Institute of Management Studies).eml | Participation Notice — National Career & | **EXAM** | 11.0% | HIGH | None |  |
| 22 | Attachment: Re: MPSTME Even SEM Re exam Time table 2025- 2026.eml | Re: MPSTME Even SEM Re exam Time table 2 | **EXAM** | 12.6% | HIGH | None | DATE:2026-06-17, DATE:2026-06-19, DATE:2026-06-17 |
| 23 | Attachment: Narsee Monjee Institute of Management Studies (NMIMS) Second Notice: Professional Development Program under META SkillsBuild.eml | Narsee Monjee Institute of Management St | **ATTENDANCE** | 10.5% | MEDIUM | None | ROOM:Online, ROOM:online |
| 24 | Attachment: FW: Revised computer based even semester re-exam time table.eml | FW: Revised computer based even semester | **EXAM** | 13.0% | HIGH | YES: Class / Examination Schedule Change (New Date) | DATE:2026-06-17, DATE:2026-06-19, DATE:2026-07-04 |
| 25 | Attachment: FW: Bloomberg Education Webinar Series – June Edition.eml | FW: Bloomberg Education Webinar Series – | **EVENT** | 11.5% | HIGH | None | ROOM:room
Explore, ROOM:room learning, ROOM:online |
| 26 | Attachment: New Announcement: Revised MPSTME Computer based  Re-exam Time Table - Even semester 2025-26 send  for course.eml | New Announcement: Revised MPSTME Compute | **EXAM** | 11.8% | HIGH | None |  |
| 27 | Attachment: New Announcement: MPSTME Computer based  Re-exam Time Table - Even semester 2025-26 send  for course.eml | New Announcement: MPSTME Computer based  | **EXAM** | 11.4% | HIGH | None |  |
| 28 | Attachment: FW: computer based even semester re-exam time table.eml | FW: computer based even semester re-exam | **GENERAL** | 12.7% | HIGH | None |  |
| 29 | Attachment: Selection Notice — National Career & Development Drive for NMIMS University.eml | Selection Notice — National Career & Dev | **EXAM** | 11.5% | HIGH | None |  |
| 30 | Attachment: MUST-READ BOOKS !!.eml | MUST-READ BOOKS !! | **EVENT** | 10.7% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:05:00 AM, ROOM:Online |
| 31 | Attachment: Nomination for ANJALI UPADHYAY - 70512400043, has Been Confirmed — National Career & Development Drive.eml | Nomination for ANJALI UPADHYAY - 7051240 | **EXAM** | 11.4% | HIGH | None |  |
| 32 | Attachment: Narsee Monjee Institute of Management Studies (NMIMS) | META SkillsBuild Professional Development Program.eml | Narsee Monjee Institute of Management St | **ATTENDANCE** | 10.5% | MEDIUM | None | ROOM:Online, ROOM:online |
| 33 | Attachment: Academic Calendar - A. Y. 2026-2027.eml | Academic Calendar - A. Y. 2026-2027 | **GENERAL** | 13.9% | LOW | None |  |
| 34 | Attachment: Nomination for ANJALI UPADHYAY - 70512400043, has Been Confirmed — National Career & Development Drive.eml | Nomination for ANJALI UPADHYAY - 7051240 | **EXAM** | 11.4% | HIGH | None |  |
| 35 | Attachment: Fw: Revised User Manual - GR PROCESS.eml | Fw: Revised User Manual - GR PROCESS | **GENERAL** | 11.3% | LOW | None |  |
| 36 | Attachment: User Manual for GR application.eml | User Manual for GR application | **PLACEMENT** | 11.7% | HIGH | None |  |
| 37 | Attachment: Result Declaration (70512400043).eml | Result Declaration (70512400043) | **EXAM** | 11.4% | HIGH | None | SUBJECT:Artificial Intelligence |
| 38 | Attachment: [Final Notice] : Academic Internship(Batch-2026)[With NOC & Credentials].eml | [Final Notice] : Academic Internship(Bat | **ATTENDANCE** | 11.1% | MEDIUM | None | SUBJECT:If you lack |
| 39 | Attachment: Nomination for ANJALI UPADHYAY - 70512400043, has Been Confirmed — National Career & Development Drive.eml | Nomination for ANJALI UPADHYAY - 7051240 | **EXAM** | 11.4% | HIGH | None |  |
| 40 | Attachment: Anjali Upadhyay Student of NMIMS | [Final Reminder] for Summer Internship | NASSCOM Accredited.eml | Anjali Upadhyay Student of NMIMS / [Fina | **EVENT** | 10.8% | MEDIUM | None | TIME:06:30 PM |
| 41 | Attachment: Narsee Monjee Institute of Management Studies & Affiliates - Action Required: Your Nomination for National Career & Development Drive.eml | Narsee Monjee Institute of Management St | **ASSIGNMENT** | 13.9% | HIGH | None |  |
| 42 | Attachment: Narsee Monjee Institute of Management Studies & Affiliates - Action Required: Your Nomination for National Career & Development Drive.eml | Narsee Monjee Institute of Management St | **ASSIGNMENT** | 13.9% | HIGH | None |  |
| 43 | Attachment: Core Committee Roles for AY 2026-27.eml | Core Committee Roles for AY 2026-27 | **PLACEMENT** | 11.7% | HIGH | None | DATE:2026-05-30, DATE:2026-05-30, TIME:11:59 PM |
| 44 | Attachment: Narsee Monjee Institute of Management Studies & Affiliates - Action Required: Your Nomination for National Career & Development Drive.eml | Narsee Monjee Institute of Management St | **ASSIGNMENT** | 13.9% | HIGH | None |  |
| 45 | Attachment: Revised Re-Examination Dates – Even Term AY 2025-26.eml | Revised Re-Examination Dates – Even Term | **EXAM** | 13.4% | HIGH | None | DATE:2026-06-29, DATE:2026-07-11 |
| 46 | Attachment: Official Advisory: National Career & Development Drive 2026 — Narsee Monjee Institute of Management Studies & Affiliates.eml | Official Advisory: National Career & Dev | **ATTENDANCE** | 11.0% | MEDIUM | None |  |
| 47 | Attachment: [Final Notice] : Academic Internship(Batch-2026)[With NOC & Credentials].eml | [Final Notice] : Academic Internship(Bat | **ATTENDANCE** | 11.1% | MEDIUM | None | SUBJECT:If you lack |
| 48 | Attachment: Students' Council Core Team for AY 2026-27..eml | Students' Council Core Team for AY 2026- | **EVENT** | 11.1% | MEDIUM | None |  |
| 49 | Attachment: Library Timings During Summer Vacation.eml | Library Timings During Summer Vacation | **ADMINISTRATIVE** | 18.6% | HIGH | None | DATE:2026-05-18, DATE:2026-07-13 |
| 50 | Attachment: Re: Java Workshop registration for BTech Ai and MBA Tech AI - Sem V - AY 26-27.eml | Re: Java Workshop registration for BTech | **EXAM** | 10.9% | MEDIUM | None | DATE:2026-07-06, DATE:2026-07-10, DATE:2026-06-30 |
| 51 | Attachment: Directive Narsee Monjee Institute of Management Studies & Affiliates : Application pending for National Career and Development Drive.eml | Directive Narsee Monjee Institute of Man | **ATTENDANCE** | 10.8% | MEDIUM | None | ROOM:online |
| 52 | Attachment: Directive Narsee Monjee Institute of Management Studies & Affiliates : Application pending for National Career and Development Drive.eml | Directive Narsee Monjee Institute of Man | **ATTENDANCE** | 10.8% | MEDIUM | None | ROOM:online |
| 53 | Attachment: DHAKAAN RIYA - 70012400010 sent a message.eml | DHAKAAN RIYA - 70012400010 sent a messag | **ATTENDANCE** | 11.1% | MEDIUM | None |  |
| 54 | Attachment: Seating Plan and students Instructions for Even  semester Exam - May 2026.eml | Seating Plan and students Instructions f | **EXAM** | 13.4% | HIGH | None | SUBJECT:Notice Boards on |
| 55 | Attachment: DHAKAAN RIYA - 70012400010 sent a message.eml | DHAKAAN RIYA - 70012400010 sent a messag | **ATTENDANCE** | 11.2% | HIGH | None |  |
| 56 | Attachment: FW: Bloomberg Education Webinars | May 2026.eml | FW: Bloomberg Education Webinars / May 2 | **EVENT** | 11.9% | HIGH | None | ROOM:room integration |
| 57 | Attachment: Seating Plan and students Instructions for Even  semester Exam - May 2026.eml | Seating Plan and students Instructions f | **EXAM** | 13.3% | HIGH | None | DATE:2026-05-12, DATE:2026-05-15, SUBJECT:Notice Boards on |
| 58 | Attachment: FW: Action Requested: Share with Students & Faculty | Bloomberg Education Webinar Se.eml | FW: Action Requested: Share with Student | **EVENT** | 11.7% | MEDIUM | None | ROOM:room integration |
| 59 | Attachment: MEHEK SINGH - 70372200030 shared the folder "interview baksodi" with you.eml | MEHEK SINGH - 70372200030 shared the fol | **ASSIGNMENT** | 11.3% | MEDIUM | None |  |
| 60 | Attachment: AICTE MITACS Globalink Research Internship (GRI) Program 2027 – Opportunity for Undergraduate Students.eml | AICTE MITACS Globalink Research Internsh | **PLACEMENT** | 11.5% | MEDIUM | None |  |
| 61 | Attachment: RE: OE2 - Life Skills (Tuts) cancelled on 7/8/2026.eml | RE: OE2 - Life Skills (Tuts) cancelled o | **GENERAL** | 12.2% | MEDIUM | YES: Class / Examination Schedule Change (New Date) | DATE:2026-08-07 |
| 62 | Attachment: MAD lecture and practical cancellation on 07.08.2026- MBA Tech-AI, Sem  V.eml | MAD lecture and practical cancellation o | **EXAM** | 11.2% | HIGH | None | TIME:02:00 PM, TIME:04:00 PM, SUBJECT:MAD lecture and |
| 63 | Attachment: OE2 Creativity & Ethics -Div B lecture cancelled on 7/8/2026.eml | OE2 Creativity & Ethics -Div B lecture c | **ACADEMIC** | 13.1% | HIGH | YES: Div B Schedule Change (New Date) | DATE:2026-08-07, TIME:04:00 PM, TIME:05:00 PM |
| 64 | Attachment: OE2 Modelling & Simulation lecture re-schedule details.eml | OE2 Modelling & Simulation lecture re-sc | **EVENT** | 11.6% | HIGH | YES: Artificial Intelligence Schedule Change (New Date) | DATE:2026-08-07, DATE:2026-08-14, TIME:05:00 PM |
| 65 | Attachment: OE2 Elements of Project Management lecture re-schedule details.eml | OE2 Elements of Project Management lectu | **GENERAL** | 11.7% | HIGH | YES: Project Management Schedule Change (New Date) | DATE:2026-08-14, DATE:2026-08-07, DATE:2026-08-14 |
| 66 | Attachment: OE2 Creativity & Ethics -Div B lecture cancelled on 6/8/2026.eml | OE2 Creativity & Ethics -Div B lecture c | **ACADEMIC** | 13.1% | HIGH | YES: Div B Schedule Change (New Date) | DATE:2026-08-06, TIME:04:00 PM, TIME:06:00 PM |
| 67 | Attachment: OE2 - Life Skills (Tuts) cancelled on 6/8/2026.eml | OE2 - Life Skills (Tuts) cancelled on 6/ | **ACADEMIC** | 13.4% | MEDIUM | YES: Kindly note Schedule Change (New Date) | DATE:2026-08-06, SUBJECT:Kindly note |
| 68 | Attachment: Access to Pai's Friends Library.eml | Access to Pai's Friends Library  | **EVENT** | 11.2% | HIGH | None |  |
| 69 | Attachment: OE1 Research Methodology lecture cancelled on 03.08.2026.eml | OE1 Research Methodology lecture cancell | **ACADEMIC** | 12.8% | HIGH | YES: Research Methodology Schedule Change (New Date) | TIME:06:00 PM, SUBJECT:Research Methodology |
| 70 | Attachment: Leena Nadkar VISFAC sent a message.eml | Leena Nadkar VISFAC sent a message | **ATTENDANCE** | 11.1% | MEDIUM | None |  |
| 71 | Attachment: OE2 - Financial derivatives- Div A lecture cancellation and re-schedule details.eml | OE2 - Financial derivatives- Div A lectu | **EVENT** | 11.5% | HIGH | YES: Div A Schedule Change (New Date) | TIME:04:00 PM, TIME:05:00 PM, TIME:06:00 PM |
| 72 | Attachment: RE: OE2 - Intro for Forensic Science lecture cancellation and re-schedule details.eml | RE: OE2 - Intro for Forensic Science lec | **ACADEMIC** | 12.0% | HIGH | YES: Intro for Forensic Science Schedule Change (New Date) | DATE:2026-07-31, DATE:2026-08-07, TIME:05:00 PM |
| 73 | Attachment: Change in lecture venue.eml | Change in lecture venue  | **CLASSROOM / TIMETABLE** | 13.1% | HIGH | YES: Change in Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, TIME:04:00 PM |
| 74 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EVENT** | 11.2% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 75 | Attachment: OE2 - Technology & Innovation for Marketing lecture cancellation and re-schedule.eml | OE2 - Technology & Innovation for Market | **EXAM** | 11.2% | HIGH | YES: Innovation for Marketing Schedule Change (New Date) | DATE:2026-07-31, DATE:2026-08-07, TIME:04:00 PM |
| 76 | Attachment: Hackathon.eml | Hackathon | **EVENT** | 11.7% | HIGH | None | ROOM:online |
| 77 | Attachment: Request to Disseminate CCS Information to Students Across All Programs.eml | Request to Disseminate CCS Information t | **EVENT** | 11.3% | LOW | None |  |
| 78 | Attachment: OE1 -Drone Technology Pr B2 batch extra practical schedule.eml | OE1 -Drone Technology Pr B2 batch extra  | **GENERAL** | 11.6% | HIGH | None | TIME:07:00 PM, TIME:07:00 PM, SUBJECT:Kindly note extra |
| 79 | Attachment: You've joined the IEC_2026-27 group.eml | You've joined the IEC_2026-27 group | **ASSIGNMENT** | 11.7% | MEDIUM | None |  |
| 80 | Attachment: OE2 LTLS extra lecture scheduled for every Friday.eml | OE2 LTLS extra lecture scheduled for eve | **GENERAL** | 13.2% | HIGH | None | TIME:00:00 PM, TIME:00:00 PM, SUBJECT:LTLS extra |
| 81 | Attachment: OE1 -Wireless Communication for Everybody change in faculty and practical timing w.e.f. 27.07.2026.eml | OE1 -Wireless Communication for Everybod | **GENERAL** | 11.1% | HIGH | None | TIME:06:00 PM, TIME:06:30 PM, TIME:06:30 PM |
| 82 | Attachment: OE1 Smart Cities -Div B lecture cancelled on 29.07.2026.eml | OE1 Smart Cities -Div B lecture cancelle | **ACADEMIC** | 13.1% | HIGH | YES: Div B Schedule Change (New Date) | DATE:2026-07-29, TIME:04:00 PM, TIME:06:00 PM |
| 83 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **ATTENDANCE** | 11.4% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 84 | Attachment: MEHEK SINGH - 70372200030 shared the folder "IEC 2025-26" with you.eml | MEHEK SINGH - 70372200030 shared the fol | **ASSIGNMENT** | 11.4% | MEDIUM | None |  |
| 85 | Attachment: Classroom for OE2 Life Skills.eml | Classroom for OE2 Life Skills  | **GENERAL** | 13.3% | HIGH | None | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 86 | Attachment: Monthly Thematic e-Books Display on "Kargil Vijay Diwas – 26 July ".eml | Monthly Thematic e-Books Display on "Kar | **EXAM** | 10.8% | HIGH | None | DATE:2026-07-26, DATE:2026-07-26, DATE:2026-07-26 |
| 87 | Attachment: OE-1 : Basic Decision Making with Spreadsheet theory / practical cancellation.eml | OE-1 : Basic Decision Making with Spread | **EVENT** | 11.3% | HIGH | YES: Kindly note Schedule Change (New Date) | ROOM:room

 CC-803, SUBJECT:Kindly note |
| 88 | Attachment: Advisory for Students to deal with Cyber Fraud / Unauthorized Calls.eml | Advisory for Students to deal with Cyber | **GENERAL** | 14.0% | LOW | None |  |
| 89 | Attachment: Venue change for OE2 subjects - Sem V.eml | Venue change for OE2 subjects - Sem V | **GENERAL** | 12.3% | HIGH | None | ROOM:room change |
| 90 | Attachment: FW: User Manual - GR PROCESS.eml | FW: User Manual - GR PROCESS | **GENERAL** | 11.8% | HIGH | None | TIME:00:00 PM, ROOM:online |
| 91 | Attachment: OE2 –Financial Derivatives - Div A - lecture cancelled on 24.7.2026.eml | OE2 –Financial Derivatives - Div A - lec | **ACADEMIC** | 11.3% | HIGH | YES: Kindly note Schedule Change (New Date) | TIME:04:00 PM, TIME:05:00 PM, TIME:06:00 PM |
| 92 | Attachment: OE2 –Creativity and Ethics in Marketing lecture cancelled on 24.7.2026.eml | OE2 –Creativity and Ethics in Marketing  | **ACADEMIC** | 12.5% | HIGH | YES: Ethics in Marketing Schedule Change (New Date) | TIME:04:00 PM, TIME:05:00 PM, SUBJECT:Ethics in Marketing |
| 93 | Attachment: SVKM's Narsee Monjee Institute of Management Studies (NMIMS) First Notice: Professional Development Program under META SkillsBuild.eml | SVKM's Narsee Monjee Institute of Manage | **ATTENDANCE** | 10.5% | MEDIUM | None | ROOM:Online, ROOM:online |
| 94 | Attachment: OE2 - Advertising and PR lecture cancellation and re-schedule details.eml | OE2 - Advertising and PR lecture cancell | **EVENT** | 11.6% | HIGH | YES: Advertising and PR Schedule Change (New Date) | DATE:2026-07-23, DATE:2026-07-24, TIME:05:00 PM |
| 95 | Attachment: OE1 -Interior Design re-schedule details.eml | OE1 -Interior Design re-schedule details | **EVENT** | 11.9% | HIGH | YES: Kindly note Schedule Change (New Date) | DATE:2026-07-20, DATE:2026-07-21, DATE:2026-07-28 |
| 96 | Attachment: OE1 -Drone Technology Pr B2 batch cancelled on 22.07.2026.eml | OE1 -Drone Technology Pr B2 batch cancel | **ACADEMIC** | 12.9% | MEDIUM | YES: Kindly note Schedule Change (New Date) | DATE:2026-07-22, TIME:06:00 PM, SUBJECT:Kindly note |
| 97 | Attachment: Clarification Regarding OE1 -Smart Cities Lecture Session.eml | Clarification Regarding OE1 -Smart Citie | **GENERAL** | 11.6% | HIGH | None | SUBJECT:Smart Cities |
| 98 | Attachment: Payment Receipt 020000586266.eml | Payment Receipt 020000586266 | **FEES** | 14.4% | HIGH | None |  |
| 99 | Attachment: Payment Receipt 020000586266.eml | Payment Receipt 020000586266 | **FEES** | 14.4% | HIGH | None |  |
| 100 | Attachment: Payment Receipt 020000586266.eml | Payment Receipt 020000586266 | **FEES** | 12.5% | MEDIUM | None | DATE:0403-21-07 |
| 101 | Attachment: OE1 -Interior Design lecture cancelled on 21.07.2026.eml | OE1 -Interior Design lecture cancelled o | **ACADEMIC** | 15.1% | MEDIUM | YES: Interior Design Schedule Change (New Date) | DATE:2026-07-21, TIME:05:00 PM, SUBJECT:Interior Design |
| 102 | Attachment: FW: Empowering the Next Generation of Finance Professionals | Bloomberg Education We.eml | FW: Empowering the Next Generation of Fi | **ATTENDANCE** | 11.6% | HIGH | None | ROOM:room learning, ROOM:online, ROOM:room engagement |
| 103 | Attachment: Revised Open Elective 1 & 2 time table.eml | Revised Open Elective 1 & 2 time table | **EXAM** | 11.1% | HIGH | None | TIME:00:00 PM, TIME:00:00 PM |
| 104 | Attachment: OE1 -Interior Design lecture cancelled on 20.07.2026.eml | OE1 -Interior Design lecture cancelled o | **ACADEMIC** | 14.8% | MEDIUM | YES: Interior Design Schedule Change (New Date) | DATE:2026-07-20, TIME:06:00 PM, SUBJECT:Interior Design |
| 105 | Attachment: RE: Introduction to ERP I and II.eml | RE: Introduction to ERP I and II  | **REGISTRATION** | 10.7% | HIGH | None | TIME:00:00 PM |
| 106 | Attachment: OE1 -Sustainable Energy Technologies lecture cancellation and re-schedule details.eml | OE1 -Sustainable Energy Technologies lec | **ACADEMIC** | 11.6% | HIGH | YES: Energy Technologies Schedule Change (New Date) | DATE:2026-07-20, DATE:2026-07-21, DATE:2026-08-04 |
| 107 | Attachment: OE1 -Basic decision making with spreadsheet lecture cancelled on 20.07.2026 - Sem V.eml | OE1 -Basic decision making with spreadsh | **ACADEMIC** | 12.2% | HIGH | YES: Kindly note Schedule Change (New Date) | SUBJECT:Kindly note |
| 108 | Attachment: Change in lab venue- MBA Tech & B Tech-AI, Sem V w.e.f. 20.07.2026.eml | Change in lab venue- MBA Tech & B Tech-A | **GENERAL** | 11.3% | HIGH | None | ROOM:Lab
4, ROOM:Lab
CL, ROOM:Lab
2 |
| 109 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EVENT** | 11.2% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 110 | Attachment: Greetings and Introductory Message : Prof. Sougata Ray, Vice Chancellor.eml | Greetings and Introductory Message : Pro | **EXAM** | 11.2% | MEDIUM | None | SUBJECT:Artificial Intelligence |
| 111 | Attachment: OE 2 Life Skills tutorial cancelled on 17.07.2026 - Sem V.eml | OE 2 Life Skills tutorial cancelled on 1 | **ACADEMIC** | 12.8% | MEDIUM | YES: Kindly note Schedule Change (New Date) | TIME:05:00 PM, SUBJECT:Kindly note |
| 112 | Attachment: IS -II Pr B1 &  B2 batch cancelled on 20.07.2026 - MBA Tech-AI -Sem V.eml | IS -II Pr B1 &  B2 batch cancelled on 20 | **GENERAL** | 11.2% | MEDIUM | YES: Kindly note Schedule Change (New Date) | TIME:04:00 PM, SUBJECT:Kindly note |
| 113 | Attachment: Team Code for OE1 Research Methodology odd 2026-27.eml | Team Code for OE1 Research Methodology o | **GENERAL** | 11.4% | LOW | None | SUBJECT:Research Methodology |
| 114 | Attachment: OE2 TIM lecture cancellation and re-schedule details.eml | OE2 TIM lecture cancellation and re-sche | **EVENT** | 11.4% | HIGH | YES: TIM Schedule Change (New Date) | DATE:2026-07-17, DATE:2026-07-24, TIME:04:00 PM |
| 115 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EXAM** | 11.3% | HIGH | None | ROOM:online, ROOM:LAB MBA, SUBJECT:You have been added to a |
| 116 | Attachment: Change in practical  venue w.e.f. 20.07.2026 - MBA Tech-AI, Sem V.eml | Change in practical  venue w.e.f. 20.07. | **GENERAL** | 11.5% | HIGH | None | TIME:02:00 PM, SUBJECT:Computer Networks |
| 117 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **ATTENDANCE** | 11.3% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 118 | Attachment: RE: OE1 Division details - Sem III & V.eml | RE: OE1 Division details - Sem III & V | **GENERAL** | 12.1% | LOW | None | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 119 | Attachment: RE: OE2 Division/CR /Life Skills Th/Tuts-BTech_MBA Tech_BTI  26-27.eml | RE: OE2 Division/CR /Life Skills Th/Tuts | **GENERAL** | 11.8% | LOW | None | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 120 | Attachment: OE-2- FINANCIAL DERIVATIVES lecture cancellation and re-schedule details- Sem V.eml | OE-2- FINANCIAL DERIVATIVES lecture canc | **EVENT** | 11.4% | HIGH | YES: FINANCIAL DERIVATIVES Schedule Change (New Date) | DATE:2026-07-16, DATE:2026-07-17, TIME:04:00 PM |
| 121 | Attachment: NMIMS Knowledge Trendsetters – Volume 5 (Issue 3) | Indigenous Intelligence: Learning from IKS.eml | NMIMS Knowledge Trendsetters – Volume 5  | **EVENT** | 11.2% | HIGH | None |  |
| 122 | Attachment: reg. OE Engineering Materials for Daily Life.eml | reg. OE Engineering Materials for Daily  | **GENERAL** | 13.0% | LOW | YES: Class / Examination Schedule Change (New Date) |  |
| 123 | Attachment: FW: Link to join MS Team for the subject OE - I, Smart Cities.eml | FW: Link to join MS Team for the subject | **GENERAL** | 13.9% | LOW | None |  |
| 124 | Attachment: OE1 - Wireless Communication for Everybody practical batches.eml | OE1 - Wireless Communication for Everybo | **EXAM** | 11.5% | HIGH | None | TIME:06:00 PM, TIME:06:00 PM, SUBJECT:Artificial Intelligence |
| 125 | Attachment: Change of faculty - OE2 Leading through Life Skills - B Tech & MBA Tech -Sem V.eml | Change of faculty - OE2 Leading through  | **GENERAL** | 13.1% | HIGH | None |  |
| 126 | Attachment: RE: OE1 & OE2 - UPDATED Time table, Student and practical batches - B Tech & MBA Tech -DS & AI -Sem V (2026-2027).eml | RE: OE1 & OE2 - UPDATED Time table, Stud | **EXAM** | 11.1% | MEDIUM | None | SUBJECT:Student and |
| 127 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EXAM** | 11.2% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 128 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EVENT** | 11.1% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 129 | Attachment: Attendance Report_70512400043.eml | Attendance Report_70512400043 | **ATTENDANCE** | 15.7% | HIGH | None |  |
| 130 | Attachment: Your sign-in code 296897 for Hack2skill.eml | Your sign-in code 296897 for Hack2skill | **EXAM** | 11.3% | HIGH | None |  |
| 131 | Attachment: SRG Projects- Invitation to Join the WhatsApp Group.eml | SRG Projects- Invitation to Join the Wha | **ATTENDANCE** | 11.7% | HIGH | None | DATE:2026-09-24, DATE:2026-09-18, DATE:2026-09-10 |
| 132 | Attachment: OE-1 : Basic Decision Making with Spreadsheet Pr Batch 2 re-schedule.eml | OE-1 : Basic Decision Making with Spread | **EVENT** | 11.3% | HIGH | YES: Kindly note Schedule Change (New Date) | ROOM:room

 CL-706, SUBJECT:Kindly note |
| 133 | Attachment: Online Meeting for Discussion on SRG Projects.eml | Online Meeting for Discussion on SRG Pro | **ATTENDANCE** | 11.6% | HIGH | None | DATE:2026-09-24, DATE:2026-09-18, DATE:2026-09-10 |
| 134 | Attachment: OE2 Management through Movies –DIV A lecture cancellation on 01.10.2026.eml | OE2 Management through Movies –DIV A lec | **ACADEMIC** | 11.6% | HIGH | None | DATE:2026-10-01, TIME:06:00 PM, SUBJECT:DIV A |
| 135 | Attachment: OE1 - Engineering Materials for Daily Life extra lecture schedule.eml | OE1 - Engineering Materials for Daily Li | **GENERAL** | 11.8% | HIGH | None | DATE:2026-09-14, DATE:2026-09-14, DATE:2026-10-20 |
| 136 | Attachment: OE2 Waste Management lecture cancellation and re-schedule details.eml | OE2 Waste Management lecture cancellatio | **EVENT** | 11.5% | HIGH | YES: Waste Management Schedule Change (New Date) | TIME:00:00 PM, TIME:06:00 PM, SUBJECT:Waste Management |
| 137 | Attachment: OE2 Leading through Life Skills Div. B extra lecture details.eml | OE2 Leading through Life Skills Div. B e | **GENERAL** | 11.6% | HIGH | None | TIME:00:00 PM, TIME:00:00 PM, SUBJECT:B extra |
| 138 | Attachment: Fw: National Hardware challenge: Vishwakarma Awards 2026-27 - Submission Deadline Extended to 20th September,2026-reg..eml | Fw: National Hardware challenge: Vishwak | **ASSIGNMENT** | 11.6% | MEDIUM | None | DATE:2026-09-20, DATE:2026-09-20 |
| 139 | Attachment: OE2 FIMIS-DIV B extra lecture details.eml | OE2 FIMIS-DIV B extra lecture details | **EVENT** | 11.2% | HIGH | YES: DIV B extra Schedule Change (New Date) | TIME:05:00 PM, TIME:06:00 PM, SUBJECT:DIV B extra |
| 140 | Attachment: OE1 EOA practical re-schedule details.eml | OE1 EOA practical re-schedule details | **EVENT** | 11.7% | HIGH | YES: EOA Schedule Change (New Date) | DATE:2026-09-16, DATE:2026-09-22, DATE:2026-09-29 |
| 141 | Attachment: OE2 Advertising and Public Relations lecture re-schedule details.eml | OE2 Advertising and Public Relations lec | **EVENT** | 11.5% | HIGH | YES: Public Relations Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 142 | Attachment: RE: OE2 Modelling and Simulation lecture cancellation and re-schedule details.eml | RE: OE2 Modelling and Simulation lecture | **EXAM** | 11.4% | HIGH | YES: Artificial Intelligence Schedule Change (New Date) | DATE:2026-09-18, DATE:2026-10-09, DATE:2026-09-10 |
| 143 | Attachment: FW: Bloomberg Education Webinars | September 2026.eml | FW: Bloomberg Education Webinars / Septe | **EVENT** | 11.4% | HIGH | None | DATE:2026-09-18, DATE:2026-09-21, TIME:05:00 PM |
| 144 | Attachment: OE2 Operations and Supply Chain Management  extra lecture scheduled.eml | OE2 Operations and Supply Chain Manageme | **ACADEMIC** | 11.3% | HIGH | YES: Chain Management extra Schedule Change (New Date) | DATE:2026-09-18, DATE:2026-09-25, DATE:2026-10-02 |
| 145 | Attachment: Change in OE2  - IFS lecture venue on 18.09.2026.eml | Change in OE2  - IFS lecture venue on 18 | **CLASSROOM / TIMETABLE** | 12.7% | HIGH | YES: IFS Schedule Change (New Date) | TIME:06:00 PM, SUBJECT:IFS |
| 146 | Attachment: Problem Statements for Developing Innovative Solutions – Presentation Opportunity.eml | Problem Statements for Developing Innova | **ATTENDANCE** | 11.5% | MEDIUM | None | DATE:2026-09-24, DATE:2026-09-18, DATE:2026-09-10 |
| 147 | Attachment: DAA practical cancellation and re-schedule details - MBA Tech-AI, Sem V.eml | DAA practical cancellation and re-schedu | **EXAM** | 11.6% | HIGH | YES: DAA Schedule Change (New Date) | TIME:04:00 PM, TIME:10:00 AM, SUBJECT:DAA |
| 148 | Attachment: Deep Learning practical B2 batch cancelled on 17.09.2026 - MBA Tech-AI, Sem V.eml | Deep Learning practical B2 batch cancell | **EXAM** | 11.4% | HIGH | YES: Deep Learning Schedule Change (New Date) | DATE:2026-09-17, TIME:12:00 PM, TIME:02:00 PM |
| 149 | Attachment: OE2 Life Skills extra tutorial schedule.eml | OE2 Life Skills extra tutorial schedule | **GENERAL** | 12.4% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:06:00 PM, ROOM:room
 CR |
| 150 | Attachment: OE1 Drone Technology practical cancelled for today.eml | OE1 Drone Technology practical cancelled | **EXAM** | 10.9% | HIGH | YES: Drone Technology Schedule Change (New Date) | SUBJECT:Drone Technology |
| 151 | Attachment: OE1 Basic Decision Making with Spreadsheet /Pr. Batch-1 re-schedule details.eml | OE1 Basic Decision Making with Spreadshe | **EVENT** | 12.2% | HIGH | YES: Class / Examination Schedule Change (New Date) | ROOM:room

 CL-706 |
| 152 | Attachment: OE 2 RES lecture cancelled on 15.09.2026.eml | OE 2 RES lecture cancelled on 15.09.2026 | **ACADEMIC** | 10.7% | HIGH | YES: RES Schedule Change (New Date) | SUBJECT:RES |
| 153 | Attachment: OE1 Introduction to GIS lecture cancelled on 15.09.2026 - Sem V.eml | OE1 Introduction to GIS lecture cancelle | **ACADEMIC** | 11.8% | HIGH | YES: Introduction to GIS Schedule Change (New Date) | TIME:05:00 PM, SUBJECT:Introduction to GIS |
| 154 | Attachment: OE2 FIMIS Div A extra lecture scheduled on 11.09.2026.eml | OE2 FIMIS Div A extra lecture scheduled  | **CLASSROOM / TIMETABLE** | 11.0% | HIGH | YES: FIMIS Div A extra Schedule Change (New Date) | DATE:2026-09-11, TIME:05:00 PM, TIME:06:00 PM |
| 155 | Attachment: OE2 FIMIS Div B extra lecture scheduled on 11.09.2026.eml | OE2 FIMIS Div B extra lecture scheduled  | **CLASSROOM / TIMETABLE** | 11.5% | HIGH | YES: FIMIS Div B extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, TIME:05:00 PM |
| 156 | Attachment: OE2-Financial derivatives –DIV A extra lecture.eml | OE2-Financial derivatives –DIV A extra l | **GENERAL** | 11.4% | HIGH | YES: DIV A extra Schedule Change (New Date) | TIME:06:00 PM, SUBJECT:DIV A extra |
| 157 | Attachment: OE2-FIMIS - Div A lecture cancelled on 10.09.2026.eml | OE2-FIMIS - Div A lecture cancelled on 1 | **ACADEMIC** | 11.3% | HIGH | YES: Div A Schedule Change (New Date) | DATE:2026-09-10, TIME:04:00 PM, TIME:06:00 PM |
| 158 | Attachment: Don't lose your progress - pick up where you left off 🎯.eml | Don't lose your progress - pick up where | **ATTENDANCE** | 11.2% | MEDIUM | None |  |
| 159 | Attachment: OE1 Interior Design extra lecture schedule.eml | OE1 Interior Design extra lecture schedu | **GENERAL** | 11.8% | HIGH | YES: Interior Design extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, ROOM:room
CR-506 |
| 160 | Attachment: FW: NMIMS x Coursera Student Office Hours.eml | FW: NMIMS x Coursera Student Office Hour | **ATTENDANCE** | 12.5% | HIGH | None | TIME:05:00 PM, TIME:05:40 PM, TIME:05:00 PM |
| 161 | Attachment: OE2-Production Management extra lecture schedule.eml | OE2-Production Management extra lecture  | **GENERAL** | 11.2% | HIGH | YES: Management extra Schedule Change (New Date) | DATE:2026-08-28, DATE:2026-09-25, DATE:2026-10-02 |
| 162 | Attachment: OE2-Life Skills extra tutorial schedule.eml | OE2-Life Skills extra tutorial schedule | **GENERAL** | 11.3% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:05:00 PM, TIME:06:00 PM, ROOM:room

 CR |
| 163 | Attachment: SIH Problem Statement and Theme Details.eml | SIH Problem Statement and Theme Details | **EXAM** | 11.1% | MEDIUM | None | TIME:02:00 PM, TIME:03:00 PM, SUBJECT:Artificial Intelligence |
| 164 | Attachment: Refresh with a short course recap.eml | Refresh with a short course recap | **EVENT** | 10.8% | MEDIUM | None | SUBJECT:Software Engineering |
| 165 | Attachment: Thematic E- Book Display on "Teacher's Day" 2026.eml | Thematic E- Book Display on "Teacher's D | **EVENT** | 11.2% | MEDIUM | None | DATE:2026-09-05 |
| 166 | Attachment: RE: Changes in Classroom from 8.9.2026 to 12.9.2026.eml | RE: Changes in Classroom from 8.9.2026 t | **CLASSROOM / TIMETABLE** | 14.0% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, TIME:04:00 PM |
| 167 | Attachment: Change in venue of OE1 EOA on 21.09.2026 and 22.09.2026.eml | Change in venue of OE1 EOA on 21.09.2026 | **CLASSROOM / TIMETABLE** | 12.5% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, TIME:05:00 PM |
| 168 | Attachment: OE2-Financial Derivatives Div. B extra lecture schedule.eml | OE2-Financial Derivatives Div. B extra l | **CLASSROOM / TIMETABLE** | 11.4% | HIGH | YES: B extra Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, TIME:04:00 PM |
| 169 | Attachment: OE2-FIMIS Div. B extra lecture schedule.eml | OE2-FIMIS Div. B extra lecture schedule | **EXAM** | 11.3% | HIGH | YES: B extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, TIME:05:00 PM |
| 170 | Attachment: OE2-  FIMIS Div. A lecture cancellation on 03.09.2026.eml | OE2-  FIMIS Div. A lecture cancellation  | **ACADEMIC** | 11.6% | HIGH | None | DATE:2026-09-03, TIME:04:00 PM, TIME:06:00 PM |
| 171 | Attachment: SIH 2026 – Internal Faculty Mentor Allotment.eml | SIH 2026 – Internal Faculty Mentor Allot | **ATTENDANCE** | 11.5% | MEDIUM | None | SUBJECT:Artificial Intelligence |
| 172 | Attachment: OE2- Leading through Life Skills Div. B extra lecture schedule.eml | OE2- Leading through Life Skills Div. B  | **GENERAL** | 11.3% | HIGH | YES: B extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 173 | Attachment: ⚡ You activated your weekly learning streak!.eml | ⚡ You activated your weekly learning str | **GENERAL** | 11.0% | MEDIUM | None |  |
| 174 | Attachment: OE1- 3D Printing- OE 1/ PR (Batch 2) practical cancellation on 2.9.2026.eml | OE1- 3D Printing- OE 1/ PR (Batch 2) pra | **GENERAL** | 12.3% | HIGH | YES: Kindly note Schedule Change (New Date) | DATE:2026-09-02, TIME:04:00 PM, TIME:06:00 PM |
| 175 | Attachment: OE2 Management through Movies-DIV B cancellation and extra lecture schedule.eml | OE2 Management through Movies-DIV B canc | **EXAM** | 11.0% | MEDIUM | YES: B cancellation and extra Schedule Change (New Date) | DATE:2026-10-08, DATE:2026-10-09, DATE:2026-09-04 |
| 176 | Attachment: Keep your weekly streak alive⚡.eml | Keep your weekly streak alive⚡ | **EXAM** | 11.0% | MEDIUM | None |  |
| 177 | Attachment: Attendance Report_70512400043.eml | Attendance Report_70512400043 | **ATTENDANCE** | 15.7% | HIGH | None |  |
| 178 | Attachment: MPSTME Student Research Group (SRG) Projects.eml | MPSTME Student Research Group (SRG) Proj | **EVENT** | 11.7% | MEDIUM | None |  |
| 179 | Attachment: OE2 Quantum Computing and Technology extra lecture schedule.eml | OE2 Quantum Computing and Technology ext | **GENERAL** | 11.1% | HIGH | None | TIME:00:00 PM, TIME:00:00 PM, SUBJECT:Technology extra |
| 180 | Attachment: Change in lecture schedule on 01.09.2026 and DL extra lecture on 03.09.2026 - MBA Tech-AI, Sem V.eml | Change in lecture schedule on 01.09.2026 | **CLASSROOM / TIMETABLE** | 12.8% | HIGH | YES: Change in Schedule Change (New Date) | TIME:11:00 AM, TIME:11:00 AM, SUBJECT:Change in |
| 181 | Attachment: OE2 TIM - Extra Lecture on 04.09.2026.eml | OE2 TIM - Extra Lecture on 04.09.2026 | **EXAM** | 10.9% | HIGH | YES: Kindly note extra Schedule Change (New Date) | DATE:2026-09-04, TIME:05:00 PM, TIME:06:00 PM |
| 182 | Attachment: Just a few minutes today can make a big difference 📚.eml | Just a few minutes today can make a big  | **EXAM** | 11.1% | HIGH | None |  |
| 183 | Attachment: OE1- Basic Decision Making with Spreadsheet lecture cancellation & re-schedule details.eml | OE1- Basic Decision Making with Spreadsh | **EVENT** | 11.7% | HIGH | YES: Making with Spreadsheet Schedule Change (New Date) | ROOM:room

 CC-803, SUBJECT:Making with Spreadsheet |
| 184 | Attachment: OE2 Advertising and Public relations extra lecture schedule.eml | OE2 Advertising and Public relations ext | **GENERAL** | 12.3% | HIGH | YES: Public relations extra Schedule Change (New Date) | TIME:00:00 PM, ROOM:room
CR-506, SUBJECT:Public relations extra |
| 185 | Attachment: OE1 Elements of Automation extra lecture schedule.eml | OE1 Elements of Automation extra lecture | **CLASSROOM / TIMETABLE** | 11.2% | HIGH | YES: Automation extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, ROOM:room
CR |
| 186 | Attachment: Dive into  AI Receptive Software Development!.eml | Dive into  AI Receptive Software Develop | **EVENT** | 11.0% | HIGH | None |  |
| 187 | Attachment: OE2 Management through Movies –DIV A extra lecture schedule.eml | OE2 Management through Movies –DIV A ext | **GENERAL** | 11.3% | HIGH | None | TIME:06:00 PM, SUBJECT:DIV A extra |
| 188 | Attachment: Invitation to Participate in Book Review Competition on Srimad Bhagavatam.eml | Invitation to Participate in Book Review | **EVENT** | 12.3% | MEDIUM | None | DATE:2026-09-04, DATE:2026-09-04, DATE:2026-09-03 |
| 189 | Attachment: 📚 Start AI Receptive Software Development!.eml | 📚 Start AI Receptive Software Developmen | **EXAM** | 11.0% | MEDIUM | None |  |
| 190 | Attachment: OE2 Financial derivatives –DIV B lecture cancellation  .eml | OE2 Financial derivatives –DIV B lecture | **GENERAL** | 11.3% | HIGH | None | TIME:06:00 PM, ROOM:room
CR-502, SUBJECT:DIV B |
| 191 | Attachment: FW: Holiday on account of Raksha Bandhan – Friday, 28 August 2026.eml | FW: Holiday on account of Raksha Bandhan | **GENERAL** | 15.5% | HIGH | None | DATE:2026-08-28, DATE:2026-08-28, DATE:2026-08-18 |
| 192 | Attachment: OE1 Drone Technology B2 batch practical cancelled on 26.08.2026.eml | OE1 Drone Technology B2 batch practical  | **ACADEMIC** | 11.7% | HIGH | YES: Kindly note Schedule Change (New Date) | DATE:2026-08-26, TIME:06:00 PM, SUBJECT:Kindly note |
| 193 | Attachment: OE2 Financial derivatives –DIV A lecture cancellation and re-schedule details .eml | OE2 Financial derivatives –DIV A lecture | **EVENT** | 11.5% | HIGH | YES: DIV A Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, TIME:06:00 PM |
| 194 | Attachment: OE1 SCADA extra lecture / practical schedule.eml | OE1 SCADA extra lecture / practical sche | **EXAM** | 11.6% | HIGH | YES: SCADA extra Schedule Change (New Date) | DATE:2026-08-31, DATE:2026-09-21, DATE:2026-09-08 |
| 195 | Attachment: NLP theory cancelled on 26.08.2026 - MBA Tech-AI, Sem V.eml | NLP theory cancelled on 26.08.2026 - MBA | **EVENT** | 11.3% | MEDIUM | YES: NLP Schedule Change (New Date) | TIME:04:00 PM, SUBJECT:NLP |
| 196 | Attachment: Anjali Upadhyay: NMIMS invites you to learn on Coursera!.eml | Anjali Upadhyay: NMIMS invites you to le | **ATTENDANCE** | 11.1% | MEDIUM | None |  |
| 197 | Attachment: Action Required: Please confirm your email.eml | Action Required: Please confirm your ema | **ATTENDANCE** | 11.7% | MEDIUM | None |  |
| 198 | Attachment: Action Required: Please confirm your email.eml | Action Required: Please confirm your ema | **ATTENDANCE** | 11.7% | MEDIUM | None |  |
| 199 | Attachment: Don't miss out, activate your Coursera access today!.eml | Don't miss out, activate your Coursera a | **WORKSHOP** | 11.9% | MEDIUM | None | ROOM:online |
| 200 | Attachment: FW: Updated invitation: Coursera x NMIMS Student Office Hours @ Tue Aug 25, 2026 4pm - 4:40pm (IST) (siba.panda@nmims.edu).eml | FW: Updated invitation: Coursera x NMIMS | **ATTENDANCE** | 11.9% | MEDIUM | None | DATE:2026-08-25, DATE:2026-08-25, TIME:04:00 PM |
| 201 | Attachment: OE2 Leading through Life Skills Div. B lecture cancellation and re-schedule details.eml | OE2 Leading through Life Skills Div. B l | **EVENT** | 11.5% | MEDIUM | YES: Kindly note Schedule Change (New Date) | DATE:2004-06-05, SUBJECT:Kindly note |
| 202 | Attachment: Save 25% on in-demand skills!.eml | Save 25% on in-demand skills! | **EXAM** | 10.9% | MEDIUM | None | SUBJECT:Artificial Intelligence |
| 203 | Attachment: Try a month of Coursera Plus for 25% off!.eml | Try a month of Coursera Plus for 25% off | **EXAM** | 10.9% | MEDIUM | None | SUBJECT:Artificial Intelligence |
| 204 | Attachment: OE2 Waste Management lecture cancelled on 21.08.2026.eml | OE2 Waste Management lecture cancelled o | **ACADEMIC** | 12.9% | HIGH | YES: Waste Management Schedule Change (New Date) | DATE:2026-08-21, TIME:05:00 PM, ROOM:room

CR |
| 205 | Attachment: OE2 -Environment Mgmt lecture cancellation and re-schedule details.eml | OE2 -Environment Mgmt lecture cancellati | **EVENT** | 11.5% | HIGH | YES: Environment Mgmt Schedule Change (New Date) | DATE:2026-08-20, DATE:2026-08-21, DATE:2026-08-28 |
| 206 | Attachment: OE2  TIM lecture cancellation and re-schedule details.eml | OE2  TIM lecture cancellation and re-sch | **EVENT** | 11.5% | HIGH | YES: TIM Schedule Change (New Date) | DATE:2026-08-21, DATE:2026-08-28, TIME:04:00 PM |
| 207 | Attachment: RE: OE2 FIMIS extra lecture schedule.eml | RE: OE2 FIMIS extra lecture schedule | **GENERAL** | 11.9% | HIGH | YES: FIMIS extra Schedule Change (New Date) | DATE:2026-08-21, TIME:06:00 PM, TIME:06:00 PM |
| 208 | Attachment: You're invited to join Coursera!.eml | You're invited to join Coursera! | **ATTENDANCE** | 11.5% | MEDIUM | None | ROOM:online |
| 209 | Attachment: OE2 -Financial Derivatives -Div B lecture cancellation and M1 TEST details.eml | OE2 -Financial Derivatives -Div B lectur | **EVENT** | 11.2% | HIGH | None | DATE:2026-08-20, TIME:06:00 PM, TIME:04:00 PM |
| 210 | Attachment: FW: Approval for Extra lecture -FIMIS  (OE -2) - Theory.eml | FW: Approval for Extra lecture -FIMIS  ( | **ACADEMIC** | 11.2% | HIGH | None | DATE:2026-10-09, DATE:2026-10-09, DATE:2026-10-09 |
| 211 | Attachment: OE2 -IES extra lecture schedule.eml | OE2 -IES extra lecture schedule | **EVENT** | 11.0% | HIGH | YES: IES extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, ROOM:room

 CR |
| 212 | Attachment: RE: Revised M2 test schedule - OE1 Wireless Communication for Everybody..eml | RE: Revised M2 test schedule - OE1 Wirel | **EXAM** | 11.8% | HIGH | YES: Class / Examination Schedule Change (New Date) | DATE:2026-10-12, DATE:2026-10-19, TIME:04:00 PM |
| 213 | Attachment: RE: Reg: Missed Class test due to medical reason.eml | RE: Reg: Missed Class test due to medica | **ATTENDANCE** | 11.2% | HIGH | None | DATE:2026-10-10 |
| 214 | Attachment: DAA lab extra practical schedule - MBA Tech-AI, Sem V.eml | DAA lab extra practical schedule - MBA T | **EXAM** | 11.7% | HIGH | None | DATE:2026-10-09, DATE:2026-10-23, TIME:10:00 AM |
| 215 | Attachment: New Announcement: MPSTME ODD Semester Final Exam Timetable A Y 2026 27 send  for course.eml | New Announcement: MPSTME ODD Semester Fi | **EXAM** | 12.5% | HIGH | None |  |
| 216 | Attachment: OE2 -Life Skills  extra tutorial schedule.eml | OE2 -Life Skills  extra tutorial schedul | **GENERAL** | 12.2% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:06:00 PM, ROOM:room

CR |
| 217 | Attachment: OE2 Financial Derivatives –DIV B  extra lecture schedule.eml | OE2 Financial Derivatives –DIV B  extra  | **CLASSROOM / TIMETABLE** | 11.9% | HIGH | YES: DIV B extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, ROOM:room
CR-502 |
| 218 | Attachment: RE: Book Review Writing Competition - 2026.eml | RE: Book Review Writing Competition - 20 | **GENERAL** | 11.7% | LOW | None | DATE:2026-10-15, ROOM:online |
| 219 | Attachment: Attendance Report_70512400043.eml | Attendance Report_70512400043 | **ATTENDANCE** | 15.7% | HIGH | None |  |
| 220 | Attachment: Reg: Change of venue for NLP M2 test on 07.10.2026 - MBA Tech-AI, Sem V.eml | Reg: Change of venue for NLP M2 test on  | **GENERAL** | 11.5% | HIGH | None | TIME:04:00 PM, SUBJECT:NLP |
| 221 | Attachment: IS - II extra practical schedule - MBA Tech-AI, Sem V.eml | IS - II extra practical schedule - MBA T | **EXAM** | 11.6% | HIGH | None | ROOM:conference room



Link, ROOM:lab


2, SUBJECT:II extra |
| 222 | Attachment: IS- II extra lecture scheduled on 15.10.2026 - MBA Tech-AI, Sem V.eml | IS- II extra lecture scheduled on 15.10. | **EXAM** | 11.4% | HIGH | None | TIME:11:00 AM, SUBJECT:II extra |
| 223 | Attachment: Your weekly learning snapshot is here 📊.eml | Your weekly learning snapshot is here 📊 | **EXAM** | 10.9% | MEDIUM | None |  |
| 224 | Attachment: OE1 -SCADA extra practical Batch 1 schedule.eml | OE1 -SCADA extra practical Batch 1 sched | **EXAM** | 11.7% | HIGH | YES: SCADA extra Schedule Change (New Date) | DATE:2026-10-06, DATE:2026-10-27, TIME:00:00 PM |
| 225 | Attachment: Important: Mandatory Coursera Course Completion for Academic Credits.eml | Important: Mandatory Coursera Course Com | **EXAM** | 11.1% | MEDIUM | None | DATE:2026-10-10, DATE:2026-10-10 |
| 226 | Attachment: Last call.eml | Last call | **REGISTRATION** | 11.7% | MEDIUM | None | ROOM:room full |
| 227 | Attachment: Monthly Thematic e-Books Display on "Gandhi Jayanti "  – 2nd October 2026. .eml | Monthly Thematic e-Books Display on "Gan | **EVENT** | 10.9% | MEDIUM | None | DATE:2026-10-02, DATE:2026-10-02, DATE:2026-10-02 |
| 228 | Attachment: Now live: real practice, right inside Copilot.eml | Now live: real practice, right inside Co | **WORKSHOP** | 12.1% | MEDIUM | None |  |
| 229 | Attachment: OE2 Financial derivatives –DIV A lecture cancelled on 01.10.2026.eml | OE2 Financial derivatives –DIV A lecture | **ACADEMIC** | 12.6% | HIGH | YES: DIV A Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, SUBJECT:DIV A |
| 230 | Attachment: OE2 Elements of Project Management extra lecture schedule.eml | OE2 Elements of Project Management extra | **EVENT** | 10.9% | HIGH | None | DATE:2026-10-09, DATE:2026-10-16, DATE:2026-10-23 |
| 231 | Attachment: Bloomberg Global Trading Challenge 2026 – Registration Open.eml | Bloomberg Global Trading Challenge 2026  | **EVENT** | 12.5% | MEDIUM | None | DATE:2026-08-31, DATE:2026-10-04, DATE:2026-10-12 |
| 232 | Attachment: FW: M1- Coursera- AI Receptive Software Development - MBA Tech-AI, Sem V.eml | FW: M1- Coursera- AI Receptive Software  | **EXAM** | 11.2% | HIGH | None | DATE:2026-10-01, TIME:03:45 PM |
| 233 | Attachment: MAD extra practical B1 batch scheduled on 17.10.2026 - MBA Tech-AI, Sem V.eml | MAD extra practical B1 batch scheduled o | **EXAM** | 11.5% | HIGH | None | TIME:10:00 AM, SUBJECT:MAD extra |
| 234 | Attachment: OE1 -Basic decision making with Spreadsheet extra lecture / practical schedule.eml | OE1 -Basic decision making with Spreadsh | **EXAM** | 11.1% | HIGH | YES: Spreadsheet extra Schedule Change (New Date) | DATE:2026-10-05, DATE:2026-10-12, DATE:2026-10-06 |
| 235 | Attachment: Your weekly learning snapshot is here 📊.eml | Your weekly learning snapshot is here 📊 | **EXAM** | 11.1% | MEDIUM | None |  |
| 236 | Attachment: OE2 TIM extra lecture schedule.eml | OE2 TIM extra lecture schedule | **EXAM** | 11.3% | HIGH | YES: TIM extra Schedule Change (New Date) | DATE:2026-10-01, DATE:2026-10-01, DATE:2026-10-15 |
| 237 | Attachment: OE1 - Engineering Materials for Daily Life lecture cancellation details.eml | OE1 - Engineering Materials for Daily Li | **ACADEMIC** | 12.2% | HIGH | YES: Materials for Daily Life Schedule Change (New Date) | ROOM:room


7, SUBJECT:Materials for Daily Life |
| 238 | Attachment: MAD extra lecture and practical scheduled on 03.10.2026 - MBA Tech-AI, Sem V.eml | MAD extra lecture and practical schedule | **EXAM** | 11.4% | HIGH | None | TIME:10:00 AM, SUBJECT:MAD extra lecture and |
| 239 | Attachment: Developers across JAPAC have already registered!.eml | Developers across JAPAC have already reg | **REGISTRATION** | 11.3% | MEDIUM | None |  |
| 240 | Attachment: FW: NMIMS x Coursera Student Office Hours.eml | FW: NMIMS x Coursera Student Office Hour | **ATTENDANCE** | 11.4% | MEDIUM | None | DATE:2026-09-29, TIME:04:00 PM, TIME:04:50 PM |
| 241 | Attachment: Class Test – 2 (M2) schedule of B Tech & MBA Tech AI, Sem III, V & VII_Term I AY 26-27.eml | Class Test – 2 (M2) schedule of B Tech & | **GENERAL** | 12.2% | HIGH | None |  |
| 242 | Attachment: Important Notice – Unauthorised Outstation Trips and Student Safety.eml | Important Notice – Unauthorised Outstati | **ATTENDANCE** | 11.4% | MEDIUM | None |  |
| 243 | Attachment: SHOURYA GUPTA - 70022600757 wants to access 'Unplanned day 2'.eml | SHOURYA GUPTA - 70022600757 wants to acc | **ATTENDANCE** | 11.0% | MEDIUM | None |  |
| 244 | Attachment: RE: MAD extra lecture and practical scheduled on 26.09.2026 - MBA Tech-AI, Sem V.eml | RE: MAD extra lecture and practical sche | **GENERAL** | 11.4% | HIGH | None | TIME:10:00 AM, TIME:02:00 PM, SUBJECT:MAD extra lecture and |
| 245 | Attachment: Microsoft 365 security: You have messages in quarantine.eml | Microsoft 365 security: You have message | **GENERAL** | 11.1% | HIGH | None | DATE:2026-24-09, DATE:2026-24-09, TIME:22:54 AM |
| 246 | Attachment: OE-2 Financial derivatives –DIV A lecture cancellation and re-schedule details.eml | OE-2 Financial derivatives –DIV A lectur | **EVENT** | 11.4% | HIGH | YES: DIV A Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, TIME:06:00 PM |
| 247 | Attachment: LAVANYA KHANDELWAL - 70372200002 (LAVANYA.KHANDELWAL02@nmims.in) has created an anonymous access link to "Conference_Paper_UAE_v2 (1) (1)_3411.docx".eml | LAVANYA KHANDELWAL - 70372200002 (LAVANY | **EXAM** | 10.6% | MEDIUM | None | DATE:2026-23-09, TIME:05:55 AM |
| 248 | Attachment: Microsoft 365 security: You have messages in quarantine.eml | Microsoft 365 security: You have message | **EVENT** | 11.2% | HIGH | None | DATE:2026-23-09, DATE:2026-22-09, DATE:2026-22-09 |
| 249 | Attachment: Attendance Defaulter list -II (Term I_AY 2026-27).eml | Attendance Defaulter list -II (Term I_AY | **ATTENDANCE** | 13.5% | MEDIUM | None | DATE:2026-09-20 |
| 250 | Attachment: OE2 - LTLS lecture cancellation details.eml | OE2 - LTLS lecture cancellation details  | **ACADEMIC** | 12.2% | HIGH | YES: LTLS Schedule Change (New Date) | TIME:04:00 PM, TIME:05:00 PM, TIME:00:00 PM |
| 251 | Attachment: Presentations.eml | Presentations | **EVENT** | 10.8% | HIGH | None |  |
| 252 | Attachment: Professional Development Opportunities for Narsee Monjee Institute of Management Studies (NMIMS) Students.eml | Professional Development Opportunities f | **EVENT** | 10.9% | MEDIUM | None | ROOM:Online |
| 253 | Attachment: Fw: Important: Download Required Turnitin Reports/Data Before Platform Migration.eml | Fw: Important: Download Required Turniti | **GENERAL** | 11.4% | LOW | None |  |
| 254 | Attachment: OE2 - FIMIS - Div A extra lecture schedule.eml | OE2 - FIMIS - Div A extra lecture schedu | **EXAM** | 11.3% | HIGH | None | DATE:2026-10-23, TIME:05:00 PM, TIME:06:00 PM |
| 255 | Attachment: RE: Urgent- On-line Faculty feedback submission - Term I- B. Tech /MBA Tech/ M Tech-DS & AI (2026-27).eml | RE: Urgent- On-line Faculty feedback sub | **EXAM** | 11.1% | MEDIUM | None | DATE:2026-11-01, DATE:2026-11-01, ROOM:online |
| 256 | Attachment: Attendance Defaulter list - Term I_AY 2026-27.eml | Attendance Defaulter list - Term I_AY 20 | **ATTENDANCE** | 13.5% | MEDIUM | None | DATE:2026-10-18 |
| 257 | Attachment: OE2 - FIMIS - Div B extra lecture schedule.eml | OE2 - FIMIS - Div B extra lecture schedu | **EXAM** | 11.3% | HIGH | YES: Div B extra Schedule Change (New Date) | TIME:05:00 PM, TIME:06:00 PM, SUBJECT:Div B extra |
| 258 | Attachment: OE2 - LTLS - Div. A lecture cancelled on 23.10.2026.eml | OE2 - LTLS - Div. A lecture cancelled on | **ACADEMIC** | 11.4% | HIGH | YES: Kindly note Schedule Change (New Date) | TIME:04:00 PM, TIME:05:00 PM, TIME:05:00 PM |
| 259 | Attachment: FW: Reminder: Re-Test (M3) for Missed cases for M1 and M2 for genuine reasons for APR on 22-10-2026.eml | FW: Reminder: Re-Test (M3) for Missed ca | **EXAM** | 10.6% | MEDIUM | None | DATE:2026-10-22, DATE:2026-10-22 |
| 260 | Attachment: Attendance Report_70512400043.eml | Attendance Report_70512400043 | **ATTENDANCE** | 15.7% | HIGH | None |  |
| 261 | Attachment: OE2 - Introduction to Forensic Science -Div B lectures cancelled on 22 & 23 October, 2026.eml | OE2 - Introduction to Forensic Science - | **ACADEMIC** | 11.8% | MEDIUM | YES: Kindly note Schedule Change (New Date) | DATE:2026-10-23, SUBJECT:Kindly note |
| 262 | Attachment: OE1 -Basic decision making with spreadsheet extra and re-schedule lecture / practical.eml | OE1 -Basic decision making with spreadsh | **EXAM** | 11.3% | HIGH | YES: Class / Examination Schedule Change (New Date) | DATE:2026-10-27, DATE:2026-10-21, DATE:2026-10-26 |
| 263 | Attachment: OE2 -LTLS -Div B extra lecture schedule.eml | OE2 -LTLS -Div B extra lecture schedule | **GENERAL** | 12.0% | HIGH | YES: Div B extra Schedule Change (New Date) | TIME:00:00 PM, TIME:00:00 PM, SUBJECT:Div B extra |
| 264 | Attachment: OE1 Industrial Ergonomics extra lecture schedule.eml | OE1 Industrial Ergonomics extra lecture  | **EXAM** | 11.2% | HIGH | None | DATE:2026-10-27, TIME:00:00 PM, TIME:00:00 PM |
| 265 | Attachment: RE: Change in lecture venue on 30.10.2026 due to MUN Event - MBA Tech-AI, Sem V.eml | RE: Change in lecture venue on 30.10.202 | **CLASSROOM / TIMETABLE** | 13.8% | HIGH | YES: Change in Schedule Change (New Date) | TIME:02:00 PM, SUBJECT:Change in |
| 266 | Attachment: Presentations.eml | Presentations | **EVENT** | 10.8% | HIGH | None |  |
| 267 | Attachment: DIYA RAJPAL - 70512400067 (DIYA.RAJPAL67@nmims.in) has changed an anonymous access link to "FoodieOrder_Assignment1.zip".eml | DIYA RAJPAL - 70512400067 (DIYA.RAJPAL67 | **GENERAL** | 10.6% | MEDIUM | None | DATE:2026-18-10, TIME:11:03 AM |
| 268 | Attachment: Narsee Monjee Institute of Management Studies (NMIMS) First Notice: Professional Development Program under META SkillsBuild.eml | Narsee Monjee Institute of Management St | **ATTENDANCE** | 10.5% | MEDIUM | None | ROOM:Online, ROOM:online |
| 269 | Attachment: RE: Department Elective for Term II-Sem VI_AY 26-27 - B Tech & MBA Tech-AI, III yr..eml | RE: Department Elective for Term II-Sem  | **EXAM** | 10.8% | MEDIUM | None | DATE:2026-10-17, DATE:2026-10-17, DATE:2026-10-17 |
| 270 | Attachment: OE1 Renewable Energy Sources lecture re-schedule.eml | OE1 Renewable Energy Sources lecture re- | **GENERAL** | 11.5% | HIGH | YES: Renewable Energy Sources Schedule Change (New Date) | DATE:2026-10-19, DATE:2026-10-27, DATE:2026-11-03 |
| 271 | Attachment: Your weekly learning snapshot is here 📊.eml | Your weekly learning snapshot is here 📊 | **EXAM** | 11.1% | MEDIUM | None |  |
| 272 | Attachment: Change in OE2  - IFS lecture venue on 18.09.2026.eml | Change in OE2  - IFS lecture venue on 18 | **CLASSROOM / TIMETABLE** | 12.7% | HIGH | YES: IFS Schedule Change (New Date) | TIME:06:00 PM, SUBJECT:IFS |
| 273 | Attachment: Change in venue of OE1 EOA on 21.09.2026 and 22.09.2026.eml | Change in venue of OE1 EOA on 21.09.2026 | **CLASSROOM / TIMETABLE** | 12.5% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:04:00 PM, TIME:06:00 PM, TIME:05:00 PM |
| 274 | Attachment: Classroom for OE2 Life Skills.eml | Classroom for OE2 Life Skills  | **GENERAL** | 13.3% | HIGH | None | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 275 | Attachment: Monthly Thematic e-Books Display on "Kargil Vijay Diwas – 26 July ".eml | Monthly Thematic e-Books Display on "Kar | **EXAM** | 10.8% | HIGH | None | DATE:2026-07-26, DATE:2026-07-26, DATE:2026-07-26 |
| 276 | Attachment: OE-1 : Basic Decision Making with Spreadsheet theory / practical cancellation.eml | OE-1 : Basic Decision Making with Spread | **EVENT** | 11.3% | HIGH | YES: Kindly note Schedule Change (New Date) | ROOM:room

 CC-803, SUBJECT:Kindly note |
| 277 | Attachment: Advisory for Students to deal with Cyber Fraud / Unauthorized Calls.eml | Advisory for Students to deal with Cyber | **GENERAL** | 14.0% | LOW | None |  |
| 278 | Attachment: Venue change for OE2 subjects - Sem V.eml | Venue change for OE2 subjects - Sem V | **GENERAL** | 12.3% | HIGH | None | ROOM:room change |
| 279 | Attachment: FW: User Manual - GR PROCESS.eml | FW: User Manual - GR PROCESS | **GENERAL** | 11.8% | HIGH | None | TIME:00:00 PM, ROOM:online |
| 280 | Attachment: OE2 –Financial Derivatives - Div A - lecture cancelled on 24.7.2026.eml | OE2 –Financial Derivatives - Div A - lec | **ACADEMIC** | 11.3% | HIGH | YES: Kindly note Schedule Change (New Date) | TIME:04:00 PM, TIME:05:00 PM, TIME:06:00 PM |
| 281 | Attachment: OE2 –Creativity and Ethics in Marketing lecture cancelled on 24.7.2026.eml | OE2 –Creativity and Ethics in Marketing  | **ACADEMIC** | 12.5% | HIGH | YES: Ethics in Marketing Schedule Change (New Date) | TIME:04:00 PM, TIME:05:00 PM, SUBJECT:Ethics in Marketing |
| 282 | Attachment: SVKM's Narsee Monjee Institute of Management Studies (NMIMS) First Notice: Professional Development Program under META SkillsBuild.eml | SVKM's Narsee Monjee Institute of Manage | **ATTENDANCE** | 10.5% | MEDIUM | None | ROOM:Online, ROOM:online |
| 283 | Attachment: OE2 - Advertising and PR lecture cancellation and re-schedule details.eml | OE2 - Advertising and PR lecture cancell | **EVENT** | 11.6% | HIGH | YES: Advertising and PR Schedule Change (New Date) | DATE:2026-07-23, DATE:2026-07-24, TIME:05:00 PM |
| 284 | Attachment: OE1 -Interior Design re-schedule details.eml | OE1 -Interior Design re-schedule details | **EVENT** | 11.9% | HIGH | YES: Kindly note Schedule Change (New Date) | DATE:2026-07-20, DATE:2026-07-21, DATE:2026-07-28 |
| 285 | Attachment: OE1 -Drone Technology Pr B2 batch cancelled on 22.07.2026.eml | OE1 -Drone Technology Pr B2 batch cancel | **ACADEMIC** | 12.9% | MEDIUM | YES: Kindly note Schedule Change (New Date) | DATE:2026-07-22, TIME:06:00 PM, SUBJECT:Kindly note |
| 286 | Attachment: Clarification Regarding OE1 -Smart Cities Lecture Session.eml | Clarification Regarding OE1 -Smart Citie | **GENERAL** | 11.6% | HIGH | None | SUBJECT:Smart Cities |
| 287 | Attachment: Payment Receipt 020000586266.eml | Payment Receipt 020000586266 | **FEES** | 14.4% | HIGH | None |  |
| 288 | Attachment: Payment Receipt 020000586266.eml | Payment Receipt 020000586266 | **FEES** | 14.4% | HIGH | None |  |
| 289 | Attachment: Payment Receipt 020000586266.eml | Payment Receipt 020000586266 | **FEES** | 12.5% | MEDIUM | None | DATE:0403-21-07 |
| 290 | Attachment: OE1 -Interior Design lecture cancelled on 21.07.2026.eml | OE1 -Interior Design lecture cancelled o | **ACADEMIC** | 15.1% | MEDIUM | YES: Interior Design Schedule Change (New Date) | DATE:2026-07-21, TIME:05:00 PM, SUBJECT:Interior Design |
| 291 | Attachment: FW: Empowering the Next Generation of Finance Professionals | Bloomberg Education We.eml | FW: Empowering the Next Generation of Fi | **ATTENDANCE** | 11.6% | HIGH | None | ROOM:online, ROOM:room engagement, ROOM:room learning |
| 292 | Attachment: Revised Open Elective 1 & 2 time table.eml | Revised Open Elective 1 & 2 time table | **EXAM** | 11.1% | HIGH | None | TIME:00:00 PM, TIME:00:00 PM |
| 293 | Attachment: OE1 -Interior Design lecture cancelled on 20.07.2026.eml | OE1 -Interior Design lecture cancelled o | **ACADEMIC** | 14.8% | MEDIUM | YES: Interior Design Schedule Change (New Date) | DATE:2026-07-20, TIME:06:00 PM, SUBJECT:Interior Design |
| 294 | Attachment: RE: Introduction to ERP I and II.eml | RE: Introduction to ERP I and II  | **REGISTRATION** | 10.7% | HIGH | None | TIME:00:00 PM |
| 295 | Attachment: OE1 -Sustainable Energy Technologies lecture cancellation and re-schedule details.eml | OE1 -Sustainable Energy Technologies lec | **ACADEMIC** | 11.6% | HIGH | YES: Energy Technologies Schedule Change (New Date) | DATE:2026-07-20, DATE:2026-07-21, DATE:2026-08-04 |
| 296 | Attachment: OE1 -Basic decision making with spreadsheet lecture cancelled on 20.07.2026 - Sem V.eml | OE1 -Basic decision making with spreadsh | **ACADEMIC** | 12.2% | HIGH | YES: Kindly note Schedule Change (New Date) | SUBJECT:Kindly note |
| 297 | Attachment: Change in lab venue- MBA Tech & B Tech-AI, Sem V w.e.f. 20.07.2026.eml | Change in lab venue- MBA Tech & B Tech-A | **GENERAL** | 11.3% | HIGH | None | ROOM:Lab
CL, ROOM:Lab
4, ROOM:lab venue |
| 298 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EVENT** | 11.2% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 299 | Attachment: Greetings and Introductory Message : Prof. Sougata Ray, Vice Chancellor.eml | Greetings and Introductory Message : Pro | **EXAM** | 11.2% | MEDIUM | None | SUBJECT:Artificial Intelligence |
| 300 | Attachment: OE 2 Life Skills tutorial cancelled on 17.07.2026 - Sem V.eml | OE 2 Life Skills tutorial cancelled on 1 | **ACADEMIC** | 12.8% | MEDIUM | YES: Kindly note Schedule Change (New Date) | TIME:05:00 PM, SUBJECT:Kindly note |
| 301 | Attachment: IS -II Pr B1 &  B2 batch cancelled on 20.07.2026 - MBA Tech-AI -Sem V.eml | IS -II Pr B1 &  B2 batch cancelled on 20 | **GENERAL** | 11.2% | MEDIUM | YES: Kindly note Schedule Change (New Date) | TIME:04:00 PM, SUBJECT:Kindly note |
| 302 | Attachment: Team Code for OE1 Research Methodology odd 2026-27.eml | Team Code for OE1 Research Methodology o | **GENERAL** | 11.4% | LOW | None | SUBJECT:Research Methodology |
| 303 | Attachment: OE2 TIM lecture cancellation and re-schedule details.eml | OE2 TIM lecture cancellation and re-sche | **EVENT** | 11.4% | HIGH | YES: TIM Schedule Change (New Date) | DATE:2026-07-17, DATE:2026-07-24, TIME:04:00 PM |
| 304 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EXAM** | 11.3% | HIGH | None | ROOM:LAB MBA, ROOM:online, SUBJECT:You have been added to a |
| 305 | Attachment: Change in practical  venue w.e.f. 20.07.2026 - MBA Tech-AI, Sem V.eml | Change in practical  venue w.e.f. 20.07. | **GENERAL** | 11.5% | HIGH | None | TIME:02:00 PM, SUBJECT:Computer Networks |
| 306 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **ATTENDANCE** | 11.3% | HIGH | None | ROOM:online, SUBJECT:You have been added to a |
| 307 | Attachment: RE: OE1 Division details - Sem III & V.eml | RE: OE1 Division details - Sem III & V | **GENERAL** | 12.1% | LOW | None | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 308 | Attachment: RE: OE2 Division/CR /Life Skills Th/Tuts-BTech_MBA Tech_BTI  26-27.eml | RE: OE2 Division/CR /Life Skills Th/Tuts | **GENERAL** | 11.8% | LOW | None | TIME:00:00 PM, TIME:00:00 PM, TIME:00:00 PM |
| 309 | Attachment: OE-2- FINANCIAL DERIVATIVES lecture cancellation and re-schedule details- Sem V.eml | OE-2- FINANCIAL DERIVATIVES lecture canc | **EVENT** | 11.4% | HIGH | YES: FINANCIAL DERIVATIVES Schedule Change (New Date) | DATE:2026-07-16, DATE:2026-07-17, TIME:04:00 PM |
| 310 | Attachment: NMIMS Knowledge Trendsetters – Volume 5 (Issue 3) | Indigenous Intelligence: Learning from IKS.eml | NMIMS Knowledge Trendsetters – Volume 5  | **EVENT** | 11.2% | HIGH | None |  |
| 311 | Attachment: reg. OE Engineering Materials for Daily Life.eml | reg. OE Engineering Materials for Daily  | **GENERAL** | 13.0% | LOW | YES: Class / Examination Schedule Change (New Date) |  |
| 312 | Attachment: FW: Link to join MS Team for the subject OE - I, Smart Cities.eml | FW: Link to join MS Team for the subject | **GENERAL** | 13.9% | LOW | None |  |
| 313 | Attachment: OE1 - Wireless Communication for Everybody practical batches.eml | OE1 - Wireless Communication for Everybo | **EXAM** | 11.5% | HIGH | None | TIME:06:00 PM, TIME:06:00 PM, SUBJECT:Artificial Intelligence |
| 314 | Attachment: Time Table: Sem I, MBA.Tech AI/IT (2023-24): Div A.eml | Time Table: Sem I, MBA.Tech AI/IT (2023- | **EXAM** | 11.2% | HIGH | None |  |
| 315 | Attachment: Lab/ classroom shifting from 24th July to 15th August 2023.eml | Lab/ classroom shifting from 24th July t | **CLASSROOM / TIMETABLE** | 17.7% | HIGH | YES: Class / Examination Schedule Change (New Date) | DATE:2026-07-24, DATE:2023-08-15, DATE:2026-07-24 |
| 316 | Attachment: New Links in for Literary Workshop Submission.eml | New Links in for Literary Workshop Submi | **GENERAL** | 15.3% | MEDIUM | None |  |
| 317 | Attachment: B Tech and  MBA Tech Class teachers / mentors  Sem I 2023-24.eml | B Tech and  MBA Tech Class teachers / me | **EXAM** | 11.0% | MEDIUM | None |  |
| 318 | Attachment: Link for Student Information Handouts AY 2023.eml | Link for Student Information Handouts AY | **GENERAL** | 15.1% | LOW | None |  |
| 319 | Attachment: Enactus Mpstme is Recruiting!.eml | Enactus Mpstme is Recruiting! | **EVENT** | 11.5% | MEDIUM | None | DATE:2023-07-28, DATE:2023-07-26, TIME:08:00 PM |
| 320 | Attachment: IEC Core Recruitments 23-24'.eml | IEC Core Recruitments 23-24' | **EVENT** | 11.3% | MEDIUM | None | DATE:2026-07-29, DATE:2026-07-27 |
| 321 | Attachment: Information regarding COURSERA.eml | Information regarding COURSERA | **EXAM** | 11.2% | MEDIUM | None | ROOM:online |
| 322 | Attachment: CIRCULAR - Closure of university on 27th July, 2023.eml | CIRCULAR - Closure of university on 27th | **GENERAL** | 17.6% | HIGH | None | DATE:2026-07-27, DATE:2023-07-27, TIME:08:00 PM |
| 323 | Attachment: Revised Timetable.eml | Revised Timetable | **GENERAL** | 16.9% | LOW | None |  |
| 324 | Attachment: Change in Lab.eml | Change in Lab | **GENERAL** | 14.6% | HIGH | None | ROOM:Lab 21, ROOM:Lab 25 |
| 325 | Attachment: Counsellor Desk.eml | Counsellor Desk | **EVENT** | 12.4% | HIGH | None |  |
| 326 | Attachment: You have been added to a team in Microsoft Teams.eml | You have been added to a team in Microso | **EXAM** | 11.1% | HIGH | None |  |
| 327 | Attachment: Fresher's welcome event.eml | Fresher's welcome event | **EVENT** | 11.9% | HIGH | None |  |
| 328 | Attachment: Lecture Reschedule Details.eml | Lecture Reschedule Details | **CLASSROOM / TIMETABLE** | 13.4% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:12:00 PM, TIME:14:00 PM |
| 329 | Attachment: Leave Application.eml | Leave Application | **GENERAL** | 12.7% | HIGH | None |  |
| 330 | Attachment: Lecture Cancellation 07.08.2023.eml | Lecture Cancellation 07.08.2023 | **CLASSROOM / TIMETABLE** | 12.6% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:12:00 PM, TIME:13:00 PM |
| 331 | Attachment: MPSTME library on 7th Floor.eml | MPSTME library on 7th Floor | **GENERAL** | 11.1% | HIGH | None | ROOM:room booking, ROOM:online |
| 332 | Attachment: Enrollment to NDLI club of MPSTME.eml | Enrollment to NDLI club of MPSTME | **EVENT** | 12.3% | MEDIUM | None |  |
| 333 | Attachment: Student portal login credentials.eml | Student portal login credentials | **GENERAL** | 17.4% | LOW | None |  |
| 334 | Attachment: You have been added to a class team in Microsoft Teams.eml | You have been added to a class team in M | **EXAM** | 11.3% | MEDIUM | None | SUBJECT:You have been added to a |
| 335 | Attachment: Lecture Rescheduled 11.08.2023.eml | Lecture Rescheduled 11.08.2023 | **CLASSROOM / TIMETABLE** | 11.6% | HIGH | YES: Physics Schedule Change (New Date) | TIME:12:00 AM, TIME:01:00 PM, SUBJECT:Physics |
| 336 | Attachment: AYUSH MANOJ GARG - 70512300051 is trying to reach you in Microsoft Teams.eml | AYUSH MANOJ GARG - 70512300051 is trying | **ATTENDANCE** | 11.2% | HIGH | None | ROOM:online |
| 337 | Attachment: ID card wearing is mandatory.eml | ID card wearing is mandatory | **EXAM** | 11.4% | MEDIUM | None | DATE:2023-08-14 |
| 338 | Attachment: Change in labs from 16th August, 2023 onwards.eml | Change in labs from 16th August, 2023 on | **GENERAL** | 15.0% | HIGH | None | DATE:2026-08-16 |
| 339 | Attachment: Extra Class scheduled on 21.08.2023.eml | Extra Class scheduled on 21.08.2023 | **GENERAL** | 11.9% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:08:00 AM, TIME:09:00 AM, TIME:08:00 AM |
| 340 | Attachment: Portal Announcement.eml | Portal Announcement | **GENERAL** | 15.1% | LOW | None |  |
| 341 | Attachment: Lecture Rescheduled 22.08.2023.eml | Lecture Rescheduled 22.08.2023 | **ACADEMIC** | 11.2% | HIGH | YES: Class / Examination Schedule Change (New Date) | TIME:03:00 PM, TIME:05:00 PM |
| 342 | Attachment: M1 Test Schedule and Portion.eml | M1 Test Schedule and Portion | **GENERAL** | 14.6% | HIGH | None |  |
| 343 | Attachment: Enrollment to NDLI club of MPSTME.eml | Enrollment to NDLI club of MPSTME | **EVENT** | 12.5% | MEDIUM | None |  |
| 344 | Attachment: Library Orientation session.eml | Library Orientation session | **ATTENDANCE** | 10.9% | HIGH | None | DATE:2023-09-01, DATE:2023-09-08, DATE:2023-09-09 |
| 345 | Attachment: Physics.eml | Physics | **GENERAL** | 12.4% | HIGH | None | TIME:01:00 PM |
| 346 | Attachment: Attendance Report_70512300028.eml | Attendance Report_70512300028 | **ATTENDANCE** | 14.1% | HIGH | None |  |
| 347 | Attachment: Shutdown of power supply for switchover - 16.12.2023 from 5.30 pm onwards.eml | Shutdown of power supply for switchover  | **GENERAL** | 11.8% | HIGH | None | TIME:30:00 PM, TIME:30:00 PM, TIME:30:00 PM |