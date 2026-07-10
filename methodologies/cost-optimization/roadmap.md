# Cost Optimization Roadmap — Methodology

A phased method for driving down the unit cost (COGS) of an assembled hardware product, especially one **derived from a higher-volume parent product**. The parent relationship is the central lever: parts shared with the parent ride existing volume; parts unique to the derivative carry a low-volume premium. That asymmetry decides where the money is.

Apply the phases in order. Do not skip Phase 0 — every later decision depends on it.

## Principles

1. **Measure before you optimize.** A cost you cannot see, you cannot prioritize. Cost per *good* unit, not per started unit.
2. **Qualification is sacred.** If a customer is qualifying or has qualified the product, no cost change ships without their sign-off. Run cost changes as a tracked engineering-change lane against a frozen configuration.
3. **Attack the delta, not the platform.** Optimize the parts unique to the derivative. Flag findings on shared/parent parts to the platform owner; do not fork the platform.
4. **Lead time is cost.** Long-lead and single-source parts are cash and expedite risk, not just calendar risk.
5. **Trigger scale levers on volume, not on the calendar.** Tooling and automation pay back above a unit threshold you compute from Phase 0 numbers, not on a hunch.
6. **No silent truncation.** If the analysis bounds coverage (top-N parts, one supplier quote), say so.

## Phase 0 — Cost transparency (start first)

Deliverable: a one-page yield-adjusted should-cost model.

- Pull actual or quoted cost per BOM line from ERP / supplier quotes.
- Add labor at loaded rates per process step (durations come from the process flow; the lead-time planner already holds them if used).
- Add yield: capture first-pass yield, incoming reject rate, rework hours. Report cost per good unit.
- Pareto the result. Set a **target cost** tied to the business case (target margin or price). Without a target, every later discussion is opinion.

## Phase 1 — Quick wins, design untouched (0–6 months)

No requalification risk. Procurement and process only.

- Frame / volume agreements on the unique long-lead parts; reserve bottleneck raw material instead of spot buys.
- Volume-commit pricing on single-source or near-monopoly inputs (the only real lever there).
- Close open make/buy or material decisions that force duplicate stock, duplicate inspection, or duplicate calibration recipes.
- Second-source the easy, available parts (risk + price).
- Risk-based review of long test / burn-in steps once failure data exists: shorten, sample, or parallelize.
- Commercial review of commodity peripherals (customer-supplied option, separate line items so they stop diluting margin).

## Phase 2 — Design-to-cost on the derivative delta (6–18 months)

Touches the design. Gate every change against qualification status.

- **VAVE** on the cost-driving unique subsystem. Use existing engineering simulations to answer the money question (where can expensive material be trimmed or substituted).
- **DFM review** with the machining / fabrication supplier: tolerance relaxation on non-functional surfaces, near-net-shape blanks, combine parts always made together into one setup.
- **Commonality audit vs the parent.** Score every part shared / modified / unique. For each modified or unique part, ask whether the delta earns its premium. Raise the shared fraction each iteration.
- **Yield program.** Weekly yield review once units flow; every rework loop gets a root cause. This is where 10–30% of COGS typically hides in low-volume hardware.
- **Test-flow compression.** Script manual setup steps; merge test stations where fixtures allow.

## Phase 3 — Scale and platform levers (18–36 months, volume-triggered)

- **Family architecture.** Design shared subsystems once across product variants so NRE and tooling amortize. Do not let each variant become bespoke.
- **Second source** for the dominant single-source input at sustained volume (also improves pricing on the incumbent).
- **Material utilization.** Revisit blank sizes / tiling against raw-stock utilization with the supplier; material bought by area or mass is paid partly as offcut.
- **Dedicated tooling and automation.** Justify with Phase 0 numbers and the learning curve.
- **Learning-curve tracking.** Plot COGS per unit against cumulative units. Deviation above the expected curve flags a process problem; deviation below it is pricing headroom.

## Output shape

A markdown roadmap with: a plain-language summary, a qualitative cost-structure map from the BOM, the four phases with concrete actions, explicit guardrails (qualification freeze, lead-time-is-cost, don't-fork-the-platform), a "data needed to quantify" list, and a governance/KPI section. KPIs: yield-adjusted unit COGS, first-pass yield, unique-part count, bottleneck-part lead time, cost-vs-target waterfall.
