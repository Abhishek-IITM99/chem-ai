# Follow the Money — Research File (v1)
> Purpose: Before fixing our problem statement, map **where money is actually flowing** in (1) company-funded academic research and (2) consulting/industrial-software firms. Then narrow our wedge to a problem that real budgets already exist for.
>
> Team: 3 founders | IIT Madras | Chemical Engineering + ML | Target: Hub71 Abu Dhabi (ClimateTech / AI)
> Date: 2026-06-27 | Status: DRAFT — raw research, not yet conclusions

---

## How to read this file
Two tasks the team agreed on:
- **Task 1 — Academia money:** Where are companies paying universities to do research? Which problems?
- **Task 2 — Consulting money:** Where are the big consulting + industrial-software firms getting paid? To solve which problems?

Each section ends with a **"Signal for us"** note. The final section (§5) synthesizes into candidate wedges. Every number has a source link at the bottom of its section — treat market-size figures as *directional* (analyst reports vary widely), and trust the *direction and ranking* more than the exact dollar value.

---

# TASK 1 — Flow of Funds in Academia (company-paid research)

### 1.1 The headline: fossil-fuel & industrial money is deeply embedded in university research
- Oil & gas companies have funded climate/energy research at top universities (US, UK, Canada, Australia) for **30+ years**.
- **MIT Energy Initiative** has raised **>$1 billion** for energy research since 2006 — **~45% from oil & gas companies**.
- Documented cases of companies steering *what* gets researched — e.g., ExxonMobil's influence over carbon-capture projects at Louisiana State University.
- 750+ academics signed a 2022 letter pushing to ban fossil-fuel funding of climate research → signals just how large and entrenched the money is.

**Signal for us:** Industrial/energy incumbents already pay heavily for *applied* research in energy efficiency and carbon. A startup that productizes that research (rather than re-running it) is selling into an existing willingness-to-pay.

### 1.2 Government co-funding is huge and points at the same problems
The same problems attract matched public money — useful because it tells us what's considered nationally strategic:
- **US DOE / NETL**: multiple recent university programs — $17M, $8M, $2.5M tranches — explicitly for **decarbonization & net-zero GHG** tech and training.
- **DOE OCED**: **$1.3 billion** new funding to bolster **CCUS** technologies; another **$54.4M** to expand carbon-management tech portfolio.
- **NSF C-CAS** (Center for Computer-Assisted Synthesis), **AFOSR/AFRL D3OM2S** (data-driven discovery of optimized materials) — AI-for-chemistry/materials is a funded national priority.

### 1.3 The specific research themes companies are paying for (ChemE × AI)
From 2024–2026 ChemE/AI literature and centers, the recurring funded themes:
1. **Surrogate / hybrid models** — ML models that replace expensive unit-operation simulations, embedded in plant-scale optimization. (This is "self-learning digital twin" in academic language.)
2. **AI for catalyst design & reaction optimization** — heavily NSF/industry co-funded.
3. **Time-series pre-trained transformers** applied to chlor-alkali, thermal power, petrochemical operations (vendor-reported efficiency/quality/safety gains).
4. **LLM systems for chemical-engineering knowledge/workflows** — emerging.
- Example industry-embedded center: **Innovation Centre in Digital Molecular Technologies**, co-funded by industrial members + University of Cambridge.

**Signal for us:** The academic frontier most aligned to our ChemE+ML team is **hybrid/surrogate modeling for plant optimization** — i.e., physics + ML digital twins. That is exactly the "ThermoTwin" thesis, and it's *funded science*, not just a pitch.

**Sources (Task 1):**
- [Fossil fuel funding embedded across academia — Inside Climate News](https://insideclimatenews.org/news/06092024/todays-climate-fossil-fuels-funding-university/)
- [DOE $17M university decarbonization projects — NETL](https://netl.doe.gov/node/13236) · [DOE $8M](https://www.energy.gov/hgeo/articles/doe-announces-8-million-university-training-and-research-decarbonization-and-net-zero) · [DOE $54.4M carbon mgmt — NETL](https://netl.doe.gov/node/14045) · [OCED $1.3B CCUS — DOE](https://www.energy.gov/oced/articles/oced-announces-13-billion-new-funding-bolster-carbon-capture-utilization-and-storage)
- [AI in chemical engineering: from promise to practice — AIChE Journal 2026](https://aiche.onlinelibrary.wiley.com/doi/10.1002/aic.70358)
- [Advancing ChemE with AI — Oxford Clean Energy](https://academic.oup.com/ce/article/9/5/55/8263023)

---

# TASK 2 — Where Consulting & Industrial-Software Firms Get Paid

### 2.1 Strategy consultancies (MBB) — energy + AI is the cash engine
- **McKinsey** ranks #1 in energy consulting (Global Energy & Materials practice + **QuantumBlack** AI analytics). **~40% of McKinsey client work now includes AI.**
- **BCG**: **AI consulting = ~20% of 2024 revenue**; hired 1,000+ staff for AI demand. Partnered with **Anthropic (Claude)**.
- **Bain**: #4 in energy; strong on PE value-creation in energy; partnered with **OpenAI**.
- Big Four + strategy houses collectively poured **>$10B into AI initiatives since 2023**.

### 2.2 The system integrators / Big Four — industrial AI productized into "agents"
- **Accenture**: FY2025 revenue **$69.7B** (Consulting $35.1B / Managed Services $34.6B). **AI revenue tripled to $2.7B**; GenAI bookings **$5.9B**. Launched **"AI Refinery for Industry"** — 12 industry agent solutions, including **"Asset Troubleshooting for Industrial"** (multi-agent troubleshooting to cut downtime, shift maintenance reactive→proactive). Energy practice explicitly sells **decarbonization pathways + energy-system optimization**.
- **Deloitte**: FY2025 revenue **$70.5B**; heavy on enterprise transformation; annual "State of AI in the Enterprise" report.

### 2.3 Industrial-software vendors — the incumbents we'd actually compete/partner with
This is the most important sub-section for us — these companies *sell software that does what we're describing*:
- **AspenTech** (majority owned by **Emerson**) — leads process optimization & ChemE simulation; expanded into power-grid management 2024–25.
- **AVEVA** (Schneider Electric) — TTM revenue **~$1.55B** (mid-2025).
- **Honeywell** (Forge / Process Solutions) — dominant in Advanced Process Control (APC) + OT/IT.

**Relevant market sizes (directional):**
| Market | 2024/25 | Forecast | CAGR |
|---|---|---|---|
| Advanced Process Control (APC) software | $2.48B (2025) | $5.51B (2035) | 8.3% |
| Process Simulation & Optimization software | $5.18B (2024) | $9.2B (2035) | ~6% |
| Digital Twin — **process segment** | part of $21B (2025) total | $150B+ (2030) total mkt | ~40% (process twins) |
| Digital Twin in **Oil & Gas** | $1.33B (2025) | $3.11B (2033) | 11–26% (sources vary) |
| AI-driven energy optimization (industrial) | — | **>$12B by 2030** | — |
| AI in manufacturing | $34B (2025) | **$155B by 2030** | 35% |

**Signal for us:** The "real-time energy optimization" and "self-learning digital twin" space is **not empty** — AspenTech/AVEVA/Honeywell own it, and Accenture is wrapping it in agents. Our wedge must be something **they do badly or don't bother with** (see §5).

**Sources (Task 2):**
- [Top energy consulting firms — ManagementConsulted](https://managementconsulted.com/top-energy-consulting-firms/) · [AI forcing MBB to rethink fees — TheStreet](https://www.thestreet.com/markets/ai-is-forcing-mckinsey-bcg-bain-to-rethink-consulting-fees)
- [Accenture AI Refinery for Industry](https://newsroom.accenture.com/news/2025/accenture-launches-ai-refinery-for-industry-to-reinvent-processes-and-accelerate-agentic-ai-journeys) · [Accenture energy Tech Vision 2025](https://www.accenture.com/us-en/blogs/energy/technology-vision-2025-harnessing-ai-transformative-power-energy-sector)
- [Advanced Process Control market — SNS Insider](https://www.snsinsider.com/reports/advanced-process-control-market-5642) · [Process Simulation & Optimization mkt](https://www.verifiedmarketreports.com/product/process-simulation-and-optimization-software-market/) · [AspenTech profile](https://pitchgrade.com/companies/aspen-technology-inc) · [AVEVA competitive landscape](https://matrixbcg.com/blogs/competitors/aveva)
- [AI in manufacturing $155B by 2030 — MarketsandMarkets](https://www.marketsandmarkets.com/PressReleases/artificial-intelligence-manufacturing.asp) · [Digital twin in oil & gas — Astute](https://www.globenewswire.com/news-release/2025/11/05/3181359/0/en/Latest-Digital-Twin-in-Oil-Gas-Market-to-Reach-US-1-137-32-Million-by-2033-Astute-Analytica.html)

---

# §3 — Abu Dhabi / ADNOC: where the *local* money is going (Hub71 fit)
The most concrete buyer in our pitch geography. ADNOC is spending real money on exactly this category:
- **ENERGYai** platform — built with **AIQ** (JV) + **Microsoft** + **G42**; AI agents + LLM trained on ADNOC's value-chain workflows. Trial showed **70% improvement in seismic interpretation accuracy** + reservoir/anomaly detection gains.
- **$14.7B** (AED 54B) to UAE suppliers for local tech ecosystem; **$920M** AI-powered well-digitalization program; **$340M** to AIQ to deploy ENERGYai.
- ADNOC reports **$500M value generated from 30+ AI systems** (2024), matching all of 2023 — and is shifting **from pilots to enterprise-wide deployment** in 2025.
- Decarbonization: **$23B committed** to low-carbon; net-zero gas projects (Hail & Ghasha); CCUS target **10 mtpa CO₂ by 2030**, Net Zero by 2045, **$15B** initial low-carbon allocation.

**Signal for us:** ADNOC is already buying enterprise AI for operations and decarbonization. A pre-MVP startup will **not** displace AIQ/Accenture on a core platform — but Hub71's whole model is to plug startups in as **specialized layers/suppliers** to this ecosystem. Our wedge should be a *specific, hard sub-problem* their big platforms underserve.

**Sources:** [ADNOC AI for Energy](https://www.adnoc.ae/en/artificial-intelligence/ai-for-energy) · [ADNOC AI initiatives 2025 — EnkiAI](https://enkiai.com/adnoc-ai-initiatives-for-2025-key-projects-strategies-and-partnerships) · [ADNOC Net-Zero / CCUS FID](https://www.adnoc.ae/en/news-and-media/press-releases/2023/adnoc-takes-fid-on-worlds-first-project-that-aims-to-operate-with-net-zero-emissions)

---

# §4 — The competitive & funding climate (who else is chasing this)
- **AI = ~half of all global VC in 2025** (>$160B in 9 months) — capital is abundant but crowded.
- **Digital-twin VC is hot**: Neara (power-grid digital twin) raised **$63M Series D → unicorn**; physics-informed twin startups (e.g., Inviscid AI) funded for HVAC/building optimization.
- **CCUS funding inflecting**: global CCS investment heading toward **$80B by 2030** (DNV); US alone **270+ projects / $77.5B** announced; Wood Mackenzie sees a **$196B** US CCUS opportunity over 10 yrs. CCUS share of climate-tech funding rose **5×** (0.7%→3.5%) since 2020. Investors favor **utilization** (revenue-generating output) over pure removal — note for the M.Tech gas-hydrate angle.

### The single most important demand signal for our wedge
- **Poor data quality is the #1 reason industrial AI fails:** S&P Global 2025 — **42% of companies abandoned most AI initiatives** (up from 17% in 2024); avg org scrapped **46% of AI POCs** before production. RAND — **>80% of AI projects fail** to reach production. **56% of manufacturers** name data challenges as the #1 barrier; **52%** cite poor system integration. Informatica — data quality/readiness is the top obstacle (43%).

**Signal for us:** This validates the *"Poor Data Quality"* problem already written at the top of `trio.md`. The market is loudly telling us the bottleneck isn't fancier optimization algorithms — it's **getting industrial data clean, contextualized, and model-ready**. The incumbents (Aspen/AVEVA) assume good data; the consultancies bill huge hours fixing it by hand.

**Sources:** [AI/climate biggest rounds 2025](https://entrepreneurloop.com/ai-climate-tech-funding-largest-rounds-2025/) · [Neara $63M — SiliconANGLE](https://siliconangle.com/2026/02/09/digital-twin-startup-neara-raises-63m-help-power-companies-cope-ais-energy-demands/) · [$80B CCS surge — CarbonCredits](https://carboncredits.com/80b-surge-in-carbon-capture-investments-by-2030/) · [CCUS 2025 review — Carbon Herald](https://carbonherald.com/ccus-in-2025-an-end-of-year-review/) · [Poor data quality 42–85% failures — WebProNews](https://www.webpronews.com/poor-data-quality-to-cause-42-85-ai-project-failures-in-2025/) · [AI in manufacturing fails without quality data — Quality Magazine](https://www.qualitymag.com/articles/99678-why-ai-in-manufacturing-fails-without-quality-data)

---

# §5 — Synthesis: where the money points (for our problem definition)
> This is the "so what." Not a decision yet — a ranked read of the evidence.

**Three places money is clearly flowing, ranked by fit for a 3-person pre-MVP ChemE+ML team:**

1. **Industrial data quality / contextualization layer ("make plant data AI-ready").**
   - *Money evidence:* It's the named #1 blocker (42–56% failure stats); consultancies bill it by hand; vendors assume it away.
   - *Why us:* ChemE domain knowledge is the moat — knowing that a tag is wrong requires process understanding, not just data science. Easiest to validate without a giant platform.
   - *Risk:* Less glamorous; harder to frame as "ClimateTech" (but framable as "the enabler of decarbonization AI").

2. **Self-learning hybrid digital twin for energy/CO₂ optimization (the ThermoTwin thesis).**
   - *Money evidence:* Funded academic frontier (surrogate/hybrid models); $12B+ AI energy-optimization market; ADNOC actively buying; APC + sim markets ~$8–14B combined.
   - *Why us:* Directly matches our skills + Hub71/ADNOC narrative.
   - *Risk:* AspenTech/AVEVA/Honeywell/Accenture already here. We'd need a sharp, narrow entry (one unit op, one KPI) — not a platform.

3. **CCUS / decarbonization economics (utilization-favored, ties to M.Tech gas-hydrate work).**
   - *Money evidence:* $80B+ CCS by 2030, ADNOC 10 mtpa target, investors favor revenue-generating utilization.
   - *Why us:* Real research asset (M.Tech). Strongest pure-ClimateTech Hub71 framing.
   - *Risk:* Capital-intensive, long cycles, further from "software startup" — but a *software/optimization layer on top of CCUS* could be a wedge.

**Working hypothesis to test next:** Lead with **#1 (data-quality/contextualization) as the wedge**, positioned as *"the data foundation that makes energy/CO₂ optimization (#2) actually work"* — so #2 is the vision and #1 is the entry product. This matches both the failure-rate evidence AND our domain edge, and keeps the ClimateTech story intact for Hub71.

---

# §6 — Open gaps / next research tasks
- [ ] Quantify **what consultancies charge** for industrial-data-cleanup / historian projects (proves willingness-to-pay for wedge #1).
- [ ] Map **direct competitors** doing industrial data contextualization (e.g., Cognite, Palantir Foundry, TwinThread, Seeq, Toumetis) — funding, pricing, gaps.
- [ ] Find **Indian refinery / petrochem** access points (IOCL, BPCL, Reliance, ADNOC-India links) for pilot data — feeds our 3-month validation.
- [ ] Pull **2 primary sources** per claim before pitch (analyst reports vary; cite IEA, S&P, DOE directly).
- [ ] Check **Hub71+ ClimateTech Cohort 20** deadline + whether data-foundation framing qualifies as ClimateTech.

> Reminder: market-size numbers here are analyst estimates and disagree with each other. For the pitch, cite the *direction* (huge + growing + budgeted) and lean on the *demand signals* (ADNOC spend, AI-failure stats) which are harder to dispute.
