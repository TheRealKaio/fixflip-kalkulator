/* Mobile button haptics only: no visual or layout changes. */
(() => {
  'use strict';
  if (typeof navigator.vibrate !== 'function') return;

  document.addEventListener('pointerdown', (event) => {
    if (event.pointerType !== 'touch' || !event.isPrimary) return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    const button = target.closest('button, input[type="button"], input[type="submit"], input[type="reset"], [role="button"]');
    if (!button || button.matches(':disabled, [aria-disabled="true"], [inert]') || button.closest('[inert]')) return;
    navigator.vibrate(12);
  }, { passive: true });
})();
