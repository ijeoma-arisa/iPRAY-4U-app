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

function handleVisibilityChange() {
  if (document.visibilityState === 'visible'){
    requestAnimationFrame(playLaunchDemo());
  }
}

function initDemoVideoListeners() {
  window.addEventListener('pageshow', playLaunchDemo);
  document.addEventListener('visibilitychange', handleVisibilityChange)
}

function initPage() {
  initDemoVideoListeners();

  initPrayerRequestModal({
    onSuccess: () => window.location.href = '/prayer-requests'
  });

  initCloseModalListeners();
}

initPage();