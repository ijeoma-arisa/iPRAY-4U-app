import { GET_PEOPLE_URL } from './api/endpoints.js';

async function loadPrayers(person_id) {
  const response = await fetch(`${GET_PEOPLE_URL}/${person_id}/prayers`);
  const {status, data: prayers} = await response.json();

  let prayersHTML = '';

  prayers.forEach(prayer => {
    prayersHTML += `
      <div
        id="prayer-${prayer.id}" 
        class="prayer-card prayer-card-js"
          data-person-id="${person_id}" 
          data-prayer-id="${prayer.id}"
          data-prayer-text="${prayer.prayer}"
          data-has-prayed="${prayer['has_prayed']}"  
      >
        <div class="prayer-text">
          ${prayer.prayer}
          ${prayer['has_prayed'] ? '<span class="prayed-badge">Prayed!</span>' : ""}
        </div>
        <div class="update-prayer-buttons">
          <button 
            class="btn mark-prayed-button mark-prayed-button-js"
          >
            <i class="fa-solid fa-hands-praying" aria-hidden="true"></i>
          </button>

          <button class="btn edit-prayer-button edit-prayer-button-js">
            <i class="fa-solid fa-pencil" aria-hidden="true"></i>
          </button>

          <button 
            class="btn delete-prayer-button delete-prayer-button-js"
          >
            <i class="fa-solid fa-trash" aria-hidden="true"></i>
          </button>
        </div>
      </div>`;
  });
  return prayersHTML;
}

export async function renderPersonCards(url) {
  const response = await fetch(url);
  const {status, data: persons} = await response.json();
  
  let personCardsHTML = '';

  for (const person of persons){
    const prayersHTML = await loadPrayers(person.id);
    
    personCardsHTML += `
      <div
          id="person-${person.id}" 
          class="person-card person-card-js" 
          data-person-id="${person.id}"
          data-person-name="${person.name}"
          data-person-relationship="${person.relationship}"
      >
        <div class="person-info-section">
          <div class="person-header">
            <div class="person-title">
              <h3>${person.name}</h3>
              <p>${person.relationship}</p>
            </div>
          
            <div class="person-buttons">
              <button class="btn edit-person-button edit-person-button-js" aria-label="Edit ${person.name}">
                <i class="fa-solid fa-pencil" aria-hidden="true"></i> 
              </button>
              <button class="btn delete-person-button delete-person-button-js" aria-label="Delete ${person.name}">
                <i class="fa-solid fa-trash" aria-hidden="true"></i>
              </button>
            </div>
          </div>
        </div>

        <div class="prayer-cards-section">
          ${prayersHTML}
        </div>

        <button id=${person.id} 
          class="btn add-prayer-button add-prayer-button-js" 
          data-person-id=${person.id} 
          data-person-name="${person.name}" 
          data-person-relationship="${person.relationship}"
        >
          Add Prayer 
        </button>
      </div>`;
  }
  
  document.querySelector('.person-cards-js')
    .innerHTML = personCardsHTML || 'No people found.';
}

