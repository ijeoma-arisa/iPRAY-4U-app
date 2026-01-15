import { renderPersonCards } from './prayer-requests.js';

function renderPrayerRequestModal() {
  document.querySelector('.add-prayer-request-modal-js').innerHTML =
  `<button class="close-button close-prayer-request-modal-js" aria-label="Close">&times;</button>
    <form class="prayer-request-form" method="POST">
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

    if (event.target.classList.contains('add-prayer-button-js')) {
      
      const addPrayerButton = event.target.closest('.add-prayer-button-js');
      
      const personId = addPrayerButton.dataset.personId;
      const personName = addPrayerButton.dataset.personName;
      const personRelationship = addPrayerButton.dataset.personRelationship;
      
      if (personId && personName && personRelationship) {
        const prayerRequestForm = document.querySelector('.prayer-request-form');
        prayerRequestForm.dataset.personId = personId; 

        prayerRequestForm.elements.name.value = personName;
        prayerRequestForm.elements.name.readOnly = true;
        
        prayerRequestForm.elements.relationship.value = personRelationship;
        prayerRequestForm.elements.relationship.disabled = true;
      }

      addPrayerRequestModal.showModal();
    }
    
    if (event.target.classList.contains('close-prayer-request-modal-js')) {
      addPrayerRequestModal.close();
    }
    });
}

async function renderRelationshipDropdown() {
  const response = await fetch("/relationships");
  const {status, data: relationships} = await response.json();
  
  let relationshipsHTML = '<option value="Select...">Select...</option>';

  relationships.forEach(relationship => {
    relationshipsHTML += `<option value="${relationship.relationship}">${relationship.relationship}</option>`;
  });

  document.querySelector('.relationship-dropdown-js').innerHTML = relationshipsHTML;
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
        `/people/${prayerRequestForm.dataset.personId}/prayers`:
        '/people'
        
    const response = await fetch(prayerRoute, options);
    const {status, message} = await response.json();

    console.log(`${status}:${message}`);

    if (status === 'success') {
      const addPrayerRequestModal = document.querySelector('.add-prayer-request-modal-js');
      renderPersonCards();
      
      prayerRequestForm.elements.prayer.value = "";
      addPrayerRequestModal.close();
    }

  });

}

export function initPrayerRequestModal(){
  renderPrayerRequestModal();
  initPrayerRequestModalListeners();
  renderRelationshipDropdown();
  handlePrayerRequestInput();
}

initPrayerRequestModal();