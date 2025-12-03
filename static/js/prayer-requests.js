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

  let prayersHTML = '<div>';

  prayers.forEach(prayer => {
    prayersHTML += `
        <div class="prayer-cell-${person_id}-${prayer.id}">
          ${prayer.text} ${prayer.has_prayed ? 'X':''}
        </div>`;
  });
  prayersHTML += `</div>`

  return prayersHTML;
}

// TO DO: Add time that updates every minute
async function renderPrayerRequests() {
  const response = await fetch("/people");
  const persons = await response.json();
  
  let personHTML = '';

  for (const person of persons){
    personHTML += `
        <div class="row">
          <div class="id-cell-${person.id}">${person.id}</div>
          <div class="name-cell-${person.id}">${person.name}</div>
          <div class="rel-cell-${person.id}">${person.relationship}</div>
        </div>`;

        const prayersHTML = await loadPrayers(person.id);
        personHTML += `${prayersHTML}</div>`
  }

  document.querySelector('.prayer-requests-body')
    .innerHTML = personHTML;
}

function initPage(){
  displayTime();
  renderRelationshipButtons();
  renderPrayerRequests();
}

initPage();
