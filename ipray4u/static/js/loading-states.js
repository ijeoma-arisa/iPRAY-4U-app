const PRAYER_CARD_SKELETON_COUNT = 3;

// Keep this generated skeleton markup structurally aligned with prayer-requests.html.
export function createRelationshipButtonSkeletonsHTML(count = 4) {
  return Array.from({ length: count }, () => `
    <div
      class="skeleton skeleton-relationship-button"
      aria-hidden="true"
    ></div>`).join('');
}

function createPrayerCardSkeletonHTML() {
  return `
    <div class="prayer-card skeleton-prayer-card">
      <div class="skeleton-prayer-text">
        <div class="skeleton skeleton-prayer-text-placeholder"></div>
      </div>
      <div class="skeleton-prayer-actions">
        <div class="skeleton skeleton-prayer-action"></div>
        <div class="skeleton skeleton-prayer-action"></div>
        <div class="skeleton skeleton-prayer-action"></div>
      </div>
    </div>`;
}

export function createPersonCardSkeletonsHTML(count = 3) {
  const prayerCardsHTML = Array.from(
    { length: PRAYER_CARD_SKELETON_COUNT },
    createPrayerCardSkeletonHTML,
  ).join('');

  return Array.from({ length: count }, () => `
    <div class="person-card person-card-skeleton" aria-hidden="true">
      <div class="person-info-section skeleton-person-info-section">
        <div class="skeleton-person-header">
          <div class="skeleton-person-title">
            <div class="skeleton skeleton-person-name"></div>
            <div class="skeleton skeleton-person-relationship"></div>
          </div>
          <div class="skeleton-person-actions">
            <div class="skeleton skeleton-person-action"></div>
            <div class="skeleton skeleton-person-action"></div>
          </div>
        </div>
      </div>
      <div class="prayer-cards-section skeleton-prayer-cards-section">
        ${prayerCardsHTML}
      </div>
      <div class="skeleton skeleton-add-prayer"></div>
    </div>`).join('');
}
