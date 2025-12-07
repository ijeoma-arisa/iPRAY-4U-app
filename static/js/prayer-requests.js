import {initPrayerRequestModal} from './index.js';

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

// TO DO: Add time that updates every minute
async function renderPrayerRequests() {
  const response = await fetch("/people");
  const persons = await response.json();
  
  let personHTML = '';

  for (const person of persons){
    const prayersHTML = await loadPrayers(person.id);
    
    personHTML += `
        <div class="prayer-request-card" data-person-id=${person.id}>
          <div class="person-info-section">
            <h3>${person.name}</h3>
            <p>${person.relationship}</p>
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

  document.querySelector('.prayer-request-cards')
    .innerHTML = personHTML;
}

function initPrayerEventListeners() {
  const prayerRequestCards = document.querySelector('.prayer-request-cards');

  prayerRequestCards.addEventListener('click', async (event) => {
  const prayerRequestCard = event.target.closest('.prayer-request-card');
  const prayerCard = event.target.closest('.prayer-card');

  if (!prayerRequestCard && !prayerCard) return;
  
  const personId = prayerRequestCard.dataset.personId;
  const prayerId = prayerCard.dataset.id;

  const personRoute = `/people/${personId}`;
  const prayerRoute = `${personRoute}/prayers/${prayerId}`;

  if (event.target.classList.contains('delete-prayer-button')){
    await fetch(prayerRoute, {method: "DELETE"});
    prayerCard.remove();
  }
  });
}


async function initPage(){
  displayTime();

  initPrayerRequestModal();
  initPrayerEventListeners();

  renderRelationshipButtons();
  renderPrayerRequests();
  
}

initPage();
