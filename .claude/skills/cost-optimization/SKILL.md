---
name: cost-optimization
description: Build a phased cost-down roadmap for a hardware product, especially one derived from a higher-volume parent. Use for cost-roadmap "Product" or when asked to plan cost optimization / design-to-cost for a product.
---

# Cost Optimization — Phased Cost-Down Roadmap

Produces a cost-optimization roadmap for an assembled hardware product. Optimized for **derivative products** (built from a higher-volume parent): the shared parts ride platform volume, the unique parts carry the premium, and that split drives the priorities.

## Steps

1. Read `methodologies/cost-optimization/roadmap.md` — the phased method and the output shape. Apply it literally.
2. Gather what the workspace already knows about the product before asking the user:
   - Any BOM / parts model (e.g. a `work/lead-time-planner/products/*.json` for this product — it already lists parts, lead times, stock status, and process steps).
   - The initiative profile in `knowledge/initiatives/` if the product belongs to one (for volume, qualification status, team, constraints).
3. Establish the parent relationship. Ask which product this derives from, and treat every shared part as platform-owned (flag, don't optimize) and every unique part as the target set.
4. Confirm the qualification state. If a customer is qualifying or has qualified the product, mark the configuration frozen and route cost changes through a tracked change lane. This is a hard guardrail.
5. Write the roadmap to `work/cost-optimization/<product-slug>-cost-roadmap.md` using the output shape from the methodology: plain-language summary, cost-structure map, four phases (transparency → quick wins → design-to-cost → scale), guardrails, data-needed list, governance/KPIs.
6. List the Phase 0 data inputs needed to put numbers on it, and offer to build the yield-adjusted should-cost model once the user supplies BOM actuals.

## Rules

- Phase 0 (cost transparency) comes first. Do not propose optimizations before there is a should-cost model and a target cost, but you may draft the roadmap structure with figures marked pending.
- Never propose a change that breaks an active customer qualification without flagging the sign-off requirement.
- Optimize the derivative's unique parts. For shared/parent parts, flag findings to the platform owner; do not fork the platform.
- Trigger scale levers (tooling, automation, second sourcing) on a computed volume threshold, not on the calendar.
- Cost is per *good* unit (yield-adjusted), never per started unit.
- Output is local only — cost models and roadmaps are commercially sensitive (`work/cost-optimization/` is git-ignored).
