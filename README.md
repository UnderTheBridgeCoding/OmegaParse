# OmegaParse
The last parser you'll ever need. 
# Omega Parse

**The last parser you’ll ever need.**

Omega Parse is a personal data ingestion, parsing, and normalization suite designed for **user‑exported archives**. It exists to turn fragmented histories (chat logs, media history, files) into a coherent, inspectable dataset you can analyze, study, and reuse.

This project is intentionally *boring* in the best way: deterministic, transparent, and bounded.

---

## What Omega Parse is

- A **local‑first** parser for data *you explicitly export*
- A **normalization layer** that converts many formats into a single event schema
- A foundation for analysis (frequency, clustering, context)
- A long‑term archival tool, not a real‑time system

Supported / current sources include:
- OpenAI data exports
- YouTube / YouTube Music (Google Takeout — CSV / JSON)
- Local files (CSV, JSON, TXT)

Further integrations may be added deliberately over time.

---

## What Omega Parse is *not*

- Not a scraper
- Not a crawler
- Not an automation tool against third‑party services
- Not a surveillance or monitoring system

Omega Parse does **not** log in to accounts, bypass APIs, or collect data without explicit user action.

If you didn’t export the data yourself, Omega Parse should not touch it.

---

## Design principles

- **Explicit input** — only user‑provided files
- **Canonical schema** — all sources collapse into the same event model
- **Deterministic transforms** — no hidden state, no opaque heuristics
- **Inspectability** — intermediate outputs are readable and auditable
- **Ethical boundaries** — no scraping, no silent collection

Omega Parse is a mirror, not a motor.

---

## Typical use cases

- Analyzing listening or viewing history
- Extracting training or research data from chat archives
- Normalizing long‑term personal data for reflection or tooling
- Building higher‑level analysis on top of clean, structured events

---

## License

Omega Parse is licensed under the **Business Source License (BSL) 1.1**.

- **Free to use** for individuals and organizations with **less than $1,000,000 USD in annual revenue**
- **Commercial use above that threshold requires a paid license**

This preserves openness for personal, research, and small-scale use while preventing silent commercial extraction.

See `LICENSE.txt` for full terms.

---

## Status

Omega Parse is early‑stage and evolving.

The focus is correctness, clarity, and long‑term coherence — not feature velocity.

Expect the architecture to stabilize before the surface area expands.
