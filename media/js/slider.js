document.addEventListener('DOMContentLoaded', function() {
  const sliderContainerConocenos = document.querySelector('.conocenos-slider');
  const slidesConocenos = document.querySelectorAll('.conocenos-slide');
  const prevButtonConocenos = document.querySelector('.conocenos-nav.conocenos-prev');
  const nextButtonConocenos = document.querySelector('.conocenos-nav.conocenos-next');
  const dotsConocenos = document.querySelectorAll('.conocenos-dots .conocenos-dot');
  let currentIndexConocenos = 0;

  function updateSliderConocenos() {
    if (slidesConocenos && dotsConocenos) {
      slidesConocenos.forEach((slide, index) => slide.classList.remove('active'));
      dotsConocenos.forEach((dot, index) => dot.classList.remove('active'));
      if (slidesConocenos[currentIndexConocenos]) {
        slidesConocenos[currentIndexConocenos].classList.add('active');
      }
      if (dotsConocenos[currentIndexConocenos]) {
        dotsConocenos[currentIndexConocenos].classList.add('active');
      }
    } else {
      console.error('Error (Conócenos): No se encontraron las slides o los dots.');
    }
  }

  function goToPrevConocenos() {
    currentIndexConocenos = (currentIndexConocenos - 1 + (slidesConocenos ? slidesConocenos.length : 0)) % (slidesConocenos ? slidesConocenos.length : 1);
    updateSliderConocenos();
  }

  function goToNextConocenos() {
    currentIndexConocenos = (currentIndexConocenos + 1) % (slidesConocenos ? slidesConocenos.length : 1);
    updateSliderConocenos();
  }

  function goToSlideConocenos(index) {
    currentIndexConocenos = index;
    updateSliderConocenos();
  }

  if (prevButtonConocenos) {
    prevButtonConocenos.addEventListener('click', goToPrevConocenos);
  } else {
    console.error('Error (Conócenos): No se encontró el botón "prev".');
  }

  if (nextButtonConocenos) {
    nextButtonConocenos.addEventListener('click', goToNextConocenos);
  } else {
    console.error('Error (Conócenos): No se encontró el botón "next".');
  }

  if (dotsConocenos && dotsConocenos.length > 0) {
    dotsConocenos.forEach((dot, index) => {
      dot.addEventListener('click', () => goToSlideConocenos(index));
    });
  } else {
    console.error('Error (Conócenos): No se encontraron los dots de navegación.');
  }

  updateSliderConocenos(); // Inicializar el slider
});