export function loanOutstandingBalance(loan) {
  const emi = Number(loan.emi) || 0;
  const monthsLeft = Number(loan.monthsLeft) || 0;
  const monthlyRate = (Number(loan.ratePct) || 0) / 100 / 12;

  if (monthsLeft <= 0) return 0;
  if (monthlyRate === 0) return emi * monthsLeft;

  return (emi * (1 - Math.pow(1 + monthlyRate, -monthsLeft))) / monthlyRate;
}

function parseLocalDate(dateStr) {
  const [year, month, day] = String(dateStr).split('-').map(Number);
  return new Date(year, (month || 1) - 1, day || 1);
}

const MS_PER_DAY = 24 * 60 * 60 * 1000;

export function fdCurrentValue(fd) {
  const principal = Number(fd.principal) || 0;
  const ratePct = Number(fd.ratePct) || 0;
  const start = parseLocalDate(fd.startDate);
  const maturity = parseLocalDate(fd.maturityDate);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (Number.isNaN(start.getTime())) return principal;

  const cappedEnd = Math.min(today.getTime(), maturity.getTime());
  const elapsedDays = Math.max(0, (cappedEnd - start.getTime()) / MS_PER_DAY);
  const yearsElapsed = elapsedDays / 365;

  return principal + principal * (ratePct / 100) * yearsElapsed;
}

export function sipContributed(sip) {
  const monthly = Number(sip.monthly) || 0;
  const start = parseLocalDate(sip.startDate);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (Number.isNaN(start.getTime()) || start.getTime() > today.getTime()) return 0;

  let months = (today.getFullYear() - start.getFullYear()) * 12 + (today.getMonth() - start.getMonth());
  if (today.getDate() < start.getDate()) {
    months -= 1;
  }
  months = Math.max(0, months);

  return monthly * months;
}

export function stockInvested(stock) {
  return (Number(stock.quantity) || 0) * (Number(stock.buyPrice) || 0);
}

export function stocksInvestedTotal(stocks) {
  return stocks.reduce((total, stock) => total + stockInvested(stock), 0);
}

function isInMonth(dateStr, referenceDate) {
  const date = parseLocalDate(dateStr);
  return date.getFullYear() === referenceDate.getFullYear() && date.getMonth() === referenceDate.getMonth();
}

export function monthlyIncomeTotal(income, referenceDate = new Date()) {
  return income
    .filter((item) => isInMonth(item.date, referenceDate))
    .reduce((total, item) => total + (Number(item.amount) || 0), 0);
}

export function monthlyExpensesTotal(expenses, referenceDate = new Date()) {
  return expenses
    .filter((item) => isInMonth(item.date, referenceDate))
    .reduce((total, item) => total + (Number(item.amount) || 0), 0);
}

export function emiTotal(loans) {
  return loans.reduce((total, loan) => total + (Number(loan.emi) || 0), 0);
}

export function sipMonthlyTotal(sips) {
  return sips.reduce((total, sip) => total + (Number(sip.monthly) || 0), 0);
}

export function outstandingDebtTotal(loans) {
  return loans.reduce((total, loan) => total + loanOutstandingBalance(loan), 0);
}

export function fdValueTotal(fds) {
  return fds.reduce((total, fd) => total + fdCurrentValue(fd), 0);
}

export function sipContributedTotal(sips) {
  return sips.reduce((total, sip) => total + sipContributed(sip), 0);
}

export function netCashFlow(state) {
  const income = monthlyIncomeTotal(state.income);
  const expenses = monthlyExpensesTotal(state.expenses);
  const emi = emiTotal(state.loans);
  const sip = sipMonthlyTotal(state.sips);
  return income - expenses - emi - sip;
}
