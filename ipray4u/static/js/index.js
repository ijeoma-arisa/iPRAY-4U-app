import { initPrayerRequestModal, initCloseModalListeners } from './modals.js';

const launchDemoVideo = document.querySelector('.launch-demo-video');

function playLaunchDemo() {
  if (!launchDemoVideo) {
    return;
  }

  launchDemoVideo.play().catch(() => {});
}

function initLaunchDemoVideo() {
  window.addEventListener('pageshow', playLaunchDemo);
}

function initPage() {
  initLaunchDemoVideo();

  initPrayerRequestModal({
    onSuccess: () => window.location.href = '/prayer-requests'
  });

  initCloseModalListeners();
}

initPage();