import { beforeEach, describe, expect, it } from 'vitest';

import {
  createPersonCard,
  createPrayerCard,
  formatPrayerCreatedAt,
  updatePrayerCard,
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
