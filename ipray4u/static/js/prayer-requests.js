import { initModals, openModal } from './modals.js';
import {
  createPersonCard,
  createPrayerCard,
  insertPersonCard,
  insertPrayerCard,
  loadPrayers,
  renderPersonCards,
  showPeopleEmptyState,
  showPrayerEmptyState,
  updatePersonCard,
  updatePrayerCard,
} from './person-cards.js';
import {
  initRelationshipButtonsRowListener,
  renderRelationshipButtons,
} from './relationships.js';
import { GET_PEOPLE_URL } from './api/endpoints.js';
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

const DISPLAY_UPDATE_FAILED_MESSAGE =
  'Your change was saved, but the page display could not be updated. Please refresh.';

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

function personMatchesCurrentFilter(person) {
  const selectedRelationship = new URLSearchParams(window.location.search).get('rel');
  return !selectedRelationship
    || person.relationship.toLowerCase() === selectedRelationship.toLowerCase();
}

function findPersonCard(personId) {
  return [...document.querySelectorAll('.person-card-js')]
    .find(personCard => personCard.dataset.personId === String(personId));
}

function findPrayerCard(personCard, prayerId) {
  return [...personCard.querySelectorAll('.prayer-card-js')]
    .find(prayerCard => prayerCard.dataset.prayerId === String(prayerId));
}

async function applyLocalizedMutation({ type, data, personId, itemId }) {
  const personCards = document.querySelector('.person-cards-js');

  if (type === 'add-person') {
    if (!personMatchesCurrentFilter(data)) return;

    // The current POST /api/people response does not include its default prayer.
    const prayers = Array.isArray(data.prayers)
      ? data.prayers
      : await loadPrayers(data.id);
    const newPersonCard = createPersonCard(data, prayers);

    insertPersonCard(newPersonCard);
    return;
  }

  const targetPersonId = personId || data?.person_id || itemId;
  const personCard = findPersonCard(targetPersonId);

  if (type === 'edit-person') {
    const updatedPersonCard = findPersonCard(data.id);

    if (!personMatchesCurrentFilter(data)) {
      updatedPersonCard?.remove();
      showPeopleEmptyState(personCards);
      return;
    }

    if (!updatedPersonCard) throw new Error(`Unable to find person ${data.id}`);

    updatePersonCard(updatedPersonCard, data);
    return;
  }

  if (type === 'delete-person') {
    if (!personCard) throw new Error(`Unable to find person ${itemId}`);
    personCard.remove();
    showPeopleEmptyState(personCards);
    return;
  }
  if (!personCard) throw new Error(`Unable to find person ${targetPersonId}`);

  if (type === 'add-prayer') {
    const newPrayerCard = createPrayerCard(
      data,
      personCard.dataset.personId,
    );

    insertPrayerCard(personCard, newPrayerCard);
  } else if (type === 'edit-prayer') {
    const prayerCard = findPrayerCard(personCard, data.id);
    if (!prayerCard) throw new Error(`Unable to find prayer ${data.id}`);

    updatePrayerCard(prayerCard, data, personCard.dataset.personId);
  } else if (type === 'delete-prayer') {
    const prayerCard = findPrayerCard(personCard, itemId);
    if (!prayerCard) throw new Error(`Unable to find prayer ${itemId}`);

    prayerCard.remove();
    showPrayerEmptyState(personCard);
  }
}

function initPrayerEventListeners() {
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
      deleteItemModal.dataset.itemId = personId;
      deleteItemModal.dataset.personId = personId;
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
      deleteItemModal.dataset.itemId = prayerId;
      deleteItemModal.dataset.personId = personId;
      deleteItemModal.dataset.itemType = 'prayer request';
      clearMutationFeedback();

      openModal(deleteItemModal);
    }
    
    if (markPrayedButton && prayerCard){
      if (markPrayedButton.dataset.mutationPending === 'true') return;
      const prayerId = prayerCard.dataset.prayerId;
      const prayerRoute = `${personRoute}/prayers/${prayerId}`;

      const toggledHasPrayed = prayerCard.dataset.hasPrayed !== 'true';
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
      
      let savedPrayer;
      try {
        const response = await fetchWithCsrf(prayerRoute, options);
        const result = await mutationResponse(
          response,
          'Unable to update prayer request. Please try again.',
        );
        savedPrayer = result.data;
      } catch (error) {
        restoreMutationControl(markPrayedButton, pendingState);
        showMutationFeedback(
          mutationErrorMessage(
            error,
            'Unable to update prayer request. Please try again.',
          ),
          'error',
        );
        return;
      }

      const successMessage = savedPrayer.has_prayed
        ? 'Prayer request marked as prayed.'
        : 'Prayer request marked as unprayed.';

      try {
        restoreMutationControl(markPrayedButton, pendingState);
        updatePrayerCard(prayerCard, savedPrayer, personId);
        showMutationFeedback(
          successMessage,
          'success',
          { autoDismiss: true },
        );
      } catch (error) {
        console.error(
          'Prayer update was saved, but the page display could not be updated.',
          error,
        );
        showMutationFeedback(
          DISPLAY_UPDATE_FAILED_MESSAGE,
          'error',
          { forceGlobal: true },
        );
      } finally {
        const mutationIsStillPending =
          markPrayedButton.dataset.mutationPending === 'true';

        if (markPrayedButton.isConnected && mutationIsStillPending) {
          restoreMutationControl(markPrayedButton, pendingState);
        }
      }
    }
  });
}


function initPage(){
  displayTime();
  showQueuedMutationSuccess();

  initPageLoadListeners();
  initRelationshipButtonsRowListener();
  
  initPrayerEventListeners();
  initModals({ onSuccess: applyLocalizedMutation });
}

initPage();
