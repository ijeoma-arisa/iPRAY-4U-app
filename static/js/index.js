import { renderPersonCards } from './person-cards.js';
import { initPrayerRequestModal, initCloseModalListeners } from './modals.js';
import { GET_PEOPLE_URL } from './api/endpoints.js';

function initPage(){
  initPrayerRequestModal({onSuccess: () => window.location.href = '/prayer-requests'});
  initCloseModalListeners();
}

initPage();