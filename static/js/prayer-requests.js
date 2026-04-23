import { initPrayerRequestModal } from './index.js';

function displayTime(){
  const today = new Date();
  const options = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
  
  document.querySelector('.current-date-js').innerHTML = today.toLocaleDateString('en-US', options);
}

async function renderRelationshipButtons() {
  const response = await fetch("/api/relationships");
  const {status, data: relationships} = await response.json();

  let relationshipsHTML = '<button class="btn relationship-button relationship-button-fav">Favorites</button>';

  relationships.forEach(relationship => {
    relationshipsHTML += `<button class="btn relationship-button relationship-button-${relationship.id}">${relationship.relationship}</button>`;
  });

  document.querySelector('.relationships-row-js')
    .innerHTML = relationshipsHTML;
}

async function loadPrayers(person_id) {
  const response = await fetch(`/api/people/${person_id}/prayers`);
  const {status, data: prayers} = await response.json();

  let prayersHTML = '';

  prayers.forEach(prayer => {
    prayersHTML += `
          <div class="prayer-card" data-id="${prayer.id}">
            <div class="prayer-text">
              ${prayer.prayer}
            </div>
            <div class="update-prayer-buttons">
              <button 
                class="btn edit-prayer-button edit-prayer-button-js"
                data-person-id="${person_id}"
                data-prayer-id="${prayer.id}"
                data-prayer-text="${prayer.prayer}"
                data-prayer-has-prayed="${prayer.hasPrayed}"  
              >
                <i class="fa fa-pencil" aria-hidden="true"></i>
              </button>
              <button class="btn delete-prayer-button"><i class="fa fa-trash-o" aria-hidden="true"></i></button>
            </div>
          </div>`;
  });
  return prayersHTML;
}

export async function renderPersonCards() {
  const response = await fetch("/api/people");
  const {status, data: persons} = await response.json();
  
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
    const personRoute = `/api/people/${personId}`;
    
    if (event.target.classList.contains('delete-person-button')){
      await fetch(personRoute, {method: "DELETE"});
      personCard.remove();
    }
    
    if (event.target.classList.contains('delete-prayer-button')){
      const prayerId = prayerCard.dataset.id;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;
      
      await fetch(prayerRoute, {method: "DELETE"});
      prayerCard.remove();
    }
  });
}

function renderEditPrayerModal() {
  document.querySelector('.edit-prayer-modal-js').innerHTML =
  `<button class="close-button close-edit-prayer-modal-js" aria-label="Close">&times;</button>
    <form class="edit-prayer-form" method="POST">
      <h2 class="form-title">Edit Prayer</h2>
      <div class="form-data">
        <label for="prayer">Prayer Request</label>
        <textarea id="prayer" name="prayer" placeholder="Enter prayer here" rows="5" cols="20" required></textarea>
      </div>
      <button type="submit" name="submit" class="btn save-button save-button-js">Save</button>
    </form>`;
}

function initEditPrayerModalListeners(){
  const editPrayerModal = document.querySelector('.edit-prayer-modal-js');

  document.addEventListener('click', (event) => {
    if (event.target.classList.contains('edit-prayer-button-js')) {
      const editPrayerButton = event.target.closest('.edit-prayer-button-js');

      const personId = editPrayerButton.dataset.personId;
      const prayerId = editPrayerButton.dataset.prayerId;
      const prayerText = editPrayerButton.dataset.prayerText;

      if (personId && prayerId && prayerText){
          const editPrayerForm = document.querySelector('.edit-prayer-form');
          editPrayerForm.dataset.personId = personId; 
          editPrayerForm.dataset.prayerId = prayerId; 
          editPrayerForm.elements.prayer.value = prayerText;
      }

      editPrayerModal.showModal();
    }

    if (event.target.classList.contains('close-edit-prayer-modal-js')){
      editPrayerModal.close();
    }
  });
}

async function handleEditPrayerInput(){
  const editPrayerForm = document.querySelector('.edit-prayer-form');

  editPrayerForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = {
      prayer: editPrayerForm.elements.prayer.value
    }

    const options = {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formData)
    };

    const prayerRoute = `/api/people/${editPrayerForm.dataset.personId}/prayers/${editPrayerForm.dataset.prayerId}`;

    console.log(prayerRoute);

    const response = await fetch(prayerRoute, options);
    const { status, message } = await response.json();

    console.log(`${status}:${message}`);

    if (status === 'success') {
      const editPrayerModal = document.querySelector('.edit-prayer-modal-js');
      renderPersonCards();

      editPrayerForm.elements.prayer.value = "";
      editPrayerModal.close();
    }
  });
}

function initEditPrayerModal(){
  renderEditPrayerModal();
  initEditPrayerModalListeners();
  handleEditPrayerInput();
}

async function initPage(){
  displayTime();

  initPrayerRequestModal();
  initPrayerEventListeners();

  initEditPrayerModal();

  renderRelationshipButtons();
  renderPersonCards();
  
}

initPage();
