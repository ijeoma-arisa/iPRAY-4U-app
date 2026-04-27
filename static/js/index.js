import { renderPersonCards } from './person-cards.js';
import { renderRelationshipDropdown } from './relationships.js'
import { initPrayerRequestModal, initCloseModalListeners } from './modals.js';
import { GET_PEOPLE_URL } from './api/endpoints.js';

function initPage(){
  initPrayerRequestModal({onSuccess: () => renderPersonCards(GET_PEOPLE_URL)});
  renderRelationshipDropdown();
  initCloseModalListeners();
}

initPage();