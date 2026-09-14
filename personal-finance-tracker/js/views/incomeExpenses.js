import { escapeHTML, formatINR, formatDate } from '../format.js';
import { CATEGORIES } from '../state.js';

function renderIncomeList(income) {
  if (income.length === 0) {
    return '<p class="empty-state">No income recorded yet.</p>';
  }

  const rows = [...income]
    .sort((a, b) => b.date.localeCompare(a.date))
    .map(
      (item) => `
        <li class="list-row">
          <div>
            <strong>${escapeHTML(item.source)}</strong>
            <div class="text-muted">${formatDate(item.date)}</div>
          </div>
          <div class="form-row">
            <span>${formatINR(item.amount)}</span>
            <button type="button" class="btn btn-danger" data-action="delete-income" data-id="${escapeHTML(item.id)}">Delete</button>
          </div>
        </li>
      `
    )
    .join('');

  return `<ul class="list">${rows}</ul>`;
}

function categoryOptions(selectedCategory) {
  return CATEGORIES.map(
    (category) =>
      `<option value="${escapeHTML(category)}" ${category === selectedCategory ? 'selected' : ''}>${escapeHTML(category)}</option>`
  ).join('');
}

function renderExpenseList(expenses, filter) {
  if (expenses.length === 0) {
    return '<p class="empty-state">No expenses recorded yet.</p>';
  }

  const visible = filter === 'all' ? expenses : expenses.filter((item) => item.category === filter);

  if (visible.length === 0) {
    return '<p class="empty-state">No expenses in this category.</p>';
  }

  const rows = [...visible]
    .sort((a, b) => b.date.localeCompare(a.date))
    .map(
      (item) => `
        <li class="list-row">
          <div>
            <strong>${escapeHTML(item.category)}</strong>
            <div class="text-muted">${formatDate(item.date)}${item.note ? ' &middot; ' + escapeHTML(item.note) : ''}</div>
          </div>
          <div class="form-row">
            <span>${formatINR(item.amount)}</span>
            <button type="button" class="btn btn-danger" data-action="delete-expense" data-id="${escapeHTML(item.id)}">Delete</button>
          </div>
        </li>
      `
    )
    .join('');

  return `<ul class="list">${rows}</ul>`;
}

export function renderIncomeExpenses(panel, state) {
  const expenseFilter = state.ui.expenseCategoryFilter;

  panel.innerHTML = `
    <h2>Income &amp; Expenses</h2>

    <section class="card" aria-labelledby="income-heading">
      <h3 id="income-heading">Income</h3>
      <form data-action="add-income" class="form-row">
        <div class="field">
          <label for="income-source">Source</label>
          <input id="income-source" name="source" type="text" required maxlength="60" />
        </div>
        <div class="field">
          <label for="income-amount">Amount (₹)</label>
          <input id="income-amount" name="amount" type="number" min="0" step="1" required />
        </div>
        <div class="field">
          <label for="income-date">Date</label>
          <input id="income-date" name="date" type="date" required />
        </div>
        <button type="submit" class="btn btn-primary">Add income</button>
      </form>

      ${renderIncomeList(state.income)}
    </section>

    <section class="card section-gap" aria-labelledby="expenses-heading">
      <h3 id="expenses-heading">Expenses</h3>
      <form data-action="add-expense" class="form-row">
        <div class="field">
          <label for="expense-category">Category</label>
          <select id="expense-category" name="category" required>
            ${categoryOptions()}
          </select>
        </div>
        <div class="field">
          <label for="expense-amount">Amount (₹)</label>
          <input id="expense-amount" name="amount" type="number" min="0" step="1" required />
        </div>
        <div class="field">
          <label for="expense-date">Date</label>
          <input id="expense-date" name="date" type="date" required />
        </div>
        <div class="field">
          <label for="expense-note">Why? (optional)</label>
          <input id="expense-note" name="note" type="text" maxlength="140" />
        </div>
        <button type="submit" class="btn btn-primary">Add expense</button>
      </form>

      <div class="field filter-field section-gap">
        <label for="expense-filter">Filter by category</label>
        <select id="expense-filter" data-action="filter-expense-category">
          <option value="all" ${expenseFilter === 'all' ? 'selected' : ''}>All categories</option>
          ${categoryOptions(expenseFilter)}
        </select>
      </div>

      ${renderExpenseList(state.expenses, expenseFilter)}
    </section>
  `;
}
