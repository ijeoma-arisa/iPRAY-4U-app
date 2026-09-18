import { initPrayerRequestModal, initCloseModalListeners } from './modals.js';
import { prefersReducedMotion } from './utils.js';

const launchDemoVideos = document.querySelectorAll('.launch-demo-video');

function playLaunchDemo() {
  launchDemoVideos.forEach((video) => {
    video.play().catch((error) => {
      console.error('Launch demo playback failed:', error);
    });
  });
}

function restartLaunchDemo() {
  // iOS Safari can leave an interrupted video in a stalled state.
  // Reload the media before resuming to recover playback reliably.
  launchDemoVideos.forEach((video) => {
    video.load();
  });

  playLaunchDemo();
}

function handleVisibilityChange() {
  if (document.visibilityState === 'visible') {
    requestAnimationFrame(playLaunchDemo);
  }
}

function handlePageShow(event) {
  if (event.persisted) {
    restartLaunchDemo();
    return;
  }

  playLaunchDemo();
}

function handleLaunchDemoPlaying(event) {
  const launchDemoVideo = event.currentTarget;
  launchDemoVideo.classList.add('is-ready');
}

function initDemoVideoListeners() {
  if (!launchDemoVideos.length || prefersReducedMotion()) {
    return;
  }

  window.addEventListener('pageshow', handlePageShow);
  document.addEventListener('visibilitychange', handleVisibilityChange);

  launchDemoVideos.forEach((video) => {
    video.addEventListener('playing', handleLaunchDemoPlaying);
  });

  playLaunchDemo();
}

function initPage() {
  initDemoVideoListeners();

  initPrayerRequestModal({
    onSuccess: () => window.location.href = '/prayer-requests'
  });

  initCloseModalListeners();
}

initPage();
