import { renderPersonCards } from './person-cards.js';
import { initPrayerRequestModal, initCloseModalListeners } from './modals.js';
import { GET_PEOPLE_URL } from './api/endpoints.js';

function initPage(){
  initPrayerRequestModal({onSuccess: () => renderPersonCards(GET_PEOPLE_URL)});
  initCloseModalListeners();
}

initPage();