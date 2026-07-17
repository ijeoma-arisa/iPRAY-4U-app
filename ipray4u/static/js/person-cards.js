import { GET_PEOPLE_URL, LOGIN_URL } from './api/endpoints.js';

async function loadPrayers(person_id) {
  const response = await fetch(`${GET_PEOPLE_URL}/${person_id}/prayers`);
  if (response.status === 401) {
    window.location.href = LOGIN_URL;
    return [];
  }

  const {data: prayers} = await response.json();
  return prayers;
}

function renderPrayerCardsHTML(prayers) {
  return prayers.map(prayer => `
      <div
        class="prayer-card prayer-card-js"
      >
        <div class="prayer-text">
          <span class="prayer-text-value prayer-text-value-js"></span>
          ${prayer['has_prayed'] ? '<span class="prayed-badge">Prayed!</span>' : ""}
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
      </div>`).join('');
}

export async function renderPersonCards(url, showSpinner = false) {
  const personCards = document.querySelector('.person-cards-js'); 
  
  if (showSpinner) {
    personCards.innerHTML = '<div class="loading-spinner"></div>';
  }

  const response = await fetch(url);
  if (response.status === 401) {
    window.location.href = LOGIN_URL;
    return;
  }
  
  const {status, data: persons} = await response.json();
  
  let personCardsHTML = '';

  const prayersByPerson = [];

  for (const person of persons){
    const prayers = await loadPrayers(person.id);
    prayersByPerson.push(prayers);
    const prayersHTML = renderPrayerCardsHTML(prayers);
    
    personCardsHTML += `
      <div
          class="person-card person-card-js" 
      >
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

        <div class="prayer-cards-section">
          ${prayersHTML}
        </div>

        <button 
          type="button" 
          class="btn add-prayer-button add-prayer-button-js" 
        >
          Add Prayer 
        </button>
      </div>`;
  }
  
  personCards.innerHTML = personCardsHTML || 'No people found.';

  const renderedPersonCards = personCards.querySelectorAll('.person-card-js');

  persons.forEach((person, personIndex) => {
    const personCard = renderedPersonCards[personIndex];
    personCard.id = `person-${person.id}`;
    personCard.dataset.personId = person.id;
    personCard.dataset.personName = person.name;
    personCard.dataset.personRelationship = person.relationship;
    personCard.querySelector('.person-name-value-js').textContent = person.name;
    personCard.querySelector('.person-relationship-value-js').textContent = person.relationship;
    personCard.querySelector('.edit-person-button-js').setAttribute('aria-label', `Edit ${person.name}`);
    personCard.querySelector('.delete-person-button-js').setAttribute('aria-label', `Delete ${person.name}`);

    const addPrayerButton = personCard.querySelector('.add-prayer-button-js');
    addPrayerButton.id = `${person.id}`;
    addPrayerButton.dataset.personId = person.id;
    addPrayerButton.dataset.personName = person.name;
    addPrayerButton.dataset.personRelationship = person.relationship;

    const renderedPrayerCards = personCard.querySelectorAll('.prayer-card-js');

    prayersByPerson[personIndex].forEach((prayer, prayerIndex) => {
      const prayerCard = renderedPrayerCards[prayerIndex];
      prayerCard.id = `prayer-${prayer.id}`;
      prayerCard.dataset.personId = person.id;
      prayerCard.dataset.prayerId = prayer.id;
      prayerCard.dataset.prayerText = prayer.prayer;
      prayerCard.dataset.hasPrayed = prayer.has_prayed;
      prayerCard.querySelector('.prayer-text-value-js').textContent = prayer.prayer;
    });
  });
}

