import { escapeHTML, formatINR, formatDate } from '../format.js';
import { loanOutstandingBalance, fdCurrentValue, sipContributed, stockInvested } from '../calculations.js';

function renderLoanList(loans) {
  if (loans.length === 0) {
    return '<p class="empty-state">No loans added yet.</p>';
  }

  const rows = loans
    .map(
      (loan) => `
        <li class="list-row">
          <div>
            <strong>${escapeHTML(loan.name)}</strong>
            <div class="text-muted">EMI ${formatINR(loan.emi)} &middot; ${escapeHTML(loan.ratePct)}% p.a. &middot; ${escapeHTML(loan.monthsLeft)} months left</div>
          </div>
          <div class="form-row">
            <span>Outstanding: ${formatINR(loanOutstandingBalance(loan))}</span>
            <button type="button" class="btn btn-danger" data-action="delete-loan" data-id="${escapeHTML(loan.id)}">Delete</button>
          </div>
        </li>
      `
    )
    .join('');

  return `<ul class="list">${rows}</ul>`;
}

function renderFdList(fds) {
  if (fds.length === 0) {
    return '<p class="empty-state">No FDs added yet.</p>';
  }

  const rows = fds
    .map(
      (fd) => `
        <li class="list-row">
          <div>
            <strong>${escapeHTML(fd.name)}</strong>
            <div class="text-muted">Principal ${formatINR(fd.principal)} &middot; ${escapeHTML(fd.ratePct)}% p.a. &middot; ${formatDate(fd.startDate)} to ${formatDate(fd.maturityDate)}</div>
          </div>
          <div class="form-row">
            <span title="Simple-interest estimate, not compounded">Current value (est.): ${formatINR(fdCurrentValue(fd))}</span>
            <button type="button" class="btn btn-danger" data-action="delete-fd" data-id="${escapeHTML(fd.id)}">Delete</button>
          </div>
        </li>
      `
    )
    .join('');

  return `<ul class="list">${rows}</ul>`;
}

function renderSipList(sips) {
  if (sips.length === 0) {
    return '<p class="empty-state">No SIPs added yet.</p>';
  }

  const rows = sips
    .map(
      (sip) => `
        <li class="list-row">
          <div>
            <strong>${escapeHTML(sip.name)}</strong>
            <div class="text-muted">${formatINR(sip.monthly)}/month &middot; started ${formatDate(sip.startDate)}</div>
          </div>
          <div class="form-row">
            <span>Contributed to date: ${formatINR(sipContributed(sip))}</span>
            <button type="button" class="btn btn-danger" data-action="delete-sip" data-id="${escapeHTML(sip.id)}">Delete</button>
          </div>
        </li>
      `
    )
    .join('');

  return `<ul class="list">${rows}</ul>`;
}

function renderStockEditForm(stock) {
  return `
    <li class="list-row">
      <form data-action="save-stock" class="form-row">
        <input type="hidden" name="id" value="${escapeHTML(stock.id)}" />
        <div class="field">
          <label for="stock-edit-name-${escapeHTML(stock.id)}">Name</label>
          <input id="stock-edit-name-${escapeHTML(stock.id)}" name="name" type="text" required maxlength="60" value="${escapeHTML(stock.name)}" />
        </div>
        <div class="field">
          <label for="stock-edit-sector-${escapeHTML(stock.id)}">Sector</label>
          <input id="stock-edit-sector-${escapeHTML(stock.id)}" name="sector" type="text" required maxlength="40" value="${escapeHTML(stock.sector)}" />
        </div>
        <div class="field">
          <label for="stock-edit-qty-${escapeHTML(stock.id)}">Quantity</label>
          <input id="stock-edit-qty-${escapeHTML(stock.id)}" name="quantity" type="number" min="0" step="1" required value="${escapeHTML(stock.quantity)}" />
        </div>
        <div class="field">
          <label for="stock-edit-price-${escapeHTML(stock.id)}">Buy price (₹)</label>
          <input id="stock-edit-price-${escapeHTML(stock.id)}" name="buyPrice" type="number" min="0" step="0.01" required value="${escapeHTML(stock.buyPrice)}" />
        </div>
        <button type="submit" class="btn btn-primary">Save</button>
        <button type="button" class="btn" data-action="cancel-edit-stock">Cancel</button>
      </form>
    </li>
  `;
}

function renderStockRow(stock) {
  return `
    <li class="list-row">
      <div>
        <strong>${escapeHTML(stock.name)}</strong>
        <div class="text-muted">${escapeHTML(stock.sector)} &middot; ${escapeHTML(stock.quantity)} @ ${formatINR(stock.buyPrice)}</div>
      </div>
      <div class="form-row">
        <span>Invested: ${formatINR(stockInvested(stock))}</span>
        <button type="button" class="btn" data-action="start-edit-stock" data-id="${escapeHTML(stock.id)}">Edit</button>
        <button type="button" class="btn btn-danger" data-action="delete-stock" data-id="${escapeHTML(stock.id)}">Delete</button>
      </div>
    </li>
  `;
}

function renderStockList(stocks, editingStockId) {
  if (stocks.length === 0) {
    return '<p class="empty-state">No stocks added yet.</p>';
  }

  const rows = stocks
    .map((stock) => (stock.id === editingStockId ? renderStockEditForm(stock) : renderStockRow(stock)))
    .join('');

  return `<ul class="list">${rows}</ul>`;
}

export function renderInvestments(panel, state) {
  panel.innerHTML = `
    <h2>Investments</h2>

    <section class="card" aria-labelledby="loans-heading">
      <h3 id="loans-heading">Loans</h3>
      <form data-action="add-loan" class="form-row">
        <div class="field">
          <label for="loan-name">Name</label>
          <input id="loan-name" name="name" type="text" required maxlength="60" />
        </div>
        <div class="field">
          <label for="loan-emi">EMI (₹)</label>
          <input id="loan-emi" name="emi" type="number" min="0" step="1" required />
        </div>
        <div class="field">
          <label for="loan-rate">Rate (% p.a.)</label>
          <input id="loan-rate" name="ratePct" type="number" min="0" step="0.01" required />
        </div>
        <div class="field">
          <label for="loan-months">Months left</label>
          <input id="loan-months" name="monthsLeft" type="number" min="0" step="1" required />
        </div>
        <button type="submit" class="btn btn-primary">Add loan</button>
      </form>

      ${renderLoanList(state.loans)}
    </section>

    <section class="card section-gap" aria-labelledby="fds-heading">
      <h3 id="fds-heading">Fixed Deposits</h3>
      <p class="text-muted">Current value is a simple-interest estimate from the principal, rate, and dates you enter &mdash; not a bank-quoted figure.</p>
      <form data-action="add-fd" class="form-row">
        <div class="field">
          <label for="fd-name">Name</label>
          <input id="fd-name" name="name" type="text" required maxlength="60" />
        </div>
        <div class="field">
          <label for="fd-principal">Principal (₹)</label>
          <input id="fd-principal" name="principal" type="number" min="0" step="1" required />
        </div>
        <div class="field">
          <label for="fd-rate">Rate (% p.a.)</label>
          <input id="fd-rate" name="ratePct" type="number" min="0" step="0.01" required />
        </div>
        <div class="field">
          <label for="fd-start">Start date</label>
          <input id="fd-start" name="startDate" type="date" required />
        </div>
        <div class="field">
          <label for="fd-maturity">Maturity date</label>
          <input id="fd-maturity" name="maturityDate" type="date" required />
        </div>
        <button type="submit" class="btn btn-primary">Add FD</button>
      </form>

      ${renderFdList(state.fds)}
    </section>

    <section class="card section-gap" aria-labelledby="sips-heading">
      <h3 id="sips-heading">SIPs</h3>
      <form data-action="add-sip" class="form-row">
        <div class="field">
          <label for="sip-name">Name</label>
          <input id="sip-name" name="name" type="text" required maxlength="60" />
        </div>
        <div class="field">
          <label for="sip-monthly">Monthly (₹)</label>
          <input id="sip-monthly" name="monthly" type="number" min="0" step="1" required />
        </div>
        <div class="field">
          <label for="sip-start">Start date</label>
          <input id="sip-start" name="startDate" type="date" required />
        </div>
        <button type="submit" class="btn btn-primary">Add SIP</button>
      </form>

      ${renderSipList(state.sips)}
    </section>

    <section class="card section-gap" aria-labelledby="stocks-heading">
      <h3 id="stocks-heading">My Stocks</h3>
      <form data-action="add-stock" class="form-row">
        <div class="field">
          <label for="stock-name">Name</label>
          <input id="stock-name" name="name" type="text" required maxlength="60" />
        </div>
        <div class="field">
          <label for="stock-sector">Sector</label>
          <input id="stock-sector" name="sector" type="text" required maxlength="40" />
        </div>
        <div class="field">
          <label for="stock-quantity">Quantity</label>
          <input id="stock-quantity" name="quantity" type="number" min="0" step="1" required />
        </div>
        <div class="field">
          <label for="stock-price">Buy price (₹)</label>
          <input id="stock-price" name="buyPrice" type="number" min="0" step="0.01" required />
        </div>
        <button type="submit" class="btn btn-primary">Add stock</button>
      </form>

      ${renderStockList(state.stocks, state.ui.editingStockId)}
    </section>
  `;
}
