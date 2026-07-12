# ARC 5443 — Canvas Assignment Shells
## Summer 2026 · Kurt Neiswender, AIA

Copy each block below directly into Canvas's assignment text editor.
Each block is one Canvas assignment. The line after the title gives you the
Canvas settings to configure (points, submission type, availability dates).

---

## UNIVERSAL WEEKLY RUBRIC — 10 Points
### Apply to all five weekly deliverables (Weeks 1, 2, 4, 6, 7)

**How to add this to Canvas:**
Assignments → open the weekly assignment → Rubric → Add Rubric → create new.
Enter the two criteria below. Set "Use this rubric for assignment grading" on.
The rubric stays attached to each weekly assignment — build it once on Week 1,
then find it by name ("Weekly Deliverable") when adding it to subsequent weeks.

---

### Criterion 1 — Deliverable Package · 6 points

| Rating | Pts | Description |
|---|---|---|
| Complete & Engaged | 6 | All required components submitted. Technical output (model, screenshots, calculations, or analysis) demonstrates genuine effort and responds to the week's specific task. Work is legible and organized. |
| Complete, Thin | 4–5 | All components present but one or more show minimal effort — screenshots unlabeled, calculations incomplete, or analysis copied from the tutorial without application to the student's own room. |
| Incomplete | 2–3 | One required component missing, or the submitted work does not address the week's specific task (e.g., Week 2 script output absent, Week 4 daylighting analysis missing). |
| Minimal | 1 | Multiple components missing or work is placeholder quality (blank layers, no annotations, generic model with no student decisions visible). |
| Not submitted | 0 | Nothing submitted by the 48-hour grace period deadline. |

---

### Criterion 2 — Decision Log · 4 points

| Rating | Pts | Description |
|---|---|---|
| Connected & Specific | 4 | Required entries written and directly connected to this week's analysis. At least one entry references a specific number, calculation result, or published criterion from the week's work (e.g., "revised rear wall material after RT60 came in at 2.4 s, above my 1.6–1.8 s target"). Trade-off field completed. |
| Present, Descriptive | 2–3 | Entries written but reasoning is descriptive rather than analytical — documents *what* was done without explaining *why* or connecting to a calculation or criterion. Trade-off field thin or blank. |
| Absent or Disconnected | 1 | Entries missing, or entries present but show no connection to this week's technical work. |
| Not submitted | 0 | No Decision Log entries for the week, or Google Doc link not accessible. |

---

**Grading note:** A student who scores 6 + 4 = 10 has submitted everything and made their reasoning visible. A student who submits everything but writes no Decision Log can score at most 6/10. The log is not optional — it is half the grade on every weekly.

---
---

---
---

## UNGRADED — Decision Log Link

**Canvas settings:** Points: 0 · Submission: Text Entry · Available: Week 1

---

Share the link to your Google Doc Decision Log here. Make sure sharing is set to **"Anyone with the link can view"** — the instructor needs ongoing view access throughout the term.

**How to submit:**
1. Open your Decision Log Google Doc.
2. Click Share → Change to "Anyone with the link" → Viewer.
3. Copy the link and paste it into the text entry box below.

You only need to submit this once. If you make a new copy or move the doc, re-submit the updated link.

The instructor will check your live doc before each Act Review. The Canvas text submissions at Act close are timestamped snapshots for grading — the Google Doc is the primary working record.

---
---

## Week 1 Deliverable — Hall Volume & Program Declaration

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 05·26 · 11:59 PM

---

Your hall exists — on paper, in Rhino, and in your head. This deliverable captures your first committed geometry and starts your acoustic reasoning record.

**Submit three items:**

**1 — Rhino Model File (.3dm)**
Your hall volume with AEIS_ layers assigned to all room surfaces and an AEIS_SOURCE point placed at stage center (approximately 5 ft above floor level). Minimum four surface types: floor, walls, ceiling, and seating. The Week 2 RT60 script will run directly on this file.

**2 — Two Rhino Screenshots**
One plan view and one section view. The Rhino layer panel must be visible in at least one screenshot so material assignments are legible. Annotate (in Rhino or in a PDF overlay): seat count, stage dimensions, and ceiling height.

**3 — Program Declaration (150–200 words, paste into the text entry box)**
Write a short declaration covering:
- Your geometry type (shoebox, fan, vineyard, or horseshoe) and one acoustic reason you chose it
- Program: speech-primary, music-primary, or mixed
- NC target for the main hall and a different NC target for the prefunction lobby
- One acoustic trade-off you have already accepted (a consequence of your geometry or material choices)
- Your RT60 target range (e.g., "1.4–1.8 s for mixed program") — we will calculate whether your volume supports this in Week 2

**4 — Decision Log Entry 1**
Written in your Google Doc before submission. Entry 1 should document your geometry choice and the reasoning behind it. Gut response to the precedents counts here — but say *why*, not just *what*.

---

**Late work:** 48-hour grace period at no penalty. Beyond 48 hours: –20% per week. Work more than two weeks late will not be accepted without prior instructor approval.

---
---

## Week 2 Deliverable — RT60 Calculation & Script Output

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 06·02 · 11:59 PM

---

This week you run the numbers. By the end of this deliverable, your hall has a calculated RT60 and you know whether you need more absorption, less, or whether you landed in range on the first try.

**Submit four items:**

**1 — Updated Rhino Model (.3dm)**
Surfaces refined based on RT60 results. Layer assignments should be final or near-final for Act I close.

**2 — RT60 Hand Calculation Worksheet (PDF or scanned pages)**
Sabine and Eyring equations at 500 Hz, 1 kHz, and 2 kHz. Show all work:
- Room volume (V) and total surface area (S)
- A table listing each surface, its area (ft²), and its absorption coefficient at each octave band
- Total absorption (A) and mean absorption coefficient (ᾱ) per band
- RT60 from both Sabine and Eyring
- Your target RT60 at the top of the page, with the source citation (MEEB table number or published range)
- A note on which method is more conservative for your room and why

**3 — RT60 Script HTML Report**
The HTML file generated by aeis_rt60.py, plus at least one viewport screenshot showing the ray paths (layer AEIS_RAYS visible, energy-colored lines). If the script errored, include a screenshot of the error and a note on what you tried.

**4 — Comparison Note (paste into text entry, 3–5 sentences)**
Does your hand-calculation Eyring result agree with the script's Eyring output within ±0.2 s? If yes, note it. If no, identify the most likely source of the discrepancy (volume difference, material assignment mismatch, audience area not modeled, etc.). A clear explanation of a discrepancy satisfies the rubric as fully as a match.

**Decision Log Entry 2** must address a material or geometry change made in response to your RT60 result. If you hit target on the first run, note that and describe why your first choice worked.

---
---

## Act I Review — The Hall, Heard

**Canvas settings:** Points: 20 · Submission: File Upload + Text Entry · Due: Wed 06·10 · 11:59 PM

---

Act I closes with a two-part submission: a PDF package and a pasted Decision Log text entry. Both parts are required. A missing Decision Log text entry will score zero on Criterion 5 regardless of the quality of the PDF.

The full assignment brief, rubric, and submission instructions are in the **Act I Assignment document** posted in this module. Read it before you submit.

**Part 1 — PDF Package (file upload)**
Export everything into a single PDF. All items must be present:
- Acoustic plan and section (minimum 1/8" = 1' scale)
- RT60 worksheet (Sabine + Eyring, minimum 500 Hz, 1 kHz, 2 kHz)
- RT60 script HTML report + viewport screenshot showing ray paths
- Material schedule (minimum five distinct assemblies with NRC values cited)
- STC wall assembly for your critical partition
- Act I review slides from the Week 3 in-class pin-up (6–8 slides)

**Part 2 — Decision Log Text Paste (text entry)**
In the text entry box below the file upload, paste the full text of your Decision Log entries from Weeks 1–3. Do not summarize or edit — paste as written. Separate entries with a blank line.

**Rubric (20 points total — see Act I Assignment document for full criteria):**
- Criterion 1: Acoustic Geometry — 4 pts
- Criterion 2: Quantitative Analysis (RT60) — 4 pts
- Criterion 3: Material Strategy (NRC) — 4 pts
- Criterion 4: Noise Isolation (STC) — 4 pts
- Criterion 5: Decision Log Quality — 4 pts

NAAB alignment: SC.4B (primary) · SC.4E (secondary)

---
---

## Week 4 Deliverable — Daylighting Strategy

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Sat 06·20 · 11:59 PM (extended)

**Extension note (announced Week 5):** The original Tuesday deadline was extended to **Sat 06·20 · 11:59 PM** for the entire class, no late penalty. The Week 4 live session was canceled (instructor conference travel) and the LightStanza intro is being re-covered live in the Week 5 class (Wed 06·17). Students who already submitted may resubmit by the new deadline; otherwise their existing submission stands. Act II package deadline is unchanged (Wed 06·24 · 11:59 PM).

---

[CONTENT TBD — Act II / Daylighting. Update this block when Week 4 materials are finalized.]

Act II begins. This week you commit to a daylighting strategy for the hall: aperture type, orientation, and shading approach. Deliverable details will be posted in the Week 4 module before class.

**Placeholder checklist (update before posting):**
- [ ] Daylighting analysis output
- [ ] Aperture strategy diagram
- [ ] Decision Log entries for Week 4

---
---

## Act II Review — The Hall, Lit by Day

**Canvas settings:** Points: 20 · Submission: File Upload + Text Entry · Due: Wed 06·24 · 11:59 PM

---

[CONTENT TBD — Act II / Daylighting. Update this block when the Act II assignment and rubric are finalized.]

Act II closes with a daylighting package. Full brief, rubric, and submission instructions will be posted in the Act II Assignment document in this module.

**Placeholder checklist (update before posting):**
- [ ] Act II Assignment HTML built and posted
- [ ] Act II Rubric posted
- [ ] Submission instructions added here

---
---

## Week 6 Deliverable — Lighting Kickoff: First Lumen-Method Pass + Retrospectives

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 06·30 · 11:59 PM
**Rubric:** Universal Weekly Rubric (Deliverable Package 6 + Decision Log 4)

---

Act III opens. Tonight the sun went down and the switch became yours. This week you turn the lumen method into your first real lighting number, and you close out the two Acts behind you with a short written retrospective. Same two halves as every weekly — a package and a Decision Log — but this week the log is reflective.

**Part A — Package (file upload, PDF) · 6 pts**

A one-space lumen-method pass, written up from tonight's lab:

1. **Pick a space** — your prefunction (pairs with the Act II daylight work) or the house.
2. **Set the target** — maintained illuminance *E* in footcandles (and the lux equivalent), and cite the IES Lighting Handbook category you're designing to.
3. **Select a real luminaire** — a manufacturer cut sheet or IES file. Record **delivered (fixture) lumens Φ**, watts, CCT, CRI, and distribution type. Use *delivered* lumens, not lamp lumens.
4. **Justify CU and LLF** — one line each (CU 0.4–0.8 from room shape + reflectances; LLF 0.7–0.85 from dirt + lamp aging).
5. **Solve both directions** — `N = (E·A)/(Φ·CU·LLF)` for fixture count, then plug N back to report the achieved *E*. Round N to a buildable grid.
6. **Note installed watts** — N × fixture watts, as your first LPD data point (no full compliance yet — that's Week 8).

**Part B — Decision Log Text Paste (text entry) · 4 pts — Three Retrospectives**

In the text box, paste three short *Wins / Struggles / Goals* retrospectives. Three to five honest bullets per section; candor scores higher than polish.

- **Log 1 · Act I — Acoustics** — wins/struggles/goals on geometry, RT60, materials, STC. What did the tools (Rhino / Revit / Dynamo) get right or wrong for you?
- **Log 2 · Act II — Daylighting** — wins/struggles/goals on apertures, sDA/ASE, shading, and the acoustic–daylight trade-off. What would you change if you re-ran it?
- **Log 3 · This Week's Reading** — name what you read, then one win (a takeaway you'll use in Act III), one struggle (what was unclear or surprising), and one goal (a question you want to chase). This is the reading check — keep it real.

> Format note: *Wins* = what worked / what you'd repeat. *Struggles* = what fought you (a tool, a concept, the time, a number that wouldn't resolve). *Goals* = what you carry forward or do differently.

Keep tonight's lumen-method numbers — they grow into the Act III luminaire schedule in Week 7.

**Lecture + interactive calculator:** Week 6 lecture page (course hub → Lecture Notes → "Week 06 · Lighting").

---
---

## Week 7 Deliverable — Electrical Distribution & Load Calculation

**Canvas settings:** Points: 10 · Submission: File Upload + Text Entry · Due: Tue 07·07 · 11:59 PM

---

[CONTENT TBD — Act III / Electrical. Update when Week 7 materials are finalized.]

This week you build the load summary and begin panel schedule layout. Deliverable details will be posted in the Week 7 module before class.

**Placeholder checklist (update before posting):**
- [ ] Load calculation table requirements
- [ ] Panel schedule format
- [ ] Decision Log entries for Week 7

---
---

## Week 8 — No Separate Weekly (folds into Act III)

**Canvas settings:** Not a graded weekly. Do not post a Week 8 Deliverable — or if the shell already exists, open it and check *"Do not count this assignment toward the final grade."*

---

Week 8 is an in-class electrical + PV **work session** — there is no standalone weekly upload. The work students produce (circuits, panel schedule LP-1, the official LPD verdict, and PV sizing) folds directly into the **Act III package (due Tue 07·21)** and is graded there via the Act III rubric.

The graded weekly for the Week 7–8 stretch is the **Week 7 deliverable** (above). This keeps the Weekly Deliverables group at five items (Weeks 1, 2, 4, 6, 7); with Canvas weighted groups the group weight is unchanged.

---
---

## Act III Review — The Hall, Powered & Illuminated

**Canvas settings:** Points: 20 · Submission: File Upload + Text Entry · Due: Tue 07·21 · 11:59 PM

---

Act III closes with a two-part submission: a PDF package and a pasted Decision Log text entry. Both parts are required. A missing Decision Log text entry will score zero on Criterion 5 regardless of the quality of the PDF.

The full assignment brief, rubric, and submission instructions are in the **Act III Assignment document** posted in this module. Read it before you submit.

**Part 1 — PDF Package (file upload)**
Export everything into a single PDF. All items must be present:
- Lighting plan / reflected ceiling plan showing the four layers (house / egress / work / accent) and their control zones
- Lumen-method calculations for the key spaces (house, prefunction, stage/work light) — target E (fc + lux) with IES category, N solved both directions, achieved E, installed watts
- Illuminance analysis (LightStanza or Revit false-color maps) annotated against targets and compared to the hand calc
- Luminaire schedule — real fixtures with IES data: delivered lumens Φ, watts, CCT, CRI, distribution, mounting
- Electrical load summary + panel schedule (connected load by circuit, breaker sizes, totals)
- LPD compliance check — installed W/ft² vs. ASHRAE 90.1 / IECC allowance, pass/fail + response
- PV sizing calculation — array kW, module count, roof area to offset a stated load fraction
- Act III pin-up slides from the Week 9 in-class review (6–8 slides)

**Part 2 — Decision Log Text Paste (text entry)**
In the text entry box below the file upload, paste the full text of your Decision Log entries from Weeks 6–8. Do not summarize or edit — paste as written. Separate entries with a blank line.

**Rubric (20 points total — see Act III Assignment document for full criteria):**
- Criterion 1: Lighting Design & Illuminance — 4 pts
- Criterion 2: Luminaire Selection & Photometric Logic — 4 pts
- Criterion 3: Electrical Distribution & Load — 4 pts
- Criterion 4: Energy Performance (LPD & PV) — 4 pts
- Criterion 5: Decision Log Quality — 4 pts

Rating scale (matches Act II Criteria Builder): Exceeds (4) · Mastery (3) · Near (2) · Below (1) · No Evidence (0).

NAAB alignment: SC.4B (primary) · SC.4E (secondary)

The cross-system integration/tightening work — including any revision of the Act I RT60 results — carries into the Encore (Week 10).

---
---

## Encore — The Full Hall

**Canvas settings:** Points: 60 · Submission: File Upload + Text Entry · Due: Sun 07·26 · 11:59 PM
**Rubric:** Encore rubric — 6 criteria × 10 pts. Ratings: Exceeds (10) · Mastery (8) · Near (6) · Below (3) · No Evidence (0).

---

Three acts, three systems, one building. You heard it, you lit it by day, you powered it by night — each time in isolation. The Encore is where they finally share it.

The full assignment brief, rubric, and submission instructions are in the **Encore Assignment document** posted in this module. Read it before you submit — the criteria are published and there are no surprises in them.

**This is not a fourth act.** Act III closes Tue 07·21; the Encore is due Sun 07·26. Five days. Most of this package is work you have already done, assembled and *corrected*. Only three pieces are new writing:

1. **The Cross-System Integration Sheet** — at least three documented *collisions* where two systems wanted the same surface, the same watt, or the same opening. Each with the numbers on both sides, a named winner, and a stated cost. A real collision has a loser; if nothing gave way it was a coincidence. This is the heart of the assignment and it is worth as much as an entire act.
2. **The Week 9 Systems Addendum** — one page each on sound reinforcement (system type, speaker locations, a critical-distance check against your own RT60, the AV rack as a load on LP-1) and emergency/egress power (your egress layer as the emergency branch, the 10 s / 90 min / 1 fc criteria).
3. **The Final Retrospective** — Wins/Struggles/Goals across the term, plus: what would you do differently if you started this hall over on Monday?

**Part 1 — PDF Package (file upload)**
One PDF. All items present and labeled:
- Cover + project statement (200–300 words) — *new*
- Integrated plan & section set: one plan per system layer (acoustic / daylight / lighting-electrical) on a shared base and scale, plus a section through all three
- Act I summary sheet — acoustics (final RT60 Sabine + Eyring, NRC schedule, STC assembly, NC targets), **updated to reflect the building as actually designed**
- Act II summary sheet — daylight (sDA/ASE with LightStanza output, apertures, shading geometry, glare response, daylight-harvesting link to the electric layers)
- Act III summary sheet — lighting & electrical (lumen method, illuminance maps, luminaire schedule, panel LP-1, LPD verdict, PV sizing)
- **Cross-System Integration Sheet** — *new*
- **Week 9 Systems Addendum** — *new*
- Complete Decision Log, minimum 20 entries
- **Final Retrospective** — *new*

**Part 2 — Decision Log Text Paste (text entry)**
Paste the full log — all entries, Weeks 1 through 9 — plus the Final Retrospective. Do not summarize.

**Extra Credit — 5-Minute Walkthrough Video (optional, up to +5 pts)**
Screen-share, five minutes, no slides needed. Narrate a *decision*, not a drawing, and be honest about one failure. Upload the file alongside the PDF or paste an unlisted link at the top of your text entry. It cannot hurt you and it cannot push you above 60.

**Rubric (60 points total — see Encore Assignment document for full criteria):**
- Criterion 1: Acoustic Performance — 10 pts
- Criterion 2: Daylight Performance — 10 pts
- Criterion 3: Lighting, Electrical & Energy — 10 pts
- Criterion 4: **Cross-System Integration** — 10 pts
- Criterion 5: Decision Log — Complete Record — 10 pts
- Criterion 6: Package Craft & Communication — 10 pts
- *Extra credit: walkthrough video — up to +5 pts*

**Grading note:** Six Masteries = 48/60 (B) — the honest expected outcome for a student who did the work and found real conflicts. The A range requires the integration to actually bite.

NAAB alignment: SC.4B **and** SC.4E — both primary. The integration requirement is precisely the demonstration that the student can reason across environmental and service systems at once.

**Late work:** Standard policy — 48-hour grace, then –20% per week. On a 60-point assignment that is 12 points, more than half an Act Review. Submit something on time.

---

## Build Status

| Assignment | Status | Points | Due |
|---|---|---|---|
| Decision Log Link | ✅ Ready to post | 0 (ungraded) | Week 1 tonight |
| Week 1 Deliverable | ✅ Ready to post | 10 | Tue 05·26 |
| Week 2 Deliverable | ✅ Ready to post | 10 | Tue 06·02 |
| Act I Review | ✅ Ready to post — assignment + rubric attached | 20 | Wed 06·10 |
| Week 4 Deliverable | 🔲 TBD | 10 | Sat 06·20 |
| Act II Review (Week 6) | 🔲 TBD | 20 | Wed 06·24 |
| Week 6 Deliverable | ✅ Ready to post | 10 | Tue 06·30 |
| Week 7 Deliverable | 🔲 TBD | 10 | Tue 07·07 |
| Week 8 Deliverable | ❌ Dropped — folds into Act III (graded there) | — | — |
| Act III Review (Week 9) | ✅ Ready to post — assignment + rubric attached | 20 | Tue 07·21 |
| Encore | ✅ Ready to post — assignment + rubric attached | 60 (+5 XC) | Sun 07·26 |
| **Total (graded)** | | **170 pts** | |

**Note on course total:** Five weekly × 10 + 3 Act Reviews × 20 + Encore 60 = **170 pts graded**, plus 20 pts participation = 190 pts. (The Week 8 electrical/PV work is graded inside Act III, not as a separate weekly.) If your Canvas gradebook uses **weighted assignment groups**, the Weekly group keeps its full weight no matter the item count — dropping the Week 8 weekly needs no rescale. If it uses a **straight point scale**, the graded total is now 170 (190 with participation). Verify against the posted syllabus before publishing.
