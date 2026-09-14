<!-- sipcode:start v=2 -->
<!-- sipcode:block name="output-compression" mode="default" -->
## Sipcode Output Compression

mode: default — optimizes for: diff edits, no ceremony

the rules below apply to your responses in this project. follow them.
they exist so the user pays for code, not for ceremony.
### rules (default mode)

1. **diff-only edits.** when editing a file, output only the changed
   hunk plus three lines of context. never paste the full file back
   when three lines changed. this is the single biggest win.
2. **no preamble.** skip "i'll help with that", "sure", "here's what
   i did". lead with the work. the user can see what you did.
3. **no post-amble.** don't summarize what was just shown unless the
   user explicitly asks for a summary.
4. **code over prose.** when the answer is code, the code is the
   answer. any explanation goes after the code block, not before.
5. **bullets over paragraphs** for any list of options, steps, or
   trade-offs. saves tokens versus flowing prose.
6. **one canonical example, not three.** show one good example. skip
   the exhaustive variants — the user will ask if they want more.
7. **no filler verbs.** drop "let me", "i'll go ahead and", "i'm
   going to". just do the thing.

(installed by sipcode. switch modes with `npx sipcode rules --mode <m>`.
uninstall with `npx sipcode rules --uninstall`.)

## Project architecture

Vanilla JS, ES modules, no build step. Served via a local dev server (e.g.
VS Code Live Server) — `file://` won't work because of module imports.

- `js/state.js` — single mutable `state` object, the one source of truth.
  All mutations go through named exported functions (`addIncome`,
  `deleteLoan`, etc.) that persist to `localStorage` then call `notify()`.
  No other module touches `state` directly or manipulates the DOM.
- `js/render.js` — subscribes to state via `subscribe(render)`. On every
  change, rebuilds the active tab panel's `innerHTML` from scratch
  (immediate-mode rendering, no diffing/vdom).
- `js/views/*.js` — one render function per tab, pure functions of
  `(panel, state) -> void` that set `panel.innerHTML`.
- `js/app.js` — the only place with real event listeners, delegated on
  `document` (`click`/`submit`/`change`). Listeners read `data-action` /
  `data-id` / `data-tab` attributes so they survive full DOM rebuilds.
- `js/calculations.js` — pure functions only, no side effects. Loan
  outstanding balance uses standard amortization; FD current value is
  simple interest (explicitly labelled as an estimate); SIP
  contributed-to-date counts elapsed calendar months.
- `js/format.js` — `escapeHTML` (XSS safety for all user-entered strings
  interpolated into templates), `formatINR` (₹, Indian digit grouping),
  `formatDate` (manual y/m/d parsing to avoid UTC-parsing off-by-one),
  `uid()`.

Data persists to `localStorage` under key `pft:state`, with corrupt-data
self-healing: invalid/missing JSON falls back to seed data and
immediately re-persists a valid copy.
<!-- /sipcode:block -->

<!-- sipcode:end -->
