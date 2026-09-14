import { uid } from './format.js';

const STORAGE_KEY = 'pft:state';

export const CATEGORIES = [
  'Food/Groceries',
  'Rent',
  'Transport',
  'Utilities',
  'Shopping',
  'Entertainment',
  'Health',
  'Other',
];

function createSeedState() {
  return {
    ui: {
      activeTab: 'dashboard',
      expenseCategoryFilter: 'all',
      editingStockId: null,
      watchlist: { sortByTopPerformers: false, sectorFilter: 'all' },
    },
    income: [
      { id: uid(), source: 'Salary', amount: 85000, date: '2026-08-01', note: '' },
      { id: uid(), source: 'Freelance', amount: 12000, date: '2026-08-05', note: '' },
    ],
    expenses: [
      { id: uid(), category: 'Rent', amount: 22000, date: '2026-08-01', note: '' },
      { id: uid(), category: 'Food/Groceries', amount: 6500, date: '2026-08-04', note: '' },
      { id: uid(), category: 'Transport', amount: 2200, date: '2026-08-06', note: '' },
      { id: uid(), category: 'Entertainment', amount: 1500, date: '2026-08-08', note: 'Movie night' },
    ],
    loans: [
      { id: uid(), name: 'Home Loan', emi: 18500, ratePct: 8.5, monthsLeft: 156 },
      { id: uid(), name: 'Car Loan', emi: 9200, ratePct: 9.2, monthsLeft: 24 },
    ],
    fds: [
      { id: uid(), name: 'SBI FD', principal: 100000, ratePct: 6.75, startDate: '2025-01-15', maturityDate: '2027-01-15' },
      { id: uid(), name: 'HDFC FD', principal: 50000, ratePct: 7.0, startDate: '2026-03-01', maturityDate: '2027-03-01' },
    ],
    sips: [
      { id: uid(), name: 'Nifty 50 Index Fund', monthly: 5000, startDate: '2024-06-01' },
      { id: uid(), name: 'Flexi Cap Fund', monthly: 3000, startDate: '2025-01-01' },
    ],
    stocks: [
      { id: uid(), name: 'TCS', sector: 'IT', quantity: 5, buyPrice: 3450 },
      { id: uid(), name: 'HDFC Bank', sector: 'Banking', quantity: 10, buyPrice: 1550 },
      { id: uid(), name: 'Reliance', sector: 'Energy', quantity: 8, buyPrice: 2450 },
    ],
    watchlist: [],
  };
}

function createSampleWatchlist() {
  return [
    { symbol: 'INFY', name: 'Infosys', sector: 'IT', samplePrice: 1850, sampleChangePct: 2.3 },
    { symbol: 'ITC', name: 'ITC Ltd', sector: 'FMCG', samplePrice: 460, sampleChangePct: -0.8 },
    { symbol: 'SBIN', name: 'State Bank of India', sector: 'Banking', samplePrice: 820, sampleChangePct: 1.1 },
    { symbol: 'TATAMOTORS', name: 'Tata Motors', sector: 'Auto', samplePrice: 1020, sampleChangePct: 3.4 },
    { symbol: 'SUNPHARMA', name: 'Sun Pharma', sector: 'Pharma', samplePrice: 1740, sampleChangePct: -1.2 },
    { symbol: 'ADANIPORTS', name: 'Adani Ports', sector: 'Infrastructure', samplePrice: 1380, sampleChangePct: 0.5 },
  ];
}

function isValidState(value) {
  if (!value || typeof value !== 'object') return false;
  if (!value.ui || typeof value.ui !== 'object') return false;
  const arrayKeys = ['income', 'expenses', 'loans', 'fds', 'sips', 'stocks'];
  return arrayKeys.every((key) => Array.isArray(value[key]));
}

function persist(value) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  } catch (err) {
    console.warn('Personal Finance Tracker: failed to save to localStorage.', err);
  }
}

function load() {
  let loaded;
  let usedFallback = false;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw === null) throw new Error('no stored state');
    const parsed = JSON.parse(raw);
    if (!isValidState(parsed)) throw new Error('stored state has an unexpected shape');
    loaded = parsed;
  } catch (err) {
    console.warn('Personal Finance Tracker: could not load saved data, starting from defaults.', err);
    loaded = createSeedState();
    usedFallback = true;
  }
  loaded.watchlist = createSampleWatchlist();
  if (usedFallback) persist(loaded);
  return loaded;
}

export const state = load();

function save() {
  persist(state);
}

const listeners = new Set();

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function notify() {
  listeners.forEach((fn) => fn());
}

function addTo(collection, fields) {
  const entry = { id: uid(), ...fields };
  state[collection].push(entry);
  save();
  notify();
  return entry;
}

function deleteFrom(collection, id) {
  state[collection] = state[collection].filter((item) => item.id !== id);
  save();
  notify();
}

export const addIncome = (fields) => addTo('income', fields);
export const deleteIncome = (id) => deleteFrom('income', id);

export const addExpense = (fields) => addTo('expenses', fields);
export const deleteExpense = (id) => deleteFrom('expenses', id);

export const addLoan = (fields) => addTo('loans', fields);
export const deleteLoan = (id) => deleteFrom('loans', id);

export const addFd = (fields) => addTo('fds', fields);
export const deleteFd = (id) => deleteFrom('fds', id);

export const addSip = (fields) => addTo('sips', fields);
export const deleteSip = (id) => deleteFrom('sips', id);

export const addStock = (fields) => addTo('stocks', fields);
export const deleteStock = (id) => deleteFrom('stocks', id);

export function updateStock(id, patch) {
  state.stocks = state.stocks.map((item) => (item.id === id ? { ...item, ...patch } : item));
  save();
  notify();
}

export function setEditingStockId(id) {
  state.ui.editingStockId = id || null;
  save();
  notify();
}

export function setActiveTab(tab) {
  state.ui.activeTab = tab;
  save();
  notify();
}

export function setExpenseCategoryFilter(category) {
  state.ui.expenseCategoryFilter = category;
  save();
  notify();
}

export function toggleWatchlistSort() {
  state.ui.watchlist.sortByTopPerformers = !state.ui.watchlist.sortByTopPerformers;
  save();
  notify();
}

export function setWatchlistSectorFilter(sector) {
  state.ui.watchlist.sectorFilter = sector;
  save();
  notify();
}
