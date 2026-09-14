import { escapeHTML, formatINR } from '../format.js';

function renderRow(item) {
  const changeClass = item.sampleChangePct >= 0 ? 'text-positive' : 'text-negative';
  const changeSign = item.sampleChangePct >= 0 ? '+' : '';
  return `
    <li class="list-row">
      <div>
        <strong>${escapeHTML(item.symbol)}</strong> &middot; ${escapeHTML(item.name)}
        <div class="text-muted">${escapeHTML(item.sector)}</div>
      </div>
      <div class="form-row">
        <span>${formatINR(item.samplePrice)}</span>
        <span class="${changeClass}">${changeSign}${escapeHTML(item.sampleChangePct)}%</span>
      </div>
    </li>
  `;
}

export function renderWatchlist(panel, state) {
  const { sortByTopPerformers, sectorFilter } = state.ui.watchlist;

  const sectors = ['all', ...new Set(state.watchlist.map((item) => item.sector))];
  const sectorOptions = sectors
    .map((sector) => `<option value="${escapeHTML(sector)}" ${sector === sectorFilter ? 'selected' : ''}>${sector === 'all' ? 'All sectors' : escapeHTML(sector)}</option>`)
    .join('');

  let items = sectorFilter === 'all' ? state.watchlist : state.watchlist.filter((item) => item.sector === sectorFilter);
  items = [...items].sort((a, b) => (sortByTopPerformers ? b.sampleChangePct - a.sampleChangePct : 0));

  const list = items.length === 0
    ? '<p class="empty-state">No stocks match this filter.</p>'
    : `<ul class="list">${items.map(renderRow).join('')}</ul>`;

  panel.innerHTML = `
    <h2>Stocks to Watch</h2>
    <p class="text-muted">Sample data for learning purposes only &mdash; not live prices, not investment advice.</p>

    <div class="card">
      <div class="form-row">
        <div class="field filter-field">
          <label for="watchlist-sector-filter">Sector</label>
          <select id="watchlist-sector-filter" data-action="filter-watchlist-sector">
            ${sectorOptions}
          </select>
        </div>
        <button type="button" class="btn" data-action="toggle-watchlist-sort" aria-pressed="${sortByTopPerformers}">
          ${sortByTopPerformers ? 'Sorted: top performers' : 'Sort by top performers'}
        </button>
      </div>

      ${list}
    </div>
  `;
}
