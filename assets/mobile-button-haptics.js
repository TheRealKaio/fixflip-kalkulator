/* Touch feedback for buttons: visual on iPhone, vibration where supported. */
(() => {
  'use strict';
  const selector = 'button, input[type="button"], input[type="submit"], input[type="reset"], [role="button"]';
  const style = document.createElement('style');
  style.textContent = `
    @media (hover: none) and (pointer: coarse) {
      button.nic-touch-feedback,
      input.nic-touch-feedback,
      [role="button"].nic-touch-feedback {
        filter: brightness(0.86) !important;
        transition: filter 80ms ease-out !important;
      }
    }
  `;
  (document.head || document.documentElement).appendChild(style);

  const timers = new WeakMap();
  document.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'touch' || !event.isPrimary) return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    const button = target.closest(selector);
    if (!button || button.matches(':disabled, [aria-disabled="true"], [inert]') || button.closest('[inert]')) return;
    clearTimeout(timers.get(button));
    button.classList.add('nic-touch-feedback');
    timers.set(button, setTimeout(() => button.classList.remove('nic-touch-feedback'), 180));
    if (typeof navigator.vibrate === 'function') navigator.vibrate(12);
  }, { passive: true });
})();
