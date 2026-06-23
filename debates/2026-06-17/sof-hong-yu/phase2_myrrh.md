# Phase 2 · Myrrh (沒藥) — Adversarial Audit

## Attack: What breaks for demurrage?

### Attack Vector 1: Pages 2-3 not visually verified
Gold only verified page 1. Pages 2-3 weather events come from Tesseract OCR (confidence 0.60). If there are additional bad weather / heavy rain events on pages 2-3 that OCR missed or misread, the demurrage calculation will be wrong.

**Impact**: Demurrage = laytime allowed - laytime used. Bad weather pauses the laytime clock. Missing rain events → shipowner gets paid for time they shouldn't.

### Attack Vector 2: OCR "COMPLETED OF LOADING OCTOBER)" 
The closing paren after OCTOBER could indicate a missing digit. If the date was "OCTOBER 26" and the "26" is partially obscured, Commenced Loading might be a different date. Cross-referenced with line 486 which says "COMPLETED DISCHARGE FROM BG. MIL 3105 & FINISHED FOR LOADING" — this confirms Oct 26 is correct. **Risk: LOW, verified by cross-reference.**

### Attack Vector 3: NOR = Arrival time
Both are 17:00 on Oct 21. If NOR was tendered after arrival (e.g., 17:30), the laytime clock starts later → less demurrage. But kimi verified both are 17:00. **Risk: LOW.**

### Attack Vector 4: Total Cargo precision
71,800 MT is a round number. If actual cargo was 71,750 or 71,850, the difference could affect laytime calculation if laytime is rate-based (tons per day). But SOF cargo tons are typically used for B/L quantity, not laytime calculation. **Risk: LOW.**

### Attack Vector 5: Departure time accuracy
Departure Oct 26 10:15. If actual departure was earlier (e.g., 09:00), laytime ends earlier → less demurrage. But SOF is signed by shipper/agent — departure time is typically reliable. **Risk: LOW.**

## CRITICAL Finding

**Pages 2-3 not visually verified.** This is the single point of failure. If there are undetected heavy rain events on Oct 24 or Oct 25, the demurrage calculation is wrong — potentially by several hours. 

Recommendation: Run kimi on pages 2-3 when quota allows. Until then, flag pages 2-3 weather events as UNVERIFIED.

## Risk Topology

| Risk | Severity | Verifiable? |
|------|----------|-------------|
| Pages 2-3 weather unverified | CRITICAL | Yes — needs kimi |
| OCTOBER) OCR error | LOW | Verified by cross-ref |
| NOR=Arrival same-minute | LOW | Kimi verified |
| Cargo precision | LOW | Low impact |
| Departure time | LOW | Signed document |
