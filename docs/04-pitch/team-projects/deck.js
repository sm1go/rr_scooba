(() => {
  const slides = [...document.querySelectorAll('.slide')];
  document.body.insertAdjacentHTML('beforeend',
    '<div class="nav"><button data-d="-1">&larr;</button><button data-d="1">&rarr;</button></div><div class="footer" id="counter"></div>');
  let i = 0;
  const show = n => {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, k) => s.classList.toggle('active', k === i));
    document.getElementById('counter').textContent = (i + 1) + ' / ' + slides.length;
  };
  document.addEventListener('keydown', e => {
    if (['ArrowRight', 'PageDown', ' '].includes(e.key)) show(i + 1);
    if (['ArrowLeft', 'PageUp'].includes(e.key)) show(i - 1);
  });
  document.addEventListener('click', e => {
    const b = e.target.closest('.nav button');
    if (b) return show(i + Number(b.dataset.d));
    if (!e.target.closest('iframe, a')) show(i + 1);
  });
  show(0);
})();
