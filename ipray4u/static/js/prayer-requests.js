import { initModals } from './modals.js';
import { renderPersonCards } from './person-cards.js';
import { renderRelationshipButtons, initRelationshipButtonsRowListener } from './relationships.js';
import { GET_PEOPLE_URL } from './api/endpoints.js';
import { buildPeopleApiUrl } from './utils.js';
import { fetchWithCsrf } from './api/client.js';


function displayTime(){
  const currentTime = document.querySelector('.current-date-js');
  if (!currentTime) return;
  
  const today = new Date();
  const options = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
  
  document.querySelector('.current-date-js').innerHTML = today.toLocaleDateString('en-US', options);
}

function initPageLoadListeners(){
  document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const relationship = params.get('rel');

    if (relationship){
      renderPersonCards(`${GET_PEOPLE_URL}?${params}`, true);
      renderRelationshipButtons(relationship);
      return;
    }

    renderPersonCards(GET_PEOPLE_URL, true);
    renderRelationshipButtons(null);
  });
}

function initPrayerEventListeners({ onSuccess }) {
  const personCards = document.querySelector('.person-cards-js');
  const deleteItemModal = document.querySelector('.delete-item-modal-js');
  const deleteTitle = document.querySelector('.delete-title-js');
  const itemToDeleteType = document.querySelector('.item-to-delete-type');
  const itemToDelete = document.querySelector('.item-to-delete');

  personCards.addEventListener('click', async (event) => {
    const personCard = event.target.closest('.person-card-js');
    if (!personCard) return;

    const prayerCard = event.target.closest('.prayer-card-js');

    const deletePersonButton = event.target.closest('.delete-person-button-js');
    const deletePrayerButton = event.target.closest('.delete-prayer-button-js');
    const markPrayedButton = event.target.closest('.mark-prayed-button-js');
    
    const personId = personCard.dataset.personId;
    const personRoute = `${GET_PEOPLE_URL}/${personId}`;
    
    if (deletePersonButton){
      deleteTitle.innerHTML = 'Delete Person';
      itemToDeleteType.innerHTML = 'person';
      itemToDelete.innerHTML = personCard.dataset.personName;

      deleteItemModal.dataset.route = personRoute;
      deleteItemModal.dataset.itemId = personCard.id;

      deleteItemModal.showModal();
    }
    
    if (deletePrayerButton && prayerCard){
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;

      deleteTitle.innerHTML = 'Delete Prayer';
      itemToDeleteType.innerHTML = 'prayer';
      itemToDelete.innerHTML = prayerCard.dataset.prayerText;

      deleteItemModal.dataset.route = prayerRoute;
      deleteItemModal.dataset.itemId = prayerCard.id;

      deleteItemModal.showModal();
    }
    
    if (markPrayedButton && prayerCard){
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;

      const toggledHasPrayed = prayerCard.dataset.hasPrayed === "true" ? false : true;

      const data = {
        ['has_prayed']: toggledHasPrayed,
      };
      
      const options = {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      };
      
      const response = await fetchWithCsrf(prayerRoute, options);
      const { status, message } = await response.json();
      if (status === 'success') {
        const url = `${GET_PEOPLE_URL}${window.location.search}`;
        onSuccess(url);
      }    
    }
  });
}


function initPage(){
  displayTime();

  initPageLoadListeners();
  initRelationshipButtonsRowListener();
  
  initPrayerEventListeners({onSuccess: (url) => renderPersonCards(url)});
  initModals({onSuccess: () => renderPersonCards(buildPeopleApiUrl())});
}

initPage();
