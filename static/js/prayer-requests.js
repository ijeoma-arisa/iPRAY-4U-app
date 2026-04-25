import { initPrayerRequestModal, renderRelationshipDropdown, initCloseModalListeners } from './index.js';

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

  document.querySelector('.relationships-row-js').innerHTML = relationshipsHTML;
}

async function loadPrayers(person_id) {
  const response = await fetch(`/api/people/${person_id}/prayers`);
  const {status, data: prayers} = await response.json();

  let prayersHTML = '';

  prayers.forEach(prayer => {
    prayersHTML += `
          <div
            id="prayer-${prayer.id}" 
            class="prayer-card prayer-card-js" 
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
        <div
            id="person-${person.id}" 
            class="person-card person-card-js" 
            data-person-id="${person.id}"
            data-person-name="${person.name}"
            data-person-relationship="${person.relationship}"
          >
          <div class="person-info-section">
            <h3>${person.name}</h3>
            <p>${person.relationship}</p>
            <div class="person-buttons">
              <button class="btn edit-person-button edit-person-button-js">
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
            data-person-relationship="${person.relationship}"
          >
            Add Prayer 
          </button>
        </div>`;
  }

  document.querySelector('.person-cards-js')
    .innerHTML = personHTML;
}

function initPrayerEventListeners() {
  const personCards = document.querySelector('.person-cards-js');
  const deleteItemModal = document.querySelector('.delete-item-modal-js');
  const deleteTitle = document.querySelector('.delete-title-js');
  const itemToDeleteType = document.querySelector('.item-to-delete-type');
  const itemToDelete = document.querySelector('.item-to-delete');

  personCards.addEventListener('click', async (event) => {
    const personCard = event.target.closest('.person-card-js');
    const prayerCard = event.target.closest('.prayer-card-js');

    if (!personCard && !prayerCard) return;
    
    const personId = personCard.dataset.personId;
    const personRoute = `/api/people/${personId}`;
    
    if (event.target.classList.contains('delete-person-button-js')){
      deleteTitle.innerHTML = 'Delete Person';
      itemToDeleteType.innerHTML = 'person';
      itemToDelete.innerHTML = personCard.dataset.personName;

      deleteItemModal.dataset.route = personRoute;
      deleteItemModal.dataset.itemId = personCard.id;

      deleteItemModal.showModal();
    }
    
    if (event.target.classList.contains('delete-prayer-button-js')){
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;

      deleteTitle.innerHTML = 'Delete Prayer';
      itemToDeleteType.innerHTML = 'prayer';
      itemToDelete.innerHTML = prayerCard.dataset.prayerText;

      deleteItemModal.dataset.route = prayerRoute;
      deleteItemModal.dataset.itemId = prayerCard.id;

      deleteItemModal.showModal();
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
      if (status === 'success') {
        renderPersonCards();
      }    
    }

  });
}

function initDeleteModalListeners(){
  const deleteItemModal = document.querySelector('.delete-item-modal-js');

  deleteItemModal.addEventListener('click', async (event) => {
    if (event.target.classList.contains('confirm-delete-button-js')){
      const route = deleteItemModal.dataset.route;
      const itemId = deleteItemModal.dataset.itemId;
      const item = document.getElementById(itemId);
      
      await fetch(route, {method: "DELETE"});
      item?.remove();
      renderPersonCards();

      deleteItemModal.close();
    }
  });
}


function renderEditPrayerModal() {
  document.querySelector('.edit-prayer-modal-js').innerHTML =
  `<button class="close-button close-modal-js" aria-label="Close">&times;</button>
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
  `<button class="close-button close-modal-js" aria-label="Close">&times;</button>
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
  const editPersonModal = document.querySelector('.edit-person-modal-js');

  document.addEventListener('click', (event) => {
    if (event.target.classList.contains('edit-person-button-js')) {
      const personCard = event.target.closest('.person-card-js');

      const personId = personCard.dataset.personId;
      const personName = personCard.dataset.personName;
      const personRelationship = personCard.dataset.personRelationship;

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
  initDeleteModalListeners();
  initCloseModalListeners();
}

initPage();
