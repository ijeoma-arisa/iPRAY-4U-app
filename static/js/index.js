import { renderPersonCards } from './prayer-requests.js';


export function initCloseModalListeners(){
  document.querySelectorAll('.modal-js').forEach((modal) =>{
    modal.addEventListener('click', (event) => {
      const closeModalButton = event.target.closest('.close-modal-js');
      if (!closeModalButton) return;

      const form = event.target.closest('modal-form-js');
      if (form) form.reset();

      modal.close();
    });
  })
}

function renderPrayerRequestModal() {
  document.querySelector('.add-prayer-request-modal-js').innerHTML = 
    `<button class="close-button close-modal-js" aria-label="Close">&times;</button>
    <form class="prayer-request-form modal-form-js" method="POST">
      <h2 class="form-title">New Prayer Request</h2>
      <div class="form-data">
        <label for="name">Name</label>
        <input type="text" id="name" name="name" placeholder="Name" required/>
      </div>
      <div class="form-data">
        <label for="relationship">Relationship</label> 
        <select id="relationship" name="relationship" class="relationship-dropdown-js" required>
        </select>
      </div>
      <div class="form-data">
        <label for="prayer">Prayer Request</label>
        <textarea id="prayer" name="prayer" placeholder="Enter prayer here" rows="5" cols="20" required></textarea>
      </div>
      <button type="submit" name="submit" class="btn save-button save-button-js">Save</button>
    </form>`;
}

function initPrayerRequestModalListeners(){
    const addPrayerRequestModal = document.querySelector('.add-prayer-request-modal-js');
    
    document.addEventListener('click', (event) => {
      
      const addPrayerButton = event.target.closest('.add-prayer-button-js');
      if (!addPrayerButton) return;
      
      const personCard = event.target.closest('.person-card-js');
      if (personCard){
        
        const { personId, personName, personRelationship } = personCard.dataset;
        
        if (personId && personName && personRelationship){
          const prayerRequestForm = document.querySelector('.prayer-request-form');
          
          prayerRequestForm.elements.id = personId;
          
          prayerRequestForm.elements.name.value = personName;
          prayerRequestForm.elements.name.disabled = true;
          
          prayerRequestForm.elements.relationship.value = personRelationship;
          prayerRequestForm.elements.relationship.disabled = true;
        }
      }

      addPrayerRequestModal.showModal();


      
      // const personId = addPrayerButton.dataset.personId;
      // const personName = addPrayerButton.dataset.personName;
      // const personRelationship = addPrayerButton
      // if (event.target.classList.contains('add-prayer-button-js')) {
        
      //   // const addPrayerButton = event.target.closest('.add-prayer-button-js');
        
      //   const personId = addPrayerButton.dataset.personId;
      //   const personName = addPrayerButton.dataset.personName;
      //   const personRelationship = addPrayerButton.dataset.personRelationship;
        
      //   if (personId && personName && personRelationship) {
      //     const prayerRequestForm = document.querySelector('.prayer-request-form');
      //     prayerRequestForm.dataset.personId = personId; 

      //     prayerRequestForm.elements.name.value = personName;
      //     prayerRequestForm.elements.name.readOnly = true;
          
      //     prayerRequestForm.elements.relationship.value = personRelationship;
      //     prayerRequestForm.elements.relationship.disabled = true;
      //   }

      //   addPrayerRequestModal.showModal();
      // }

      // if (event.target.classList.contains('close-prayer-request-modal-js')) {
      //   addPrayerRequestModal.close();
      // }
  });

  const prayerRequestForm = document.querySelector('.prayer-request-form');

  addPrayerRequestModal.addEventListener('close', () => {
    prayerRequestForm.reset();
    renderPersonCards();
  });
}

export async function renderRelationshipDropdown() {
  const response = await fetch("/api/relationships");
  const {status, data: relationships} = await response.json();
  
  let relationshipsHTML = '<option value="" disabled selected hidden>Select...</option>';

  relationships.forEach(relationship => {
    relationshipsHTML += `<option value="${relationship.relationship}">${relationship.relationship}</option>`;
  });

  document.querySelectorAll('.relationship-dropdown-js').forEach((dropdown) => dropdown.innerHTML = relationshipsHTML);
}

async function handlePrayerRequestInput(){
  const prayerRequestForm = document.querySelector('.prayer-request-form');

  prayerRequestForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const formData = {
      name: prayerRequestForm.elements.name.value,
      relationship: prayerRequestForm.elements.relationship.value,
      prayer: prayerRequestForm.elements.prayer.value,
    }

    const options = {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formData)
    };
    
    const personExists = prayerRequestForm.dataset.personId !== undefined && prayerRequestForm.elements.name.readOnly && prayerRequestForm.elements.relationship.disabled;
    
    const prayerRoute = personExists ? 
        `/api/people/${prayerRequestForm.dataset.personId}/prayers`:
        '/api/people'
        
    const response = await fetch(prayerRoute, options);
    const {status, message} = await response.json();

    if (status === 'success') {
      const addPrayerRequestModal = document.querySelector('.add-prayer-request-modal-js');
      addPrayerRequestModal.close();
    }

  });

}

export function initPrayerRequestModal(){
  renderPrayerRequestModal();
  initPrayerRequestModalListeners();
  handlePrayerRequestInput();
}

initPrayerRequestModal();
renderRelationshipDropdown();
initCloseModalListeners();