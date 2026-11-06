(() => {
  'use strict';
  const intro = document.getElementById('signature-intro');
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let animations = [];
  function replaySignature() {
    animations.forEach(animation => animation.cancel());
    animations = [];
    intro.style.animation = 'none';
    if (reduced.matches) { intro.style.visibility = 'hidden'; return; }
    intro.style.visibility = 'visible';
    const start = document.timeline.currentTime;
    function animate(element, frames, options) {
      const animation = element.animate(frames, {...options, fill: 'both'});
      animation.startTime = start;
      animations.push(animation);
    }
    intro.querySelectorAll('.ink-gesture').forEach(path => {
      animate(path, [{strokeDashoffset: '100'}, {strokeDashoffset: '0'}], {
        delay: Number(path.dataset.delay), duration: Number(path.dataset.duration), easing: 'linear'
      });
    });
    animate(intro.querySelector('.signature-intro-seal'), [
      {opacity: 0, transform: 'translateY(8px) scale(.965)'},
      {opacity: 1, transform: 'translateY(0) scale(1)'}
    ], {duration: 420, easing: 'cubic-bezier(.2,.8,.2,1)'});
    animate(intro.querySelector('.signature-intro-wordmark'), [
      {opacity: 0, transform: 'translateY(5px)'}, {opacity: 1, transform: 'translateY(0)'}
    ], {delay: 880, duration: 320, easing: 'ease-out'});
    animate(intro, [{opacity: 1, visibility: 'visible'}, {opacity: 0, visibility: 'hidden'}],
      {delay: 1280, duration: 220, easing: 'ease-in-out'});
  }
  // Inline SVG belongs to this document, never to a cached animated image.
  replaySignature();
  window.addEventListener('pageshow', event => { if (event.persisted) replaySignature(); });
})();
