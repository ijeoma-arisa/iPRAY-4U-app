import { describe, expect, it } from 'vitest';

import { createPersonCardSkeletonsHTML } from '../../ipray4u/static/js/loading-states.js';

describe('prayer card loading skeletons', () => {
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
