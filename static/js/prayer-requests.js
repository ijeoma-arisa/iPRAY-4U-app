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
    relationshipsHTML += ` <button class="btn relationship-button relationship-button-${relationship.id}">${relationship.relationship}</button>`;
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
          <div class="prayer-card">
            <div class="prayer-text">
              ${prayer.text}
            </div>
            <div class="update-prayer-buttons">
              <button class="prayed-prayer-button">Prayed</button>
              <button class="edit-prayer-button">Edit</button>
              <button class="archive-prayer-button">Archive</button>
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
        <div class="prayer-request-card">
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

function initPage(){
  displayTime();
  renderRelationshipButtons();
  renderPrayerRequests();
}

initPage();
