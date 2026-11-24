/* EventLocator homepage frontend. Event cards come from the PredictHQ API (HomePage/views.py). */
(() => {
  const homePage = document.querySelector('.home-page');
  if (!homePage) return;
  const categoryButtons = Array.from(homePage.querySelectorAll('.category-button'));
  const eventCards = Array.from(homePage.querySelectorAll('.event-card'));
  const filterMessage = document.getElementById('filter-message');
  const upcomingEvents = homePage.querySelector('.upcoming-events');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (upcomingEvents && !reducedMotion && 'IntersectionObserver' in window) {
    homePage.classList.add('animations-enabled');
    const scrollObserver = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) {
        upcomingEvents.classList.add('events-visible');
        scrollObserver.disconnect();
      }
    }, { threshold: 0.10, rootMargin: '0px 0px -12% 0px' });
    scrollObserver.observe(upcomingEvents);
  }

  // The original Omaha banner is the background and is ALWAYS first on page load.
  // Imported slideshow1..slideshow20 (and any later images) are shuffled each round.
  // Change slides automatically every three seconds. No manual slideshow controls.
  // Crucial: never fade OUT the current image while fading IN the next image.
  // The outgoing image stays fully opaque underneath until the new image is ready.
  const banner = homePage.querySelector('.home-banner');
  const slideLayers = banner ? Array.from(banner.querySelectorAll('.banner-slide')) : [];
  const slideFiles = Array.isArray(window.slideshowImages) ? window.slideshowImages : [];
  const validSlideFiles = slideFiles.filter(file => typeof file === 'string' && /^slide\d{2,3}\.(png|jpe?g|webp|gif|avif)$/i.test(file));
  const slideFolder = banner?.dataset.imageFolder || '';
  const slideImages = validSlideFiles.map(file => slideFolder + encodeURIComponent(file));
  const slideIntervalMs = 3000;
  const fadeDurationMs = 900;
  let slideOrder = [];
  let currentPosition = 0;
  let lastSlide = -1;
  let currentLayer = -1; // -1: only the original Omaha banner is visible.
  let isChangingSlide = false;
  const loadedImages = new Map();

  function shuffleSlides() {
    slideOrder = slideImages.map((_, slideIndex) => slideIndex);
    for (let i = slideOrder.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [slideOrder[i], slideOrder[j]] = [slideOrder[j], slideOrder[i]];
    }
    if (slideOrder.length > 1 && slideOrder[0] === lastSlide) [slideOrder[0], slideOrder[1]] = [slideOrder[1], slideOrder[0]];
    currentPosition = 0;
  }

  function getNextSlide() {
    if (currentPosition >= slideOrder.length) shuffleSlides();
    const slideIndex = slideOrder[currentPosition++];
    lastSlide = slideIndex;
    return slideIndex;
  }

  function loadImage(imagePath) {
    if (!loadedImages.has(imagePath)) {
      loadedImages.set(imagePath, new Promise((resolve, reject) => {
        const image = new Image();
        image.onload = () => resolve(imagePath);
        image.onerror = () => reject(new Error('Image failed to load: ' + imagePath));
        image.src = imagePath;
      }));
    }
    return loadedImages.get(imagePath);
  }

  function loadNextImage() {
    if (currentPosition < slideOrder.length) loadImage(slideImages[slideOrder[currentPosition]]).catch(() => {});
  }

  const waitForFrame = () => new Promise(resolve => requestAnimationFrame(resolve));
  function waitForTransition(layer) {
    return new Promise(resolve => {
      let finished = false;
      let fadeTimeout;
      const finishFade = () => {
        if (finished) return;
        finished = true;
        clearTimeout(fadeTimeout);
        layer.removeEventListener('transitionend', onTransitionEnd);
        resolve();
      };
      const onTransitionEnd = event => { if (event.target === layer && event.propertyName === 'opacity') finishFade(); };
      layer.addEventListener('transitionend', onTransitionEnd);
      fadeTimeout = setTimeout(finishFade, fadeDurationMs + 150);
    });
  }

  async function showNextSlide() {
    if (isChangingSlide || document.hidden || !slideImages.length || slideLayers.length !== 2) return;
    isChangingSlide = true;
    try {
      for (let attempt = 0; attempt < slideImages.length; attempt++) {
        const slideIndex = getNextSlide();
        let imagePath;
        try { imagePath = await loadImage(slideImages[slideIndex]); }
        catch (error) { console.warn('EventLocator slideshow: ' + error.message); continue; }
        if (document.hidden) break;

        const nextLayerIndex = currentLayer < 0 ? 0 : 1 - currentLayer;
        const nextLayer = slideLayers[nextLayerIndex];
        const currentLayerElement = currentLayer < 0 ? null : slideLayers[currentLayer];

        // Prepare the next layer in front of the current photo.
        nextLayer.style.transition = 'none';
        nextLayer.style.opacity = '0';
        nextLayer.style.zIndex = '2';
        nextLayer.style.backgroundImage = `url("${imagePath}")`;
        // Two frames guarantee that zero opacity is painted before the fade starts.
        await waitForFrame();
        await waitForFrame();
        nextLayer.style.transition = `opacity ${fadeDurationMs}ms ease-in-out`;
        nextLayer.style.opacity = '1';
        await waitForTransition(nextLayer);

        // ONLY after the next image is fully visible can the old image be hidden.
        // This prevents the original Omaha banner appearing between photos.
        if (currentLayerElement) {
          currentLayerElement.style.transition = 'none';
          currentLayerElement.style.opacity = '0';
          currentLayerElement.style.zIndex = '0';
        }
        nextLayer.style.zIndex = '1';
        currentLayer = nextLayerIndex;
        loadNextImage();
        break;
      }
    } finally { isChangingSlide = false; }
  }

  if (slideImages.length && slideLayers.length === 2) {
    shuffleSlides();
    loadNextImage();
    // Page scrolling still works for Upcoming Events; only slideshow controls are absent.
    window.setInterval(() => { void showNextSlide(); }, slideIntervalMs);
  }

  let selectedCategory = null;
  categoryButtons.forEach(button => {
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => {
      selectedCategory = selectedCategory === button.dataset.category ? null : button.dataset.category;
      categoryButtons.forEach(btn => btn.setAttribute('aria-pressed', String(btn.dataset.category === selectedCategory)));
      let visibleCount = 0;
      eventCards.forEach(card => {
        const showCard = !selectedCategory || card.dataset.category === selectedCategory;
        card.hidden = !showCard;
        if (showCard) visibleCount++;
      });
      if (filterMessage) {
        filterMessage.hidden = visibleCount > 0;
        filterMessage.textContent = selectedCategory ? `No upcoming ${selectedCategory.toLowerCase()} events found nearby.` : '';
      }
    });
  });
})();
