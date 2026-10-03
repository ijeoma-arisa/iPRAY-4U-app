import { describe, expect, it } from 'vitest';

import { createPersonCardSkeletonsHTML } from '../../ipray4u/static/js/loading-states.js';

describe('person card loading skeletons', () => {
  it('includes a compact stats summary placeholder beneath every person header', () => {
    const container = document.createElement('div');
    container.innerHTML = createPersonCardSkeletonsHTML(2);

    const personCards = [...container.querySelectorAll('.person-card-skeleton')];

    expect(personCards).toHaveLength(2);
    personCards.forEach((card) => {
      const header = card.querySelector('.skeleton-person-header');
      const stats = card.querySelector('.skeleton-prayer-stats');

      expect(header.previousElementSibling.classList)
        .toContain('skeleton-person-title');
      expect(stats.parentElement.classList)
        .toContain('skeleton-person-metadata');
      expect(stats.previousElementSibling.classList)
        .toContain('skeleton-person-relationship');
      expect(stats.classList).toContain('prayer-stats');
      expect(stats.querySelectorAll('.skeleton-prayer-stats-total')).toHaveLength(1);
      expect(stats.querySelectorAll('.skeleton-prayer-stats-state')).toHaveLength(1);
      expect(stats.querySelectorAll('.skeleton')).toHaveLength(2);
    });
  });

  it('includes one status badge placeholder in every prayer card skeleton', () => {
    const container = document.createElement('div');
    container.innerHTML = createPersonCardSkeletonsHTML(2);

    const prayerCards = [...container.querySelectorAll('.skeleton-prayer-card')];

    expect(prayerCards).toHaveLength(4);
    prayerCards.forEach((card) => {
      expect(card.querySelectorAll('.skeleton-prayer-status-badge')).toHaveLength(1);
      expect(card.querySelector('.skeleton-prayer-status-badge').classList)
        .toContain('prayer-status-badge');
      expect(card.querySelector('.skeleton-prayer-status').classList)
        .toContain('prayer-status');
      expect(card.querySelectorAll('.skeleton-prayer-date-placeholder')).toHaveLength(1);
      expect(card.querySelector('.skeleton-prayer-date').classList)
        .toContain('prayer-created-at');
      expect(card.querySelector('.skeleton-prayer-actions').classList)
        .toContain('update-prayer-buttons');
    });
  });
});
