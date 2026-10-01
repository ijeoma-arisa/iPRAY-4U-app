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
    });
  });
});
