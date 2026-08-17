import { GET_PEOPLE_URL } from './api/endpoints.js';
import { renderRelationshipDropdown } from './relationships.js';
import { fetchWithCsrf } from './api/client.js';
import {
  clearMutationFeedback,
  mutationErrorMessage,
  mutationResponse,
  queueMutationSuccess,
  restoreMutationControl,
  setMutationPending,
  showMutationFeedback,
} from './mutation-feedback.js';

export function openModal(modal) {
  if (modal.open) return;

  modal.showModal();
}

function renderPrayerRequestModal() {
  document.querySelector('.add-prayer-request-modal-js').innerHTML = 
    `<button type="button" class="close-button close-modal-js" aria-label="Close">&times;</button>
    <form class="prayer-request-form modal-form-js prayer-request-form-js" method="POST">
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
      const prayerRequestForm = document.querySelector('.prayer-request-form-js');
      clearMutationFeedback();
      
      if (personCard){
        
        const { personId, personName, personRelationship } = personCard.dataset;
        
        if (personId && personName && personRelationship){
          
          prayerRequestForm.dataset.personId = personId;
          
          prayerRequestForm.elements.name.value = personName;
          prayerRequestForm.elements.name.disabled = true;
          
          prayerRequestForm.elements.relationship.value = personRelationship;
          prayerRequestForm.elements.relationship.disabled = true;
        } 
      }

      openModal(addPrayerRequestModal);
  });
}

async function handlePrayerRequestInput({ onSuccess }){
  const prayerRequestForm = document.querySelector('.prayer-request-form-js');

  prayerRequestForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (prayerRequestForm.dataset.submitting === 'true') return;

    const saveButton = prayerRequestForm.querySelector('.save-button-js');
    prayerRequestForm.dataset.submitting = 'true';
    const pendingState = setMutationPending(saveButton, 'Saving prayer request', {
      region: prayerRequestForm,
    });
    clearMutationFeedback();
    
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
    
    const personExists = prayerRequestForm.dataset.personId !== undefined;
    
    const prayerRoute = personExists ? 
        `${GET_PEOPLE_URL}/${prayerRequestForm.dataset.personId}/prayers`:
        GET_PEOPLE_URL
        
    try {
      const response = await fetchWithCsrf(prayerRoute, options);
      await mutationResponse(
        response,
        'Unable to save prayer request. Please try again.',
      );
    } catch (error) {
      showMutationFeedback(
        mutationErrorMessage(error, 'Unable to save prayer request. Please try again.'),
        'error',
      );
      return;
    } finally {
      delete prayerRequestForm.dataset.submitting;
      restoreMutationControl(saveButton, pendingState);
    }

    const addPrayerRequestModal = document.querySelector('.add-prayer-request-modal-js');
    const redirectsToDashboard = !document.querySelector('.person-cards-js');
    addPrayerRequestModal.close();

    if (redirectsToDashboard) {
      queueMutationSuccess('Prayer request added.');
      await onSuccess();
      return;
    }

    try {
      await onSuccess();
      showMutationFeedback(
        'Prayer request added.',
        'success',
        { autoDismiss: true },
      );
    } catch (error) {
      console.error('Prayer request was added, but the page could not refresh.', error);
      showMutationFeedback(
        'Prayer request was added, but the page could not refresh. Please try again.',
        'error',
      );
    }
  });

}

export function initPrayerRequestModal({ onSuccess }){
  renderPrayerRequestModal();
  initPrayerRequestModalListeners();
  handlePrayerRequestInput({ onSuccess });

  const prayerRequestModal = document.querySelector('.add-prayer-request-modal-js');
  renderRelationshipDropdown(prayerRequestModal);
}

function initDeleteModalListeners({ onSuccess }){
  const deleteItemModal = document.querySelector('.delete-item-modal-js');

  deleteItemModal.addEventListener('click', async (event) => {
    const confirmDeleteButton = event.target.closest('.confirm-delete-button-js');
    if (!confirmDeleteButton) return;
    if (deleteItemModal.dataset.submitting === 'true') return;

    const route = deleteItemModal.dataset.route;
    const itemId = deleteItemModal.dataset.itemId;
    const itemType = deleteItemModal.dataset.itemType;
    deleteItemModal.dataset.submitting = 'true';
    clearMutationFeedback();
    const pendingState = setMutationPending(
      confirmDeleteButton,
      itemType === 'person' ? 'Deleting person' : 'Deleting prayer request',
      { region: deleteItemModal },
    );

    try {
      const response = await fetchWithCsrf(route, {method: "DELETE"});
      await mutationResponse(
        response,
        `Unable to delete ${itemType}. Please try again.`,
      );
    } catch (error) {
      showMutationFeedback(
        mutationErrorMessage(error, `Unable to delete ${itemType}. Please try again.`),
        'error',
      );
      return;
    } finally {
      delete deleteItemModal.dataset.submitting;
      restoreMutationControl(confirmDeleteButton, pendingState);
    }

    document.getElementById(itemId)?.remove();
    deleteItemModal.close();

    const successMessage = itemType === 'person'
      ? 'Person deleted.'
      : 'Prayer request deleted.';
    const refreshFailureMessage = itemType === 'person'
      ? 'Person was deleted, but the page could not refresh. Please try again.'
      : 'Prayer request was deleted, but the page could not refresh. Please try again.';

    try {
      await onSuccess();
      showMutationFeedback(successMessage, 'success', { autoDismiss: true });
    } catch (error) {
      console.error(refreshFailureMessage, error);
      showMutationFeedback(refreshFailureMessage, 'error');
    }
  
  });
}

function initDeleteModal({ onSuccess }){
  initDeleteModalListeners({ onSuccess });
}


function initEditPrayerModalListeners(){
  const editPrayerModal = document.querySelector('.edit-prayer-modal-js');

  document.addEventListener('click', (event) => {
    const editPrayerButton = event.target.closest('.edit-prayer-button-js');

    if (!editPrayerButton) return;
    
    const prayerCard = event.target.closest('.prayer-card-js');
    if (!prayerCard) return;

    const { personId, prayerId, prayerText, hasPrayed } = prayerCard.dataset;

    if (personId && prayerId && prayerText && hasPrayed){
      const editPrayerForm = document.querySelector('.edit-prayer-form-js');

      editPrayerForm.dataset.personId = personId;
      editPrayerForm.dataset.prayerId = prayerId;

      editPrayerForm.elements.prayer.value = prayerText;
      editPrayerForm.elements['has-prayed'].checked = hasPrayed === 'true';
    }

    clearMutationFeedback();
    openModal(editPrayerModal);
  });
}

async function handleEditPrayerInput({ onSuccess }){
  const editPrayerForm = document.querySelector('.edit-prayer-form-js');

  editPrayerForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (editPrayerForm.dataset.submitting === 'true') return;

    const saveButton = editPrayerForm.querySelector('.save-button-js');
    editPrayerForm.dataset.submitting = 'true';
    clearMutationFeedback();
    const pendingState = setMutationPending(saveButton, 'Updating prayer request', {
      region: editPrayerForm,
    });

    const formData = {
      prayer: editPrayerForm.elements.prayer.value,
      ['has_prayed']: editPrayerForm.elements['has-prayed'].checked,
    }

    const options = {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formData)
    };

    const personId = editPrayerForm.dataset.personId;
    const prayerId = editPrayerForm.dataset.prayerId;
    const prayerRoute = `${GET_PEOPLE_URL}/${personId}/prayers/${prayerId}`;

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
      delete editPrayerForm.dataset.submitting;
      restoreMutationControl(saveButton, pendingState);
    }

    document.querySelector('.edit-prayer-modal-js').close();

    try {
      await onSuccess();
      showMutationFeedback(
        'Prayer request updated.',
        'success',
        { autoDismiss: true },
      );
    } catch (error) {
      const message = 'Prayer request was updated, but the page could not refresh. Please try again.';
      console.error(message, error);
      showMutationFeedback(message, 'error');
    }
  });
}

function initEditPrayerModal({ onSuccess }){
  initEditPrayerModalListeners();
  handleEditPrayerInput({ onSuccess });
}


function initEditPersonModalListeners(){
  const editPersonModal = document.querySelector('.edit-person-modal-js');

  document.addEventListener('click', (event) => {
    const editPersonButton = event.target.closest('.edit-person-button-js');
    if (!editPersonButton) return;
    
    const personCard = event.target.closest('.person-card-js');
    if (!personCard) return;

    const personId = personCard.dataset.personId;
    const personName = personCard.dataset.personName;
    const personRelationship = personCard.dataset.personRelationship;

    if (personId && personName && personRelationship){
      const editPersonForm = document.querySelector('.edit-person-form-js');
      editPersonForm.dataset.personId = personId;
      editPersonForm.dataset.personName = personName;
      editPersonForm.dataset.personRelationship = personRelationship;

      editPersonForm.elements.name.value = personName;
      editPersonForm.elements.relationship.value = personRelationship;
    }

    clearMutationFeedback();
    openModal(editPersonModal);
  });
}

async function handleEditPersonInput({ onSuccess }){
  const editPersonForm = document.querySelector('.edit-person-form-js');

  editPersonForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (editPersonForm.dataset.submitting === 'true') return;

    const saveButton = editPersonForm.querySelector('.save-button-js');
    editPersonForm.dataset.submitting = 'true';
    clearMutationFeedback();
    const pendingState = setMutationPending(
      saveButton,
      'Updating person',
      { region: editPersonForm },
    );

    const formData = {
      name: editPersonForm.elements.name.value,
      relationship: editPersonForm.elements.relationship.value
    }

    const options = {
      method: "PATCH",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(formData)
    };

    const personId = editPersonForm.dataset.personId;

    const personRoute = `${GET_PEOPLE_URL}/${personId}`;

    try {
      const response = await fetchWithCsrf(personRoute, options);
      await mutationResponse(
        response,
        'Unable to update person. Please try again.',
      );
    } catch (error) {
      showMutationFeedback(
        mutationErrorMessage(
          error,
          'Unable to update person. Please try again.',
        ),
        'error',
      );
      return;
    } finally {
      delete editPersonForm.dataset.submitting;
      restoreMutationControl(saveButton, pendingState);
    }

    document.querySelector('.edit-person-modal-js').close();

    try {
      await onSuccess();
      showMutationFeedback(
        'Person updated.',
        'success',
        { autoDismiss: true },
      );
    } catch (error) {
      const message = 'Person was updated, but the page could not refresh. Please try again.';
      console.error(message, error);
      showMutationFeedback(message, 'error');
    }
  });
}

function initEditPersonModal({ onSuccess }){
  const editPersonModal = document.querySelector('.edit-person-modal-js');
  renderRelationshipDropdown(editPersonModal);
  
  initEditPersonModalListeners();
  handleEditPersonInput({ onSuccess });
}

export function initCloseModalListeners(){
  document.querySelectorAll('.modal-js').forEach((modal) =>{
    
    modal.addEventListener('close', (event) => {
      Object.keys(modal.dataset).forEach(key => {
        delete modal.dataset[key];
      });

      const form = modal.querySelector('.modal-form-js');
      
      if (form){
        form.reset();

        form.querySelectorAll('[disabled]').forEach(elem => elem.disabled = false);

        Object.keys(form.dataset).forEach(key => {
          delete form.dataset[key];
        });
      }
    })

    modal.addEventListener('click', (event) => {
      const closeModalButton = event.target.closest('.close-modal-js');
      const bounds = modal.getBoundingClientRect();
      const clickedBackdrop = event.target === modal && (
        event.clientX < bounds.left ||
        event.clientX > bounds.right ||
        event.clientY < bounds.top ||
        event.clientY > bounds.bottom
      );

      if (!closeModalButton && !clickedBackdrop) return;

      modal.close();
    });
  })
}

export function initModals({ onSuccess }){
  initPrayerRequestModal({ onSuccess });
  initEditPersonModal({ onSuccess });

  initEditPrayerModal({ onSuccess });  
  initDeleteModal({ onSuccess });
  
  initCloseModalListeners();
}
