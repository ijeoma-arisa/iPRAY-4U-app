function initPrayerRequestModal(){
  const addPrayerRequestModal = document.querySelector('.add-prayer-request-modal-js');
  
  document.querySelector('.add-button-js')
  .addEventListener('click', () => {
    addPrayerRequestModal.showModal();
  });
  
  document.querySelector('.close-prayer-request-modal-js')
    .addEventListener('click', () => {
      addPrayerRequestModal.close();
  });
  
  document.querySelector('.add-button-js')
  .addEventListener('click', () =>{
    console.log('Adding prayer request')
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

async function initPage(){
  initPrayerRequestModal();
  await renderRelationshipDropdown();
}

initPage();