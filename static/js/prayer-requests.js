import { initPrayerRequestModal, renderRelationshipDropdown } from './index.js';

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
          <div class="prayer-card prayer-card-js" 
            data-prayer-id="${prayer.id}"
            data-prayer-text="${prayer.prayer}"
            data-has-prayed="${prayer['has_prayed']}"  
          >
            <div class="prayer-text">
              ${prayer.prayer}
              ${prayer['has_prayed'] === 1 ? "Prayed!" : ""}
            </div>
            <div class="update-prayer-buttons">
              <button 
                class="btn mark-prayed-button mark-prayed-button-js"
              >
                <i class="fa-solid fa-hands-praying" aria-hidden="true"></i>
              </button>

              <button 
                class="btn edit-prayer-button edit-prayer-button-js"
                data-person-id="${person_id}"
                data-prayer-id="${prayer.id}"
                data-prayer-text="${prayer.prayer}"
                data-has-prayed="${prayer['has_prayed']}"  
              >
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

export async function renderPersonCards() {
  const response = await fetch("/api/people");
  const {status, data: persons} = await response.json();
  
  let personHTML = '';

  for (const person of persons){
    const prayersHTML = await loadPrayers(person.id);
    
    personHTML += `
        <div class="person-card person-card-js" data-person-id=${person.id}>
          <div class="person-info-section">
            <h3>${person.name}</h3>
            <p>${person.relationship}</p>
            <div class="person-buttons">
              <button 
                class="btn edit-person-button edit-person-button-js"
                data-person-id="${person.id}"
                data-person-name="${person.name}"
                data-person-relationship="${person.relationship}"
              >
                <i class="fa-solid fa-pencil" aria-hidden="true"></i> 
                Edit
              </button>
              <button class="btn delete-person-button delete-person-button-js"><i class="fa-solid fa-trash" aria-hidden="true"></i> Delete</button>
            </div>
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

  document.querySelector('.person-cards-js')
    .innerHTML = personHTML;
}

function initPrayerEventListeners() {
  const personCards = document.querySelector('.person-cards-js');

  personCards.addEventListener('click', async (event) => {
    const personCard = event.target.closest('.person-card-js');
    const prayerCard = event.target.closest('.prayer-card-js');

    if (!personCard && !prayerCard) return;
    
    const personId = personCard.dataset.personId;
    const personRoute = `/api/people/${personId}`;
    
    if (event.target.classList.contains('delete-person-button-js')){
      await fetch(personRoute, {method: "DELETE"});
      personCard.remove();
    }
    
    if (event.target.classList.contains('delete-prayer-button-js')){
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;
      
      await fetch(prayerRoute, {method: "DELETE"});
      prayerCard.remove();
    }
    
    if (event.target.classList.contains('mark-prayed-button-js')){
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;

      const toggledHasPrayed = prayerCard.dataset.hasPrayed === "1" ? 0 : 1;

      const data = {
        ['has_prayed']: toggledHasPrayed,
      };
      
      const options = {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      };
      
      const response = await fetch(prayerRoute, options);
      const { status, message } = await response.json();
      console.log(`${status}: ${message}`);
      if (status === 'success') {
        renderPersonCards();
      }    
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
    console.log(event.target);
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

    const response = await fetch(prayerRoute, options);
    const { status, message } = await response.json();

    if (status === 'success') {
      const editPrayerModal = document.querySelector('.edit-prayer-modal-js');
      renderPersonCards();

      editPrayerForm.elements.prayer.value = "";
      editPrayerModal.close();
    }
  });
}

function renderEditPersonModal(){
  document.querySelector('.edit-person-modal-js').innerHTML =
  `<button class="close-button close-edit-person-modal-js" aria-label="Close">&times;</button>
    <form class="edit-person-form" method="POST">
      <h2 class="form-title">Edit Person</h2>
      <div class="form-data">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" placeholder="Name" required/>
      </div>
      <div class="form-data">
        <label for="relationship">Relationship</label> 
        <select id="relationship" name="relationship" class="relationship-dropdown-js" required>
        </select>
      </div>
      <button type="submit" name="submit" class="btn save-button save-button-js">Save</button>
    </form>`;
}

function initEditPersonModalListeners(){
  // const editPersonModal = document.querySelector('.edit-person-modal-js');
  // const editPersonButton = document.querySelector('.edit-person-button-js');
  //   editPersonButton.addEventListener('click', () => {
  //     const personId = editPersonButton.dataset.personId;
  //     const personName = editPersonButton.dataset.personName;
  //     const personRelationship = editPersonButton.dataset.personRelationship;

  //     if (personId && personName && personRelationship){
  //       const editPersonForm = document.querySelector('.edit-person-form');
  //       editPersonForm.dataset.personId = personId;
  //       editPersonForm.dataset.personName = personName;
  //       editPersonForm.dataset.personRelationship = personRelationship;

  //       editPersonForm.elements.name.value = personName;
  //       editPersonForm.elements.relationship.value = personRelationship;
  //     }

  //     editPersonModal.showModal();
    

  //   if (event.target.classList.contains('close-edit-person-modal-js')){
  //     editPersonModal.close();
  //   }
  //   });

  document.addEventListener('click', (event) => {
    if (event.target.classList.contains('edit-person-button-js')) {
      const editPersonButton = event.target.closest('.edit-person-button-js');

      const personId = editPersonButton.dataset.personId;
      const personName = editPersonButton.dataset.personName;
      const personRelationship = editPersonButton.dataset.personRelationship;

      if (personId && personName && personRelationship){
        const editPersonForm = document.querySelector('.edit-person-form');
        editPersonForm.dataset.personId = personId;
        editPersonForm.dataset.personName = personName;
        editPersonForm.dataset.personRelationship = personRelationship;

        editPersonForm.elements.name.value = personName;
        editPersonForm.elements.relationship.value = personRelationship;
      }

      editPersonModal.showModal();
    }

    if (event.target.classList.contains('close-edit-person-modal-js')){
      editPersonModal.close();
    }
  });
}

async function handleEditPersonInput(){
  const editPersonForm = document.querySelector('.edit-person-form');

  editPersonForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = {
      name: editPersonForm.elements.name.value,
      relationship: editPersonForm.elements.relationship.value
    }

    const options = {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formData)
    };

    const personRoute = `/api/people/${editPersonForm.dataset.personId}`;

    const response = await fetch(personRoute, options);
    const { status, message } = await response.json();

    if (status === 'success') {
      const editPersonModal = document.querySelector('.edit-person-modal-js');
      renderPersonCards();

      editPersonModal.close();
    }
  });
}


function initEditPrayerModal(){
  renderEditPrayerModal();
  initEditPrayerModalListeners();
  handleEditPrayerInput();
}

function initEditPersonModal(){
  renderEditPersonModal();
  initEditPersonModalListeners();
  handleEditPersonInput();
}

async function initPage(){
  displayTime();
  initPrayerRequestModal();
  initEditPersonModal();
  initEditPrayerModal();

  
  renderRelationshipButtons();
  renderRelationshipDropdown();
  
  renderPersonCards();
  initPrayerEventListeners();
  
}

initPage();
