const PRAYER_CARD_SKELETON_COUNT = 2;

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
      <div class="prayer-text skeleton-prayer-text">
        <div class="skeleton skeleton-prayer-text-placeholder"></div>
        <p class="prayer-created-at skeleton-prayer-date">
          <span class="skeleton skeleton-prayer-date-placeholder"></span>
        </p>
      </div>
      <div class="prayer-status skeleton-prayer-status">
        <div class="prayer-status-badge skeleton skeleton-prayer-status-badge">Not Prayed</div>
      </div>
      <div class="update-prayer-buttons skeleton-prayer-actions">
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
            <div class="skeleton skeleton-person-action"></div>
          </div>
        </div>
        <div class="prayer-stats skeleton-prayer-stats">
          <span class="skeleton skeleton-prayer-stat skeleton-prayer-stat-total"></span>
          <span class="skeleton skeleton-prayer-stat skeleton-prayer-stat-prayed"></span>
          <span class="skeleton skeleton-prayer-stat skeleton-prayer-stat-not-prayed"></span>
        </div>
      </div>
      <div class="prayer-cards-section skeleton-prayer-cards-section">
        ${prayerCardsHTML}
      </div>
    </div>`).join('');
}

export function createRelationshipLoadErrorHTML() {
  return `
    <div class="load-error relationship-load-error" role="alert">
      <p class="load-error-message">Unable to load relationships.</p>
      <button
        type="button"
        class="btn error-retry-button retry-relationships-js"
      >
        <i class="fa-solid fa-rotate-right" aria-hidden="true"></i>
        Try Again
      </button>
    </div>`;
}

export function createPersonCardsLoadErrorHTML() {
  return `
    <div class="load-error person-cards-load-error" role="alert">
      <div>
        <p class="load-error-message">Unable to load prayer requests.</p>
        <p class="load-error-detail">Please try again.</p>
      </div>
      <button
        type="button"
        class="btn error-retry-button retry-person-cards-js"
      >
        <i class="fa-solid fa-rotate-right" aria-hidden="true"></i>
        Try Again
      </button>
    </div>`;
}
