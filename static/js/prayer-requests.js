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

// async function 

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
        </div>`;
  }

  document.querySelector('.prayer-request-cards')
    .innerHTML = personHTML;
}


function initPrayerEventListeners() {
  document.addEventListener('click', async (event) => {
  const prayerRequestCard = event.target.closest('.prayer-request-card');
  const personId = prayerRequestCard.dataset.personId;

  const prayerCard = event.target.closest('.prayer-card');
  const prayerId = prayerCard.dataset.id;

  const prayerRoute = `/people/${personId}/prayers/${prayerId}`

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

  });
}


function initPage(){
  displayTime();
  initPrayerEventListeners();
  renderRelationshipButtons();
  renderPrayerRequests();
}

initPage();
