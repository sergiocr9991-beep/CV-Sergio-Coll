(() => {
  'use strict';
  const section = document.getElementById('proyectos');
  const track = section.querySelector('.projects');
  const cards = [...track.querySelectorAll('.project-card')];
  const mobile = matchMedia('(max-width:720px)');
  const reduced = matchMedia('(prefers-reduced-motion:reduce)');
  const english = document.documentElement.lang === 'en';
  track.id = 'project-carousel';
  const controls = document.createElement('div');
  controls.className = 'project-carousel-controls';
  controls.innerHTML = `<div class="carousel-dots" aria-hidden="true"></div>
    <button class="carousel-arrow carousel-prev" type="button" aria-controls="project-carousel" aria-label="${english ? 'Previous project' : 'Proyecto anterior'}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m14 5-7 7 7 7"/></svg></button>
    <button class="carousel-arrow carousel-next" type="button" aria-controls="project-carousel" aria-label="${english ? 'Next project' : 'Proyecto siguiente'}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="m10 5 7 7-7 7"/></svg></button>
    <span class="carousel-sr-only" role="status" aria-live="polite"></span>`;
  track.before(controls);
  const previous = controls.querySelector('.carousel-prev');
  const next = controls.querySelector('.carousel-next');
  const dots = controls.querySelector('.carousel-dots');
  const status = controls.querySelector('[role=status]');
  const visibleCards = () => cards.filter(card => !card.hidden && card.style.display !== 'none');
  const position = card => card.getBoundingClientRect().left - track.getBoundingClientRect().left + track.scrollLeft - 2;
  let frame = 0;
  let lastStatus = '';
  function currentIndex(visible) {
    let index = 0;
    visible.forEach((card, i) => { if (Math.abs(position(card)-track.scrollLeft) < Math.abs(position(visible[index])-track.scrollLeft)) index = i; });
    // The last card cannot align all the way left because the track includes a next-card preview.
    if(track.scrollLeft > 1 && track.scrollLeft >= track.scrollWidth-track.clientWidth-3) index = visible.length-1;
    return index;
  }
  function update() {
    frame = 0;
    const visible = visibleCards();
    const index = visible.length ? currentIndex(visible) : 0;
    track.classList.toggle('is-single', visible.length === 1);
    previous.disabled = index === 0;
    next.disabled = index >= visible.length-1;
    if(dots.children.length !== visible.length) dots.innerHTML = visible.map(() => '<i class="carousel-dot"></i>').join('');
    [...dots.children].forEach((dot,i) => dot.classList.toggle('is-current',i===index));
    const label = english ? `Project ${index+1} of ${visible.length}` : `Proyecto ${index+1} de ${visible.length}`;
    if(mobile.matches && label !== lastStatus){ status.textContent=label; lastStatus=label; }
  }
  function move(direction) {
    const visible = visibleCards();
    const target = visible[Math.max(0,Math.min(visible.length-1,currentIndex(visible)+direction))];
    if(target) track.scrollTo({left:position(target),behavior:reduced.matches?'instant':'smooth'});
  }
  previous.addEventListener('click',()=>move(-1));
  next.addEventListener('click',()=>move(1));
  track.addEventListener('scroll',()=>{if(!frame)frame=requestAnimationFrame(update);},{passive:true});
  section.querySelectorAll('.filter').forEach(button=>button.addEventListener('click',()=>{
    // Existing language-specific filter handlers run first; reset only the horizontal track.
    track.scrollTo({left:0,behavior:'instant'});
    update();
  }));
  function setMode() {
    track.scrollTo({left:0,behavior:'instant'});
    if(mobile.matches){track.setAttribute('role','region');track.setAttribute('aria-roledescription',english?'carousel':'carrusel');track.setAttribute('aria-label',english?'Projects':'Proyectos');}
    else{track.removeAttribute('role');track.removeAttribute('aria-roledescription');track.removeAttribute('aria-label');}
    update();
  }
  mobile.addEventListener('change',setMode);
  window.addEventListener('resize',()=>{if(!frame)frame=requestAnimationFrame(update);},{passive:true});
  setMode();
})();
