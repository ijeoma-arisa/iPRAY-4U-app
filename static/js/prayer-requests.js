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
              <button class="prayed-prayer-button" data-has-prayed="0">Pray</button>
              <button class="edit-prayer-button">Edit</button>
              <button class="delete-prayer-button">Delete</button>
            </div>
          </div>`;
  });

  prayersHTML += `
    <div class="prayer-card" data-id="add" style="display: flex; justify-content: center; border:none;">
      <button class="btn add-prayer-button add-prayer-button-js">
        Add New Prayer Request
      </button>
    </div>`
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
            <button class="delete-person-button delete-person-button-js">Delete Person</button>
          </div>
          <div class="prayer-cards-section">
            ${prayersHTML}
          </div>
        </div>`;
  }

  document.querySelector('.prayer-request-cards')
    .innerHTML = personHTML;
}

function renderDeletePersonModal() {
  document.querySelector('.delete-person-modal-js').innerHTML =
  `
  <button class="close-button close-delete-person-modal-js" aria-label="Close">&times;</button>
    <h2>Are you sure you want to delete?</h3>
    <div class="confirm-decline-buttons">
      <button class="confirm-delete-button confirm-delete-button-js">Yes</button>
      <button class="decline-delete-button decline-delete-button-js">No</button>
    </div>
  `;
}

function initDeletePersonModalListeners() {
   document.addEventListener('click', (event) => {
    const deletePersonModal = document.querySelector('.delete-person-modal-js');

    if (event.target.classList.contains('delete-person-button-js')) {
        deletePersonModal.showModal();
    }

    if (event.target.classList.contains('close-delete-person-modal-js') ||
        event.target.classList.contains('decline-delete-button-js')) 
      {
          deletePersonModal.close();
      }
    });
}

function initPrayerEventListeners() {
  document.addEventListener('click', async (event) => {
  const prayerRequestCard = event.target.closest('.prayer-request-card');
  const prayerCard = event.target.closest('.prayer-card');

  if (!prayerRequestCard && !prayerCard) return;
  
  const personId = prayerRequestCard.dataset.personId;
  const prayerId = prayerCard.dataset.id;

  const personRoute = `/people/${personId}`;
  const prayerRoute = `${personRoute}/prayers/${prayerId}`;

  if (event.target.classList.contains('prayed-prayer-button')){
    let hasPrayed = Number(event.target.dataset.hasPrayed);
    hasPrayed = hasPrayed ? 0 : 1; 
    
    const options = {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({has_prayed: hasPrayed})
    };

    await fetch(prayerRoute, options);

    event.target.dataset.hasPrayed = hasPrayed;
    event.target.textContent = hasPrayed ? 'Prayed' : 'Pray';

  }

  if (event.target.classList.contains('edit-prayer-button')){
    // TO DO
  }

  if (event.target.classList.contains('delete-prayer-button')){
    await fetch(prayerRoute, {method: "DELETE"});
    prayerCard.remove();
  }

  if (event.target.classList.contains('confirm-delete-button-js')){
    const request = await fetch(personRoute, {method: "DELETE"});
    const response = request.json()

    if (response.status === 'success'){
      console.log(response.message);
      prayerRequestCard.remove();
      document.querySelector('.delete-person-modal-js').close();
    }
    else {
      console.log(response.message);
    }
  }
  });
}


async function initPage(){
  displayTime();

  renderDeletePersonModal();
  initDeletePersonModalListeners();
  
  initPrayerRequestModal();
  initPrayerEventListeners();

  renderRelationshipButtons();
  renderPrayerRequests();
  
}

initPage();
