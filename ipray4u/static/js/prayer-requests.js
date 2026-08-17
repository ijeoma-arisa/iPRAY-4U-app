import { initModals, openModal } from './modals.js';
import { renderPersonCards } from './person-cards.js';
import { renderRelationshipButtons, initRelationshipButtonsRowListener } from './relationships.js';
import { GET_PEOPLE_URL } from './api/endpoints.js';
import { buildPeopleApiUrl } from './utils.js';
import { fetchWithCsrf } from './api/client.js';
import {
  clearMutationFeedback,
  mutationErrorMessage,
  mutationResponse,
  restoreMutationControl,
  setMutationPending,
  showMutationFeedback,
  showQueuedMutationSuccess,
} from './mutation-feedback.js';


function displayTime(){
  const currentTime = document.querySelector('.current-date-js');
  if (!currentTime) return;
  
  const today = new Date();
  const options = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
  
  currentTime.textContent = today.toLocaleDateString('en-US', options);
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
      deleteTitle.textContent = 'Delete Person';
      itemToDeleteType.textContent = 'person';
      itemToDelete.textContent = personCard.dataset.personName;

      deleteItemModal.dataset.route = personRoute;
      deleteItemModal.dataset.itemId = personCard.id;
      deleteItemModal.dataset.itemType = 'person';
      clearMutationFeedback();

      openModal(deleteItemModal);
    }
    
    if (deletePrayerButton && prayerCard){
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;

      deleteTitle.textContent = 'Delete Prayer';
      itemToDeleteType.textContent = 'prayer';
      itemToDelete.textContent = prayerCard.dataset.prayerText;

      deleteItemModal.dataset.route = prayerRoute;
      deleteItemModal.dataset.itemId = prayerCard.id;
      deleteItemModal.dataset.itemType = 'prayer request';
      clearMutationFeedback();

      openModal(deleteItemModal);
    }
    
    if (markPrayedButton && prayerCard){
      if (markPrayedButton.dataset.mutationPending === 'true') return;
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;

      const toggledHasPrayed = prayerCard.dataset.hasPrayed === "true" ? false : true;
      clearMutationFeedback();
      const pendingName = toggledHasPrayed
        ? 'Marking prayer request as prayed'
        : 'Marking prayer request as unprayed';
      const pendingState = setMutationPending(markPrayedButton, pendingName, {
        region: prayerCard,
        compact: true,
      });

      const data = {
        ['has_prayed']: toggledHasPrayed,
      };
      
      const options = {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
      };
      
      try {
        const response = await fetchWithCsrf(prayerRoute, options);
        await mutationResponse(
          response,
          'Unable to update prayer request. Please try again.',
        );
      } catch (error) {
        showMutationFeedback(
          mutationErrorMessage(
            error,
            'Unable to update prayer request. Please try again.',
          ),
          'error',
        );
        return;
      } finally {
        restoreMutationControl(markPrayedButton, pendingState);
      }

      const successMessage = toggledHasPrayed
        ? 'Prayer request marked as prayed.'
        : 'Prayer request marked as unprayed.';
      const refreshFailureMessage = toggledHasPrayed
        ? 'Prayer request was marked as prayed, but the page could not refresh. Please try again.'
        : 'Prayer request was marked as unprayed, but the page could not refresh. Please try again.';

      try {
        const url = `${GET_PEOPLE_URL}${window.location.search}`;
        await onSuccess(url);
        showMutationFeedback(
          successMessage,
          'success',
          { autoDismiss: true },
        );
      } catch (error) {
        console.error(refreshFailureMessage, error);
        showMutationFeedback(refreshFailureMessage, 'error');
      }
    }
  });
}


function initPage(){
  displayTime();
  showQueuedMutationSuccess();

  initPageLoadListeners();
  initRelationshipButtonsRowListener();
  
  initPrayerEventListeners({
    onSuccess: (url) => renderPersonCards(url, false, true),
  });
  initModals({
    onSuccess: () => renderPersonCards(buildPeopleApiUrl(), false, true),
  });
}

initPage();
