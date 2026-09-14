# Personal Finance Tracker

A single-page personal finance tracker: income, expenses, loans, FDs, SIPs,
owned stocks, and a fully-calculated dashboard. Vanilla HTML/CSS/JS, no
build tools, no dependencies.

## Run it

Open `index.html` with a local server (e.g. VS Code's "Open with Live
Server" extension). ES modules require `http://`/`https://` — opening the
file directly (`file://`) will not work.

## Data

All data is stored in the browser's `localStorage` under the key
`pft:state`. Nothing leaves your machine. Clearing site data resets the app
to the sample seed data.

## Tabs

- **Dashboard** — 9 derived values (income, expenses, EMI, SIP, net cash
  flow, outstanding debt, FD value, SIP contributed, stocks invested) and
  quick-add forms for salary and expenses.
- **Income & Expenses** — add/delete income and expenses, filter expenses
  by category.
- **Investments** — loans (amortized outstanding balance), fixed deposits
  (simple-interest estimated value), SIPs (contributed-to-date), and owned
  stocks (add/delete/edit).
- **Stocks to Watch** — a fixed sample watchlist for learning purposes.
  Not live prices, not investment advice.
