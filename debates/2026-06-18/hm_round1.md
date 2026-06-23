# R1 · hm — Kimi Token Efficiency for MAGI Gold

## Problem

SOF test burned ~13% weekly quota (37%→24%) on 2 kimi calls. At this rate, 5 SOF documents = depleted.

kimi output pattern: 80% thinking/planning, 20% actual data.

## Solutions (ranked by impact)

### 1. Single call, all pages (HIGH impact)
One `kimi -p` covering all pages = 1 inference instead of N.
Current: 3 calls for 3-page SOF. Fixed: 1 call.
**Savings: 67% on multi-page documents.**

### 2. `--output-format stream-json` (HIGH impact)
Raw text output includes verbose thinking blocks. stream-json returns only the final message content.
**Savings: ~50% output tokens (thinking eliminated).**

### 3. Template caching (HIGH impact)
Same agent's SOF uses identical layout. After first verification of a template:
- Store field coordinates (e.g., "NOR time is at line 15, position 40-55")
- Subsequent SOFs from same agent: verify only changed fields (dates, times, cargo tons)
- Static fields (agent name, address, column headers) skip verification
**Savings: ~60% on repeat documents from same agent.**

### 4. Text-layer bypass (already implemented)
90%+ PDFs have embedded text layers → zlib extraction → no kimi needed.
Kimi only for scanned/image-based PDFs.
**Savings: 90% of all documents never hit kimi.**

### 5. Crop to relevant regions (MEDIUM impact)
Instead of sending full-page images, crop to the specific fields Gold needs.
Smaller images = fewer vision tokens.
**Savings: ~30% input tokens per call.**

### 6. Skip "obvious" fields (LOW impact)
Fields like "agent address" don't need visual verification — OCR is reliable for printed text.
Only verify fields where OCR errors would affect demurrage: dates, times, tonnages, weather events.
**Savings: ~20% input tokens per call.**

## Recommended MAGI Gold Dispatch (combined)

```
kimi -p "Read p1-pN. Output ONLY these fields as JSON: {nor, commenced, completed, cargo, weather:[{date,start,end,type}]}. No explanation." --output-format stream-json
```

Combined savings: ~85% vs naive multi-call approach.
