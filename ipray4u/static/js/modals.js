import { GET_PEOPLE_URL } from './api/endpoints.js';
import { renderRelationshipDropdown } from './relationships.js';
import { fetchWithCsrf } from './api/client.js';
import {
  clearMutationFeedback,
  isFormCorrectableMutationError,
  mutationErrorMessage,
  mutationResponse,
  queueMutationSuccess,
  restoreMutationControl,
  setMutationPending,
  showMutationFeedback,
} from './mutation-feedback.js';

const DISPLAY_UPDATE_FAILED_MESSAGE =
  'Your change was saved, but the page display could not be updated. Please refresh.';

function clearFormError(errorElement) {
  errorElement.textContent = '';
  errorElement.hidden = true;
}

function showFormError(errorElement, message) {
  errorElement.textContent = message;
  errorElement.hidden = false;
}

function initFormErrorClearing(form, errorElement) {
  form.addEventListener('input', () => {
    if (!errorElement.hidden) clearFormError(errorElement);
  });
}

export function openModal(modal) {
  if (modal.open) return;

  modal.querySelector('.modal-mutation-feedback-js')?.replaceChildren();
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
      <p class="form-error prayer-request-error-js" role="alert" hidden></p>
      <button type="submit" name="submit" class="btn save-button save-button-js">Save</button>
    </form>
    <div class="modal-mutation-feedback modal-mutation-feedback-js"></div>`;
}

function initPrayerRequestModalListeners(){
    const addPrayerRequestModal = document.querySelector('.add-prayer-request-modal-js');
    
    document.addEventListener('click', (event) => {
      
      const addPrayerButton = event.target.closest('.add-prayer-button-js');
      if (!addPrayerButton) return;
      
      const personCard = event.target.closest('.person-card-js');
      const prayerRequestForm = document.querySelector('.prayer-request-form-js');
      const formError = prayerRequestForm.querySelector('.prayer-request-error-js');
      clearFormError(formError);
      
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
  const formError = prayerRequestForm.querySelector('.prayer-request-error-js');

  initFormErrorClearing(prayerRequestForm, formError);

  prayerRequestForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (prayerRequestForm.dataset.submitting === 'true') return;

    const saveButton = prayerRequestForm.querySelector('.save-button-js');
    prayerRequestForm.dataset.submitting = 'true';
    const pendingState = setMutationPending(saveButton, 'Saving prayer request', {
      region: prayerRequestForm,
    });
    clearFormError(formError);
    
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
    let savedData;

    try {
      const response = await fetchWithCsrf(prayerRoute, options);
      const result = await mutationResponse(
        response,
        'Unable to save prayer request. Please try again.',
      );
      savedData = result.data;
    } catch (error) {
      if (isFormCorrectableMutationError(error)) {
        showFormError(formError, error.message);
        return;
      }

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
    const personId = prayerRequestForm.dataset.personId;
    addPrayerRequestModal.close();

    if (redirectsToDashboard) {
      queueMutationSuccess('Prayer request added.');
      await onSuccess();
      return;
    }

    try {
      await onSuccess({
        type: personExists ? 'add-prayer' : 'add-person',
        data: savedData,
        personId,
      });
      showMutationFeedback(
        'Prayer request added.',
        'success',
        { autoDismiss: true },
      );
    } catch (error) {
      console.error(
        'Prayer request was saved, but the page display could not be updated.',
        error,
      );
      showMutationFeedback(
        DISPLAY_UPDATE_FAILED_MESSAGE,
        'error',
        { forceGlobal: true },
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
    const personId = deleteItemModal.dataset.personId;
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

    deleteItemModal.close();

    const successMessage = itemType === 'person'
      ? 'Person deleted.'
      : 'Prayer request deleted.';
    try {
      await onSuccess({
        type: itemType === 'person' ? 'delete-person' : 'delete-prayer',
        itemId,
        personId,
      });
      showMutationFeedback(successMessage, 'success', { autoDismiss: true });
    } catch (error) {
      console.error(
        'Deletion was saved, but the page display could not be updated.',
        error,
      );
      showMutationFeedback(
        DISPLAY_UPDATE_FAILED_MESSAGE,
        'error',
        { forceGlobal: true },
      );
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

    clearFormError(
      editPrayerModal.querySelector('.edit-prayer-error-js'),
    );
    openModal(editPrayerModal);
  });
}

async function handleEditPrayerInput({ onSuccess }){
  const editPrayerForm = document.querySelector('.edit-prayer-form-js');
  const formError = editPrayerForm.querySelector('.edit-prayer-error-js');

  initFormErrorClearing(editPrayerForm, formError);

  editPrayerForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (editPrayerForm.dataset.submitting === 'true') return;

    const saveButton = editPrayerForm.querySelector('.save-button-js');
    editPrayerForm.dataset.submitting = 'true';
    clearFormError(formError);
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
    let savedData;

    try {
      const response = await fetchWithCsrf(prayerRoute, options);
      const result = await mutationResponse(
        response,
        'Unable to update prayer request. Please try again.',
      );
      savedData = result.data;
    } catch (error) {
      if (isFormCorrectableMutationError(error)) {
        showFormError(formError, error.message);
        return;
      }

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
      await onSuccess({
        type: 'edit-prayer',
        data: savedData,
        personId,
        prayerId,
      });
      showMutationFeedback(
        'Prayer request updated.',
        'success',
        { autoDismiss: true },
      );
    } catch (error) {
      console.error(DISPLAY_UPDATE_FAILED_MESSAGE, error);
      showMutationFeedback(
        DISPLAY_UPDATE_FAILED_MESSAGE,
        'error',
        { forceGlobal: true },
      );
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

    clearFormError(
      editPersonModal.querySelector('.edit-person-error-js'),
    );
    openModal(editPersonModal);
  });
}

async function handleEditPersonInput({ onSuccess }){
  const editPersonForm = document.querySelector('.edit-person-form-js');
  const formError = editPersonForm.querySelector('.edit-person-error-js');

  initFormErrorClearing(editPersonForm, formError);

  editPersonForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (editPersonForm.dataset.submitting === 'true') return;

    const saveButton = editPersonForm.querySelector('.save-button-js');
    editPersonForm.dataset.submitting = 'true';
    clearFormError(formError);
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
    let savedData;

    try {
      const response = await fetchWithCsrf(personRoute, options);
      const result = await mutationResponse(
        response,
        'Unable to update person. Please try again.',
      );
      savedData = result.data;
    } catch (error) {
      if (isFormCorrectableMutationError(error)) {
        showFormError(formError, error.message);
        return;
      }

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
      await onSuccess({ type: 'edit-person', data: savedData, personId });
      showMutationFeedback(
        'Person updated.',
        'success',
        { autoDismiss: true },
      );
    } catch (error) {
      console.error(DISPLAY_UPDATE_FAILED_MESSAGE, error);
      showMutationFeedback(
        DISPLAY_UPDATE_FAILED_MESSAGE,
        'error',
        { forceGlobal: true },
      );
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
      const containsForm = modal.querySelector('.modal-form-js') !== null;
      const dismissFromBackdrop = clickedBackdrop && !containsForm;

      if (!closeModalButton && !dismissFromBackdrop) return;

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
