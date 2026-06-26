import { 
  GET_PEOPLE_URL, 
  GET_RELATIONSHIPS_URL,
  LOGIN_URL, 
} from './api/endpoints.js';
import { renderPersonCards } from './person-cards.js';

export async function renderRelationshipDropdown(modal) {
  const response = await fetch(GET_RELATIONSHIPS_URL);
  if (response.status === 401) {
    window.location.href = LOGIN_URL;
    return;
  }
  const {status, data: relationships} = await response.json();
  
  let relationshipsHTML = '<option value="" disabled selected hidden>Select</option>';

  relationships.forEach(relationship => {
    relationshipsHTML += `<option value="${relationship.relationship}">${relationship.relationship}</option>`;
  });

  modal.querySelector('.relationship-dropdown-js').innerHTML = relationshipsHTML;
}

export async function renderRelationshipButtons(selectedRelationship) {
  const response = await fetch(GET_RELATIONSHIPS_URL);
  if (response.status === 401) {
    window.location.href = LOGIN_URL;
    return;
  }
  const { status, data: relationships } = await response.json();

  let relationshipsHTML = '<button type="button" class="btn relationship-button relationship-button-js relationship-button-all relationship-button-all-js">All</button>';

  relationships.forEach(relationship => {
    relationshipsHTML += 
    `<button
      type="button" 
      class="btn relationship-button relationship-button-js relationship-button-${relationship.id}" 
      data-rel="${relationship.relationship.toLowerCase()}"
    >
      ${relationship.relationship}
    </button>`;
  });

  const relationshipButtonsRow = document.querySelector('.relationship-buttons-row-js');
  relationshipButtonsRow.innerHTML = relationshipsHTML;
  
  const selectedButton = selectedRelationship
    ? relationshipButtonsRow.querySelector(`[data-rel="${selectedRelationship.toLowerCase()}"]`)
    : relationshipButtonsRow.querySelector('.relationship-button-all-js');

  if (selectedButton){
    selectedButton.classList.add('is-selected');
  }
}

export function selectRelationshipButton(relationshipButton){
  const relationshipButtonsRow = document.querySelector('.relationship-buttons-row-js');
  
  relationshipButtonsRow.querySelectorAll('.relationship-button-js').forEach((button) => {
    button.classList.remove('is-selected');
  });
  
  relationshipButton.classList.add('is-selected');
}

export function initRelationshipButtonsRowListener(){
  const relationshipButtonsRow = document.querySelector('.relationship-buttons-row-js');
  
  relationshipButtonsRow.addEventListener('click', async (event) => {
    const relationshipButton = event.target.closest('.relationship-button-js');
    if (!relationshipButton) return;
    
    const allButton = relationshipButtonsRow.querySelector('.relationship-button-all-js');
    
    if (relationshipButton.classList.contains('is-selected')){
      
      if (relationshipButton === allButton) return;

      selectRelationshipButton(allButton);
      renderPersonCards(GET_PEOPLE_URL, true);
      window.history.pushState({}, '', window.location.pathname);
      return;
    }
    
    if (relationshipButton === allButton){
      selectRelationshipButton(allButton);
      renderPersonCards(GET_PEOPLE_URL, true);
      window.history.pushState({}, '', window.location.pathname);
    }

    const relationship = relationshipButton.dataset.rel;
    if (!relationship) return;

    const params = new URLSearchParams({ rel: relationship});
    window.history.pushState({}, '', `?${params}`);

    const relationshipURL = `${GET_PEOPLE_URL}?${params}`;

    selectRelationshipButton(relationshipButton);
    renderPersonCards(relationshipURL, true);
  })

}
