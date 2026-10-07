import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  createPersonCard,
  createPrayerCard,
  insertPersonCard,
  insertPrayerCard,
  renderPeopleEmptyStateWhenEmpty,
  renderPersonCards,
  updatePrayerCard,
  updatePrayerStats,
  updateRelationshipStats,
} from '../../ipray4u/static/js/person-cards.js';

function person(id, relationship = 'Family') {
  return { id, name: `Person ${id}`, relationship };
}

function prayer(id, personId, hasPrayed = false) {
  return {
    id,
    person_id: personId,
    prayer: `Prayer ${id}`,
    has_prayed: hasPrayed,
  };
}

function summaryText() {
  return [...document.querySelector('.relationship-stats-js').children]
    .map(metric => metric.textContent);
}

function jsonResponse(data) {
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ data }),
  });
}

describe('relationship prayer statistics', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div class="relationship-stats-js"></div>
      <div class="person-cards-js"></div>
    `;
    window.matchMedia = () => ({ matches: true });
    window.scrollTo = () => {};
    Element.prototype.scrollTo = () => {};
    Element.prototype.scrollIntoView = () => {};
    vi.restoreAllMocks();
  });

  it('totals multiple people and prayers in the rendered relationship', () => {
    document.querySelector('.person-cards-js').append(
      createPersonCard(person(1), [prayer(11, 1), prayer(12, 1, true)]),
      createPersonCard(person(2), [prayer(21, 2), prayer(22, 2)]),
    );

    expect(updateRelationshipStats()).toEqual({
      people: 2,
      prayers: 4,
      notPrayed: 3,
    });
    expect(summaryText()).toEqual(['2 people', '4 prayers', '3 not prayed']);
  });

  it('shows consistent zero totals', () => {
    updateRelationshipStats();

    expect(summaryText()).toEqual(['0 people', '0 prayers', '0 not prayed']);
  });

  it('uses singular person and prayer grammar', () => {
    document.querySelector('.person-cards-js').append(
      createPersonCard(person(1), [prayer(11, 1)]),
    );

    updateRelationshipStats();

    expect(summaryText()).toEqual(['1 person', '1 prayer', '1 not prayed']);
  });

  it('updates after adding a person with an initial prayer', () => {
    updateRelationshipStats();

    insertPersonCard(createPersonCard(person(1), [prayer(11, 1)]));

    expect(summaryText()).toEqual(['1 person', '1 prayer', '1 not prayed']);
  });

  it('updates after adding and deleting a prayer', () => {
    const card = createPersonCard(person(1));
    document.querySelector('.person-cards-js').append(card);
    updateRelationshipStats();

    insertPrayerCard(card, createPrayerCard(prayer(11, 1), 1));
    expect(summaryText()).toEqual(['1 person', '1 prayer', '1 not prayed']);

    card.querySelector('[data-prayer-id="11"]').remove();
    updatePrayerStats(card);
    expect(summaryText()).toEqual(['1 person', '0 prayers', '0 not prayed']);
  });

  it('updates not prayed after toggling prayer status', () => {
    const initialPrayer = prayer(11, 1);
    const card = createPersonCard(person(1), [initialPrayer]);
    document.querySelector('.person-cards-js').append(card);
    updateRelationshipStats();

    updatePrayerCard(card.querySelector('.prayer-card-js'), {
      ...initialPrayer,
      has_prayed: true,
    });

    expect(summaryText()).toEqual(['1 person', '1 prayer', '0 not prayed']);
  });

  it('removes all of a deleted person’s prayers from the totals', () => {
    const card = createPersonCard(
      person(1),
      [prayer(11, 1), prayer(12, 1, true)],
    );
    document.querySelector('.person-cards-js').append(card);
    updateRelationshipStats();

    card.remove();
    renderPeopleEmptyStateWhenEmpty();

    expect(summaryText()).toEqual(['0 people', '0 prayers', '0 not prayed']);
    expect(document.querySelector('.person-cards-js').textContent)
      .toBe('No people found.');
  });

  it('stays accurate when a person leaves the active relationship', () => {
    const cards = document.querySelector('.person-cards-js');
    const movedCard = createPersonCard(person(1), [prayer(11, 1)]);
    cards.append(movedCard, createPersonCard(person(2), [prayer(21, 2, true)]));
    updateRelationshipStats();

    movedCard.remove();
    renderPeopleEmptyStateWhenEmpty(cards);

    expect(summaryText()).toEqual(['1 person', '1 prayer', '0 not prayed']);
  });

  it('renders All totals and updates immediately when switching filters', async () => {
    global.fetch = vi.fn((url) => {
      if (url === '/api/people') return jsonResponse([person(1), person(2, 'Friends')]);
      if (url === '/api/people?rel=family') return jsonResponse([person(1)]);
      if (url === '/api/people/1/prayers') return jsonResponse([prayer(11, 1)]);
      if (url === '/api/people/2/prayers') {
        return jsonResponse([prayer(21, 2, true), prayer(22, 2)]);
      }
      throw new Error(`Unexpected URL: ${url}`);
    });

    await renderPersonCards('/api/people', true, true);
    expect(summaryText()).toEqual(['2 people', '3 prayers', '2 not prayed']);

    await renderPersonCards('/api/people?rel=family', true, true);
    expect(summaryText()).toEqual(['1 person', '1 prayer', '1 not prayed']);
  });

  it('shows the summary skeleton until dashboard data finishes loading', async () => {
    let resolvePeople;
    global.fetch = vi.fn(() => new Promise((resolve) => {
      resolvePeople = () => resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve({ data: [] }),
      });
    }));

    const rendering = renderPersonCards('/api/people?rel=empty', true, true);
    const summary = document.querySelector('.relationship-stats-js');

    expect(summary.getAttribute('aria-busy')).toBe('true');
    expect(summary.querySelectorAll('.skeleton-relationship-stat')).toHaveLength(3);

    resolvePeople();
    await rendering;

    expect(summary.getAttribute('aria-busy')).toBe('false');
    expect(summaryText()).toEqual(['0 people', '0 prayers', '0 not prayed']);
  });
});
