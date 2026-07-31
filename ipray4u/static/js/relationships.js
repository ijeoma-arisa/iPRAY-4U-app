import { 
  GET_PEOPLE_URL, 
  GET_RELATIONSHIPS_URL,
  LOGIN_URL, 
} from './api/endpoints.js';
import { renderPersonCards } from './person-cards.js';
import {
  createRelationshipButtonSkeletonsHTML,
  createRelationshipLoadErrorHTML,
} from './loading-states.js';

function renderRelationshipLoadError(relationshipButtonsRow, selectedRelationship) {
  relationshipButtonsRow.innerHTML = createRelationshipLoadErrorHTML();
  relationshipButtonsRow.setAttribute('aria-busy', 'false');

  const retryButton = relationshipButtonsRow.querySelector('.retry-relationships-js');
  retryButton.addEventListener(
    'click',
    () => renderRelationshipButtons(selectedRelationship),
    { once: true },
  );
}

export async function renderRelationshipDropdown(modal) {
  const response = await fetch(GET_RELATIONSHIPS_URL);
  if (response.status === 401) {
    window.location.href = LOGIN_URL;
    return;
  }
  const {data: relationships} = await response.json();
  
  let relationshipsHTML = '<option value="" disabled selected hidden>Select</option>';

  relationships.forEach(() => {
    relationshipsHTML += '<option></option>';
  });

  const dropdown = modal.querySelector('.relationship-dropdown-js');
  dropdown.innerHTML = relationshipsHTML;
  const renderedOptions = dropdown.querySelectorAll('option');
  relationships.forEach((relationship, index) => {
    const option = renderedOptions[index + 1];
    option.value = relationship.relationship;
    option.textContent = relationship.relationship;
  });
}

export async function renderRelationshipButtons(selectedRelationship) {
  const relationshipButtonsRow = document.querySelector('.relationship-buttons-row-js');
  relationshipButtonsRow.setAttribute('aria-busy', 'true');
  relationshipButtonsRow.innerHTML = createRelationshipButtonSkeletonsHTML();

  try {
    const response = await fetch(GET_RELATIONSHIPS_URL);
    if (response.status === 401) {
      window.location.href = LOGIN_URL;
      return;
    }

    if (!response.ok) {
      throw new Error(`Relationships request failed with status ${response.status}`);
    }

    const { data: relationships } = await response.json();

    let relationshipsHTML = '<button type="button" class="btn relationship-button relationship-button-js relationship-button-all relationship-button-all-js">All</button>';

    relationships.forEach(() => {
      relationshipsHTML +=
      `<button
        type="button"
        class="btn relationship-button relationship-button-js"
      >
      </button>`;
    });

    relationshipButtonsRow.innerHTML = relationshipsHTML;

    const renderedButtons = relationshipButtonsRow.querySelectorAll('.relationship-button-js');
    relationships.forEach((relationship, index) => {
      const button = renderedButtons[index + 1];
      button.classList.add(`relationship-button-${relationship.id}`);
      button.dataset.rel = relationship.relationship.toLowerCase();
      button.textContent = relationship.relationship;
    });

    const selectedButton = selectedRelationship
      ? [...relationshipButtonsRow.querySelectorAll('.relationship-button-js')]
        .find(button => button.dataset.rel === selectedRelationship.toLowerCase())
      : relationshipButtonsRow.querySelector('.relationship-button-all-js');

    if (selectedButton){
      selectedButton.classList.add('is-selected');
    }

    relationshipButtonsRow.setAttribute('aria-busy', 'false');
  } catch (error) {
    console.error(
      'Unable to load relationships',
      { selectedRelationship },
      error,
    );
    renderRelationshipLoadError(relationshipButtonsRow, selectedRelationship);
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
