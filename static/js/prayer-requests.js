import { initPrayerRequestModal } from './index.js';

function displayTime(){
  const today = new Date();
  const options = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
  
  document.querySelector('.current-date-js').innerHTML = today.toLocaleDateString('en-US', options);
}

async function renderRelationshipButtons() {
  const response = await fetch("/relationships");
  const relationships = await response.json();

  let relationshipsHTML = '<button class="btn relationship-button relationship-button-fav">Favorites</button>';

  relationships.forEach(relationship => {
    relationshipsHTML += `<button class="btn relationship-button relationship-button-${relationship.id}">${relationship.relationship}</button>`;
  });

  document.querySelector('.relationships-row-js')
    .innerHTML = relationshipsHTML;
}


async function loadPrayers(person_id) {
  const response = await fetch(`people/${person_id}/prayers`);
  const prayers = await response.json();

  let prayersHTML = '';

  prayers.forEach(prayer => {
    prayersHTML += `
          <div class="prayer-card" data-id="${prayer.id}">
            <div class="prayer-text">
              ${prayer.text}
            </div>
            <div class="update-prayer-buttons">
              <button class="btn delete-prayer-button"><i class="fa fa-trash-o"></i></button>
            </div>
          </div>`;
  });
  return prayersHTML;
}

async function renderPersonCards() {
  const response = await fetch("/people");
  const persons = await response.json();
  
  let personHTML = '';

  for (const person of persons){
    const prayersHTML = await loadPrayers(person.id);
    
    personHTML += `
        <div class="person-card" data-person-id=${person.id}>
          <div class="person-info-section">
            <h3>${person.name}</h3>
            <p>${person.relationship}</p>
            <button class="btn delete-person-button">Delete</button>
          </div>
          <div class="prayer-cards-section">
            ${prayersHTML}
          </div>
          <button id=${person.id} 
          class="btn add-prayer-button add-prayer-button-js" 
          data-person-id=${person.id} 
          data-person-name="${person.name}" 
          data-person-relationship="${person.relationship}">
        Add Prayer 
        </button>
        </div>`;
  }

  document.querySelector('.person-cards')
    .innerHTML = personHTML;
}

function initPrayerEventListeners() {
  const personCards = document.querySelector('.person-cards');

  personCards.addEventListener('click', async (event) => {
    const personCard = event.target.closest('.person-card');
    const prayerCard = event.target.closest('.prayer-card');

    if (!personCard && !prayerCard) return;
    
    const personId = personCard.dataset.personId;
    const personRoute = `/people/${personId}`;
    
    if (event.target.classList.contains('delete-prayer-button')){
      const prayerId = prayerCard.dataset.id;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;
      
      await fetch(prayerRoute, {method: "DELETE"});
      prayerCard.remove();
    }
    if (event.target.classList.contains('delete-person-button')){
      await fetch(personRoute, {method: "DELETE"});
      personCard.remove();

    }
  });
}


async function initPage(){
  displayTime();

  initPrayerRequestModal();
  initPrayerEventListeners();

  renderRelationshipButtons();
  renderPersonCards();
  
}

initPage();
