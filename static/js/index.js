import { renderPersonCards, renderRelationshipDropdown } from './ui.js';
import { initPrayerRequestModal, initCloseModalListeners } from './modals.js';

function initPage(){
  initPrayerRequestModal();
  renderRelationshipDropdown();
  initCloseModalListeners();
}

initPage();