import { GET_PEOPLE_URL, LOGIN_URL } from './api/endpoints.js';
import {
  createPersonCardSkeletonsHTML,
  createPersonCardsLoadErrorHTML,
} from './loading-states.js';

const PEOPLE_EMPTY_TEXT = 'No people found.';
const PRAYERS_EMPTY_TEXT = 'No prayers found.';

class AuthenticationRedirectError extends Error {}

export async function loadPrayers(personId) {
  const response = await fetch(`${GET_PEOPLE_URL}/${personId}/prayers`);

  if (response.status === 401) {
    window.location.href = LOGIN_URL;
    throw new AuthenticationRedirectError();
  }

  if (!response.ok) {
    throw new Error(`Prayer request failed with status ${response.status}`);
  }

  const { data: prayers } = await response.json();

  return prayers;
}

function renderPersonCardsLoadError(personCards, url) {
  personCards.innerHTML = createPersonCardsLoadErrorHTML();
  personCards.setAttribute('aria-busy', 'false');
  personCards.querySelector('.retry-person-cards-js').addEventListener(
    'click', () => renderPersonCards(url, true), { once: true },
  );
}

function createElementFromHTML(html) {
  const template = document.createElement('template');
  template.innerHTML = html.trim();
  return template.content.firstElementChild;
}

export function updatePrayerCard(
  prayerCard,
  prayer,
  personId = prayerCard.dataset.personId,
) {
  prayerCard.id = `prayer-${prayer.id}`;
  prayerCard.dataset.personId = personId;
  prayerCard.dataset.prayerId = prayer.id;
  prayerCard.dataset.prayerText = prayer.prayer;
  prayerCard.dataset.hasPrayed = String(prayer.has_prayed);

  const prayerTextValue = prayerCard.querySelector('.prayer-text-value-js');
  prayerTextValue.textContent = prayer.prayer;

  const prayerTextContainer = prayerCard.querySelector('.prayer-text');
  const prayedBadge = prayerCard.querySelector('.prayed-badge');
  if (prayer.has_prayed && !prayedBadge) {
    prayerTextContainer.insertAdjacentHTML(
      'beforeend',
      '<span class="prayed-badge">Prayed!</span>',
    );
  } else if (!prayer.has_prayed) {
    prayedBadge?.remove();
  }

  const markPrayedButton = prayerCard.querySelector('.mark-prayed-button-js');
  markPrayedButton.setAttribute(
    'aria-label',
    prayer.has_prayed
      ? 'Mark prayer request as unprayed'
      : 'Mark prayer request as prayed',
  );

  const editPrayerButton = prayerCard.querySelector('.edit-prayer-button-js');
  editPrayerButton.setAttribute('aria-label', 'Edit prayer request');

  const deletePrayerButton = prayerCard.querySelector('.delete-prayer-button-js');
  deletePrayerButton.setAttribute('aria-label', 'Delete prayer request');

  return prayerCard;
}

export function createPrayerCard(prayer, personId) {
  const prayerCard = createElementFromHTML(`
    <div class="prayer-card prayer-card-js">
      <div class="prayer-text">
        <span class="prayer-text-value prayer-text-value-js"></span>
      </div>
      <div class="update-prayer-buttons">
        <button
          type="button"
          class="btn mark-prayed-button mark-prayed-button-js"
        >
          <i class="fa-solid fa-hands-praying" aria-hidden="true"></i>
        </button>
        <button
          type="button"
          class="btn edit-prayer-button edit-prayer-button-js"
        >
          <i class="fa-solid fa-pencil" aria-hidden="true"></i>
        </button>
        <button
          type="button"
          class="btn delete-prayer-button delete-prayer-button-js"
        >
          <i class="fa-solid fa-trash" aria-hidden="true"></i>
        </button>
      </div>
    </div>
  `);

  return updatePrayerCard(prayerCard, prayer, personId);
}

export function showPrayerEmptyState(personCard) {
  const prayerCardsSection = personCard.querySelector('.prayer-cards-section');
  if (!prayerCardsSection.querySelector('.prayer-card-js')) {
    prayerCardsSection.textContent = PRAYERS_EMPTY_TEXT;
  }
}

export function updatePersonCard(personCard, person) {
  personCard.id = `person-${person.id}`;
  personCard.dataset.personId = person.id;
  personCard.dataset.personName = person.name;
  personCard.dataset.personRelationship = person.relationship;

  const personName = personCard.querySelector('.person-name-value-js');
  personName.textContent = person.name;

  const personRelationship = personCard.querySelector('.person-relationship-value-js');
  personRelationship.textContent = person.relationship;

  const editPersonButton = personCard.querySelector('.edit-person-button-js');
  editPersonButton.setAttribute('aria-label', `Edit ${person.name}`);

  const deletePersonButton = personCard.querySelector('.delete-person-button-js');
  deletePersonButton.setAttribute('aria-label', `Delete ${person.name}`);

  const addPrayerButton = personCard.querySelector('.add-prayer-button-js');
  addPrayerButton.id = String(person.id);
  addPrayerButton.dataset.personId = person.id;
  addPrayerButton.dataset.personName = person.name;
  addPrayerButton.dataset.personRelationship = person.relationship;

  return personCard;
}

export function createPersonCard(person, prayers = []) {
  const personCard = createElementFromHTML(`
    <div class="person-card person-card-js">
      <div class="person-info-section">
        <div class="person-header">
          <div class="person-title">
            <h3 class="person-name-value-js"></h3>
            <p class="person-relationship-value-js"></p>
          </div>
          <div class="person-buttons">
            <button
              type="button"
              class="btn edit-person-button edit-person-button-js"
            >
              <i class="fa-solid fa-pencil" aria-hidden="true"></i>
            </button>
            <button
              type="button"
              class="btn delete-person-button delete-person-button-js"
            >
              <i class="fa-solid fa-trash" aria-hidden="true"></i>
            </button>
          </div>
        </div>
      </div>
      <div class="prayer-cards-section"></div>
      <button
        type="button"
        class="btn add-prayer-button add-prayer-button-js"
      >
        Add Prayer
      </button>
    </div>
  `);

  updatePersonCard(personCard, person);

  const prayerCardsSection = personCard.querySelector('.prayer-cards-section');
  prayers.forEach((prayer) => {
    const prayerCard = createPrayerCard(prayer, person.id);
    prayerCardsSection.append(prayerCard);
  });

  if (!prayers.length) showPrayerEmptyState(personCard);

  return personCard;
}

export function showPeopleEmptyState(
  personCards = document.querySelector('.person-cards-js'),
) {
  if (!personCards.querySelector('.person-card-js')) {
    personCards.textContent = PEOPLE_EMPTY_TEXT;
  }
}

export function insertPersonCard(personCard) {
  const personCards = document.querySelector('.person-cards-js');

  if (!personCards.querySelector('.person-card-js')) personCards.replaceChildren();
  personCards.append(personCard);
}

export function insertPrayerCard(personCard, prayerCard) {
  const prayerCardsSection = personCard.querySelector('.prayer-cards-section');

  if (!prayerCardsSection.querySelector('.prayer-card-js')) {
    prayerCardsSection.replaceChildren();
  }

  prayerCardsSection.append(prayerCard);
}

export async function renderPersonCards(
  url,
  showSkeletons = false,
  throwOnError = false,
) {
  const personCards = document.querySelector('.person-cards-js');

  if (showSkeletons) {
    personCards.setAttribute('aria-busy', 'true');
    personCards.innerHTML = createPersonCardSkeletonsHTML();
  }

  try {
    const response = await fetch(url);

    if (response.status === 401) {
      window.location.href = LOGIN_URL;
      return;
    }

    if (!response.ok) {
      throw new Error(`People request failed with status ${response.status}`);
    }
    
    const { data: persons } = await response.json();
    const renderedPersonCards = [];

    for (const person of persons) {
      const prayers = await loadPrayers(person.id);
      const personCard = createPersonCard(person, prayers);

      renderedPersonCards.push(personCard);
    }

    personCards.replaceChildren(...renderedPersonCards);
    showPeopleEmptyState(personCards);
    personCards.setAttribute('aria-busy', 'false');
  } catch (error) {
    if (error instanceof AuthenticationRedirectError) return;

    console.error('Unable to load prayer requests', { url }, error);
    renderPersonCardsLoadError(personCards, url);

    if (throwOnError) throw error;
  }
}
