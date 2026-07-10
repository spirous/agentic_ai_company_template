# Lead-Time Planner

A single-file, offline tool for quoting the customer lead time of an assembled hardware product and working out the latest safe order date for every part.

## Use it

Open `lead-time-planner.html` in any browser. No server, no install, no network. Edits save automatically in that browser (localStorage); use **Export JSON** to keep a file per product and **Import JSON** to load one back.

## Model

- **Parts & supply** — one row per bought part. Cycle the source button: `order` (lead time counts from today), `stock` (available day 0), or `date` (a fixed arrival date, recalculated from today). The risk column is a buffer added on top.
- **Production steps** — run in order. Click part chips to say which parts a step waits for. A step starts when the previous step is done *and* every part it needs has arrived.
- **Dispatch buffer** — covers test surprises, packing, and shipping prep after the last step.

## Read the result

- **Customer lead time** and **ready-by date** assume everything is ordered today.
- The **orange chain** in the Gantt is the critical path. It sets the quote. Shorten it, or move its gating part onto stock, and the lead time drops.
- **Order-by dates** plans backwards from a wished delivery date and lists each part by urgency, flagging any that are already too late.

## Products

`products/` holds saved product models as JSON. `example-hardware-unit.json` ships with the template. Your own product models placed here stay local (git-ignored); only the example is versioned.
