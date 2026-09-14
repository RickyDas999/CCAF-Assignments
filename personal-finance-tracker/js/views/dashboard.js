import { escapeHTML, formatINR } from '../format.js';
import { CATEGORIES } from '../state.js';
import {
  monthlyIncomeTotal,
  monthlyExpensesTotal,
  emiTotal,
  sipMonthlyTotal,
  netCashFlow,
  outstandingDebtTotal,
  fdValueTotal,
  sipContributedTotal,
  stocksInvestedTotal,
} from '../calculations.js';

function renderFlowBar(income, expenses, emi, sip) {
  const outflow = expenses + emi + sip;
  const denom = Math.max(income, outflow, 1);
  const pct = (value) => Math.min(100, (value / denom) * 100);
  const savings = Math.max(0, income - outflow);

  return `
    <div class="flow-bar" role="img" aria-label="Of ${formatINR(income)} income this month: ${formatINR(expenses)} expenses, ${formatINR(emi)} EMI, ${formatINR(sip)} SIP, ${formatINR(savings)} left over">
      <div class="flow-segment flow-segment--expenses" style="width:${pct(expenses)}%"></div>
      <div class="flow-segment flow-segment--emi" style="width:${pct(emi)}%"></div>
      <div class="flow-segment flow-segment--sip" style="width:${pct(sip)}%"></div>
      <div class="flow-segment flow-segment--savings" style="width:${pct(savings)}%"></div>
    </div>
    <div class="flow-legend">
      <span><i class="dot dot--expenses"></i>Expenses ${formatINR(expenses)}</span>
      <span><i class="dot dot--emi"></i>EMI ${formatINR(emi)}</span>
      <span><i class="dot dot--sip"></i>SIP ${formatINR(sip)}</span>
      <span><i class="dot dot--savings"></i>Left over ${formatINR(savings)}</span>
    </div>
  `;
}

function renderCard(label, value) {
  return `
    <div class="card">
      <div class="text-muted">${label}</div>
      <div class="stat-value">${formatINR(value)}</div>
    </div>
  `;
}

function renderQuickAdd() {
  const categoryOptions = CATEGORIES.map((category) => `<option value="${escapeHTML(category)}">${escapeHTML(category)}</option>`).join('');

  return `
    <div class="card section-gap">
      <h3>Quick add</h3>
      <div class="quick-add-grid">
        <form data-action="add-income" class="form-row">
          <input type="hidden" name="source" value="Salary" />
          <div class="field">
            <label for="quick-salary-amount">Salary amount (₹)</label>
            <input id="quick-salary-amount" name="amount" type="number" min="0" step="1" required />
          </div>
          <div class="field">
            <label for="quick-salary-date">Date</label>
            <input id="quick-salary-date" name="date" type="date" required />
          </div>
          <button type="submit" class="btn btn-primary">Add salary</button>
        </form>

        <form data-action="add-expense" class="form-row">
          <div class="field">
            <label for="quick-expense-category">Category</label>
            <select id="quick-expense-category" name="category" required>
              ${categoryOptions}
            </select>
          </div>
          <div class="field">
            <label for="quick-expense-amount">Amount (₹)</label>
            <input id="quick-expense-amount" name="amount" type="number" min="0" step="1" required />
          </div>
          <div class="field">
            <label for="quick-expense-date">Date</label>
            <input id="quick-expense-date" name="date" type="date" required />
          </div>
          <button type="submit" class="btn btn-primary">Add expense</button>
        </form>
      </div>
    </div>
  `;
}

export function renderDashboard(panel, state) {
  const income = monthlyIncomeTotal(state.income);
  const expenses = monthlyExpensesTotal(state.expenses);
  const emi = emiTotal(state.loans);
  const sip = sipMonthlyTotal(state.sips);
  const netFlow = netCashFlow(state);
  const outstandingDebt = outstandingDebtTotal(state.loans);
  const fdValue = fdValueTotal(state.fds);
  const sipContributed = sipContributedTotal(state.sips);
  const stocksInvested = stocksInvestedTotal(state.stocks);

  panel.innerHTML = `
    <h2>Dashboard</h2>

    <div class="card">
      <div class="text-muted">Net cash flow this month</div>
      <div class="headline ${netFlow >= 0 ? 'text-positive' : 'text-negative'}">${formatINR(netFlow)}</div>
      ${renderFlowBar(income, expenses, emi, sip)}
    </div>

    <div class="card-grid section-gap">
      ${renderCard('Income', income)}
      ${renderCard('Expenses', expenses)}
      ${renderCard('EMI', emi)}
      ${renderCard('SIP', sip)}
      ${renderCard('Outstanding debt', outstandingDebt)}
      ${renderCard('FD value', fdValue)}
      ${renderCard('SIP contributed', sipContributed)}
      ${renderCard('Stocks invested', stocksInvested)}
    </div>

    ${renderQuickAdd()}
  `;
}
