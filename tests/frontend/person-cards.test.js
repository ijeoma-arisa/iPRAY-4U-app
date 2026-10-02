import { beforeEach, describe, expect, it } from 'vitest';

import {
  createPersonCard,
  createPrayerCard,
  formatPrayerCreatedAt,
  insertPrayerCard,
  updatePrayerCard,
  updatePrayerStats,
} from '../../ipray4u/static/js/person-cards.js';

const CREATED_AT = '2026-09-23T19:42:18.123456+00:00';

function prayer(overrides = {}) {
  return {
    id: 7,
    person_id: 3,
    prayer: 'Peace and wisdom',
    has_prayed: false,
    created_at: CREATED_AT,
    ...overrides,
  };
}

function dateDisplay(card) {
  return card.querySelector('.prayer-created-at-js');
}

function timeElement(card) {
  return dateDisplay(card).querySelector('time');
}

function statusBadge(card) {
  return card.querySelector('.prayer-status-badge');
}

function stats(card) {
  const summary = card.querySelector('.prayer-stats-js');
  const state = summary.querySelector('.prayer-stats-state-js');

  return {
    total: summary.querySelector('.prayer-stats-total-js').textContent,
    state: state.textContent,
    stateHidden: state.hidden,
    ariaLabel: summary.getAttribute('aria-label'),
  };
}

describe('person prayer statistics', () => {
  beforeEach(() => {
    document.body.innerHTML = '<div class="person-cards-js"></div>';
    window.matchMedia = () => ({ matches: true });
    Element.prototype.scrollTo = () => {};
    Element.prototype.scrollIntoView = () => {};
  });

  it('displays only the pluralized total for a person without prayers', () => {
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
    );

    expect(stats(card)).toEqual({
      total: '0 prayers',
      state: '',
      stateHidden: true,
      ariaLabel: '0 prayers',
    });
    expect(card.querySelector('.person-title + .person-header'))
      .not.toBeNull();
    expect(card.querySelector('.person-metadata > .prayer-stats-js'))
      .not.toBeNull();
  });

  it('uses singular grammar and shows an outstanding prayer', () => {
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [prayer()],
    );

    expect(stats(card)).toEqual({
      total: '1 prayer',
      state: '1 not prayed',
      stateHidden: false,
      ariaLabel: '1 prayer, 1 not prayed',
    });
  });

  it('summarizes the total and outstanding prayers', () => {
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [
        prayer({ id: 7, has_prayed: true }),
        prayer({ id: 8, has_prayed: false }),
        prayer({ id: 9, has_prayed: false }),
      ],
    );

    expect(stats(card)).toEqual({
      total: '3 prayers',
      state: '2 not prayed',
      stateHidden: false,
      ariaLabel: '3 prayers, 2 not prayed',
    });
    expect(card.querySelector('.prayer-stats-state-js').classList)
      .toContain('prayer-stats-outstanding');
  });

  it('shows the completion state when all prayers have been prayed', () => {
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [prayer({ id: 7, has_prayed: true })],
    );

    expect(stats(card)).toEqual({
      total: '1 prayer',
      state: '✓ All prayed',
      stateHidden: false,
      ariaLabel: '1 prayer, all prayed',
    });
    expect(card.querySelector('.prayer-stats-state-js').classList)
      .toContain('prayer-stats-complete');
  });

  it('updates the summary when a prayer is added locally', () => {
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
    );
    document.querySelector('.person-cards-js').append(card);

    insertPrayerCard(card, createPrayerCard(prayer(), 3));

    expect(stats(card)).toMatchObject({
      total: '1 prayer',
      state: '1 not prayed',
      stateHidden: false,
    });
  });

  it('transitions between outstanding and all-prayed states', () => {
    const initialPrayer = prayer({ has_prayed: false });
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [initialPrayer],
    );
    document.querySelector('.person-cards-js').append(card);
    const prayerCard = card.querySelector('.prayer-card-js');

    updatePrayerCard(prayerCard, { ...initialPrayer, has_prayed: true });
    expect(stats(card)).toMatchObject({
      total: '1 prayer',
      state: '✓ All prayed',
      ariaLabel: '1 prayer, all prayed',
    });

    updatePrayerCard(prayerCard, { ...initialPrayer, has_prayed: false });
    expect(stats(card)).toMatchObject({
      total: '1 prayer',
      state: '1 not prayed',
      ariaLabel: '1 prayer, 1 not prayed',
    });
  });

  it('returns to zero prayers when the final prayer is removed locally', () => {
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [prayer({ id: 7, has_prayed: true })],
    );
    card.querySelector('[data-prayer-id="7"]').remove();

    updatePrayerStats(card);

    expect(stats(card)).toEqual({
      total: '0 prayers',
      state: '',
      stateHidden: true,
      ariaLabel: '0 prayers',
    });
  });

  it('does not change counts when only prayer text is edited', () => {
    const initialPrayer = prayer({ has_prayed: true });
    const card = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [initialPrayer],
    );
    document.querySelector('.person-cards-js').append(card);

    updatePrayerCard(card.querySelector('.prayer-card-js'), {
      ...initialPrayer,
      prayer: 'Updated text',
    });

    expect(stats(card)).toEqual({
      total: '1 prayer',
      state: '✓ All prayed',
      stateHidden: false,
      ariaLabel: '1 prayer, all prayed',
    });
  });
});

describe('prayer status badges', () => {
  beforeEach(() => {
    document.body.replaceChildren();
  });

  it('displays the prayed badge for a prayed prayer', () => {
    const card = createPrayerCard(prayer({ has_prayed: true }), 3);

    expect(statusBadge(card).textContent).toBe('Prayed');
    expect(statusBadge(card).classList.contains('prayed-badge')).toBe(true);
    expect(statusBadge(card).classList.contains('not-prayed-badge')).toBe(false);
  });

  it('displays the not-prayed badge for a prayer that is not prayed', () => {
    const card = createPrayerCard(prayer(), 3);

    expect(statusBadge(card).textContent).toBe('Not Prayed');
    expect(statusBadge(card).classList.contains('not-prayed-badge')).toBe(true);
    expect(statusBadge(card).classList.contains('prayed-badge')).toBe(false);
  });

  it('defaults a newly created prayer without has_prayed to not prayed', () => {
    const newPrayer = prayer();
    delete newPrayer.has_prayed;

    const card = createPrayerCard(newPrayer, 3);

    expect(card.dataset.hasPrayed).toBe('false');
    expect(statusBadge(card).textContent).toBe('Not Prayed');
    expect(statusBadge(card).classList.contains('not-prayed-badge')).toBe(true);
  });

  it('updates the badge immediately when toggling between states', () => {
    const initialPrayer = prayer();
    const card = createPrayerCard(initialPrayer, 3);
    const originalBadge = statusBadge(card);

    updatePrayerCard(card, { ...initialPrayer, has_prayed: true });

    expect(card.dataset.hasPrayed).toBe('true');
    expect(statusBadge(card)).toBe(originalBadge);
    expect(statusBadge(card).textContent).toBe('Prayed');
    expect(statusBadge(card).classList.contains('prayed-badge')).toBe(true);
    expect(statusBadge(card).classList.contains('not-prayed-badge')).toBe(false);

    updatePrayerCard(card, { ...initialPrayer, has_prayed: false });

    expect(card.dataset.hasPrayed).toBe('false');
    expect(statusBadge(card)).toBe(originalBadge);
    expect(statusBadge(card).textContent).toBe('Not Prayed');
    expect(statusBadge(card).classList.contains('not-prayed-badge')).toBe(true);
    expect(statusBadge(card).classList.contains('prayed-badge')).toBe(false);
    expect(card.querySelectorAll('.prayer-status-badge')).toHaveLength(1);
  });

  it('renders the correct badges when cards are reconstructed from cached data', () => {
    const personCard = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [prayer({ id: 7, has_prayed: true }), prayer({ id: 8 })],
    );
    const badges = [...personCard.querySelectorAll('.prayer-status-badge')];

    expect(badges.map((badge) => badge.textContent)).toEqual([
      'Prayed',
      'Not Prayed',
    ]);
  });
});

describe('prayer creation dates', () => {
  beforeEach(() => {
    document.body.replaceChildren();
  });

  it('formats a timestamp with the browser locale and local timezone', () => {
    const expected = new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(new Date(CREATED_AT));

    expect(formatPrayerCreatedAt(CREATED_AT)).toBe(expected);
  });

  it('uses the local calendar date near a UTC date boundary', () => {
    const timestamp = '2026-09-24T00:30:00.000000+00:00';
    const localDate = new Date(timestamp);

    expect(Intl.DateTimeFormat().resolvedOptions().timeZone)
      .toBe('America/Los_Angeles');
    expect(localDate.getFullYear()).toBe(2026);
    expect(localDate.getMonth()).toBe(8);
    expect(localDate.getDate()).toBe(23);
    expect(formatPrayerCreatedAt(timestamp)).toBe(
      new Intl.DateTimeFormat(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      }).format(localDate),
    );
  });

  it.each([
    ['null', { created_at: null }],
    ['missing', { created_at: undefined }],
    ['invalid', { created_at: 'not-a-timestamp' }],
  ])('does not display a date for a %s timestamp', (_label, override) => {
    const value = prayer();
    if (override.created_at === undefined) delete value.created_at;
    else Object.assign(value, override);

    const card = createPrayerCard(value, value.person_id);

    expect(dateDisplay(card).hidden).toBe(true);
    expect(dateDisplay(card).textContent.trim()).toBe('Added');
    expect(timeElement(card).textContent).toBe('');
    expect(timeElement(card).hasAttribute('datetime')).toBe(false);
  });

  it.each([
    ['text edits', { prayer: 'Updated prayer' }],
    ['prayed-status changes', { has_prayed: true }],
    ['combined updates', { prayer: 'Updated prayer', has_prayed: true }],
  ])('preserves the creation date through %s', (_label, changes) => {
    const initialPrayer = prayer();
    const card = createPrayerCard(initialPrayer, initialPrayer.person_id);
    const originalText = timeElement(card).textContent;
    const update = { ...initialPrayer, ...changes };

    updatePrayerCard(card, update);

    expect(dateDisplay(card).hidden).toBe(false);
    expect(timeElement(card).textContent).toBe(originalText);
    expect(timeElement(card).getAttribute('datetime')).toBe(CREATED_AT);
  });

  it('preserves an existing date when an update omits created_at', () => {
    const initialPrayer = prayer();
    const card = createPrayerCard(initialPrayer, initialPrayer.person_id);

    updatePrayerCard(card, {
      id: initialPrayer.id,
      prayer: 'Updated prayer',
      has_prayed: true,
    });

    expect(dateDisplay(card).hidden).toBe(false);
    expect(timeElement(card).getAttribute('datetime')).toBe(CREATED_AT);
  });

  it('displays the timestamp on a newly inserted prayer card', () => {
    const newPrayerCard = createPrayerCard(prayer(), 3);

    expect(dateDisplay(newPrayerCard).hidden).toBe(false);
    expect(timeElement(newPrayerCard).getAttribute('datetime')).toBe(CREATED_AT);
  });

  it('displays timestamps when cards are reconstructed from cached data', () => {
    const cachedPrayer = prayer();
    const personCard = createPersonCard(
      { id: 3, name: 'Avery', relationship: 'Friends' },
      [cachedPrayer],
    );
    const reconstructedPrayerCard = personCard.querySelector('.prayer-card-js');

    expect(dateDisplay(reconstructedPrayerCard).hidden).toBe(false);
    expect(timeElement(reconstructedPrayerCard).getAttribute('datetime'))
      .toBe(CREATED_AT);
  });
});
