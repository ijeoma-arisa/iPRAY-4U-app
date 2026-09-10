import { initPrayerRequestModal, initCloseModalListeners } from './modals.js';

const launchDemoVideo = document.querySelector('.launch-demo-video');

function playLaunchDemo() {
  if (!launchDemoVideo) {
    return;
  }

  launchDemoVideo.play().catch((error) => {
    console.error('Launch demo playback failed:', error);
  });
}

function restartLaunchDemo() {
  if (!launchDemoVideo) {
    return;
  }

  // iOS Safari can leave an interrupted video in a stalled state.
  // Reload the media before resuming to recover playback reliably.
  launchDemoVideo.load();
  playLaunchDemo();
}

function handleVisibilityChange() {
  if (document.visibilityState === 'visible'){
    requestAnimationFrame(restartLaunchDemo);
  }
}

function handlePageShow(event) {
  if (event.persisted) {
    restartLaunchDemo();
  }
}

function initDemoVideoListeners() {
  window.addEventListener('pageshow', handlePageShow);
  document.addEventListener('visibilitychange', handleVisibilityChange);
}

function initPage() {
  initDemoVideoListeners();

  initPrayerRequestModal({
    onSuccess: () => window.location.href = '/prayer-requests'
  });

  initCloseModalListeners();
}

initPage();
