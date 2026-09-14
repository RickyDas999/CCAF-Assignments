import {
  setActiveTab,
  addIncome,
  deleteIncome,
  addExpense,
  deleteExpense,
  setExpenseCategoryFilter,
  addLoan,
  deleteLoan,
  addFd,
  deleteFd,
  addSip,
  deleteSip,
  addStock,
  deleteStock,
  updateStock,
  setEditingStockId,
  toggleWatchlistSort,
  setWatchlistSectorFilter,
} from './state.js';
import { render } from './render.js';

const liveRegion = document.getElementById('live-region');
function announce(message) {
  if (liveRegion) liveRegion.textContent = message;
}

const CONFIRM_MESSAGES = {
  'delete-income': 'Delete this income entry?',
  'delete-expense': 'Delete this expense?',
  'delete-loan': 'Delete this loan?',
  'delete-fd': 'Delete this FD?',
  'delete-sip': 'Delete this SIP?',
  'delete-stock': 'Delete this stock?',
};

const CLICK_ACTIONS = {
  'delete-income': deleteIncome,
  'delete-expense': deleteExpense,
  'delete-loan': deleteLoan,
  'delete-fd': deleteFd,
  'delete-sip': deleteSip,
  'delete-stock': deleteStock,
  'start-edit-stock': setEditingStockId,
  'cancel-edit-stock': () => setEditingStockId(null),
  'toggle-watchlist-sort': toggleWatchlistSort,
};

const FORM_ACTIONS = {
  'add-income': (data) =>
    addIncome({
      source: data.get('source').trim(),
      amount: Number(data.get('amount')),
      date: data.get('date'),
    }),
  'add-expense': (data) =>
    addExpense({
      category: data.get('category'),
      amount: Number(data.get('amount')),
      date: data.get('date'),
      note: (data.get('note') || '').trim(),
    }),
  'add-loan': (data) =>
    addLoan({
      name: data.get('name').trim(),
      emi: Number(data.get('emi')),
      ratePct: Number(data.get('ratePct')),
      monthsLeft: Number(data.get('monthsLeft')),
    }),
  'add-fd': (data) =>
    addFd({
      name: data.get('name').trim(),
      principal: Number(data.get('principal')),
      ratePct: Number(data.get('ratePct')),
      startDate: data.get('startDate'),
      maturityDate: data.get('maturityDate'),
    }),
  'add-sip': (data) =>
    addSip({
      name: data.get('name').trim(),
      monthly: Number(data.get('monthly')),
      startDate: data.get('startDate'),
    }),
  'add-stock': (data) =>
    addStock({
      name: data.get('name').trim(),
      sector: data.get('sector').trim(),
      quantity: Number(data.get('quantity')),
      buyPrice: Number(data.get('buyPrice')),
    }),
  'save-stock': (data) => {
    updateStock(data.get('id'), {
      name: data.get('name').trim(),
      sector: data.get('sector').trim(),
      quantity: Number(data.get('quantity')),
      buyPrice: Number(data.get('buyPrice')),
    });
    setEditingStockId(null);
  },
};

document.addEventListener('click', (event) => {
  const tabBtn = event.target.closest('[data-tab]');
  if (tabBtn) {
    setActiveTab(tabBtn.dataset.tab);
    return;
  }

  const actionBtn = event.target.closest('[data-action]');
  if (actionBtn && CLICK_ACTIONS[actionBtn.dataset.action]) {
    const confirmMsg = CONFIRM_MESSAGES[actionBtn.dataset.action];
    if (confirmMsg && !window.confirm(confirmMsg)) return;
    CLICK_ACTIONS[actionBtn.dataset.action](actionBtn.dataset.id);
    if (confirmMsg) announce('Deleted.');
  }
});

document.addEventListener('submit', (event) => {
  const form = event.target.closest('[data-action]');
  if (form && FORM_ACTIONS[form.dataset.action]) {
    event.preventDefault();
    FORM_ACTIONS[form.dataset.action](new FormData(form));
    form.reset();
    announce('Saved.');
  }
});

document.addEventListener('change', (event) => {
  const expenseFilter = event.target.closest('[data-action="filter-expense-category"]');
  if (expenseFilter) {
    setExpenseCategoryFilter(expenseFilter.value);
    return;
  }

  const sectorFilter = event.target.closest('[data-action="filter-watchlist-sector"]');
  if (sectorFilter) {
    setWatchlistSectorFilter(sectorFilter.value);
  }
});

render();
