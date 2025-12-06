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
        <label for="prayer-request-text">Prayer Request</label>
        <textarea id="prayer-request-text" name="prayer-request-text" placeholder="Start typing here" rows="5" cols="20" required></textarea>
      </div>
      
      <button type="submit" class="btn save-button save-button-js">Save</button>
    </form>`;
}

function initPrayerRequestModalListeners(){
  document.addEventListener('click', (event) => {
    const addPrayerRequestModal = document.querySelector('.add-prayer-request-modal-js');

    if (event.target.classList.contains('add-prayer-button-js')) {
        addPrayerRequestModal.showModal();
      }
      
      if (event.target.classList.contains('close-prayer-request-modal-js')) {
        addPrayerRequestModal.close();
      }
    });
}

// TO DO: Make "Custom" editable here and in HTML
async function renderRelationshipDropdown() {
  const response = await fetch("/relationships");
  const relationships = await response.json();

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
      name: prayerRequestForm.name.value,
      relationship: prayerRequestForm.relationship.value,
      prayer: prayerRequestForm['prayer-request-text'].value
    }

    const options = {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formData)
    };
  
    const response = await fetch('/people', options);
    const data = await response.json();

    console.log(`Server reponses\n${data.status}: ${data.message}`); 

    if (data.status === 'success') {
      window.location.href = '/prayer-requests';
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