import { GET_PEOPLE_URL, GET_RELATIONSHIPS_URL } from './api/endpoints.js';
import { renderPersonCards } from './person-cards.js';

export async function renderRelationshipDropdown() {
  const response = await fetch(GET_RELATIONSHIPS_URL);
  const {status, data: relationships} = await response.json();
  
  let relationshipsHTML = '<option value="" disabled selected hidden>Select</option>';

  relationships.forEach(relationship => {
    relationshipsHTML += `<option value="${relationship.relationship}">${relationship.relationship}</option>`;
  });

  document.querySelectorAll('.relationship-dropdown-js').forEach((dropdown) => dropdown.innerHTML = relationshipsHTML);
}

export async function renderRelationshipButtons() {
  const response = await fetch(GET_RELATIONSHIPS_URL);
  const { status, data: relationships } = await response.json();

  let relationshipsHTML = '<button class="btn relationship-button relationship-button-js relationship-button-fav">Favorites</button>';

  relationships.forEach(relationship => {
    relationshipsHTML += 
    `<button 
      class="btn relationship-button relationship-button-js relationship-button-${relationship.id}"
      data-rel=${relationship.relationship}
    >
      ${relationship.relationship}
    </button>`;
  });

  document.querySelector('.relationship-buttons-row-js').innerHTML = relationshipsHTML;
}

function updateRelationshipButtons(relationshipButton){
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

    if (relationshipButton.classList.contains('is-selected')){
      relationshipButton.classList.remove('is-selected');
      renderPersonCards(GET_PEOPLE_URL);
      return;
    }

    const relationship = relationshipButton.dataset.rel;
    if (!relationship) return;

    const params = new URLSearchParams({ rel: relationship})
    const relationshipURL = `${GET_PEOPLE_URL}?${params}`;

    updateRelationshipButtons(relationshipButton);
    renderPersonCards(relationshipURL);
  })

}
