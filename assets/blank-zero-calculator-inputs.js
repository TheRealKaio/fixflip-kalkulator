(() => {
  const root = document.querySelector("main");
  if (!root) return;

  const selector = 'input:not([type="range"]):not([type="radio"]):not([type="checkbox"]):not([type="hidden"])';
  const isNumeric = (input) => input.matches('input[type="number"],input[inputmode="decimal"],input[inputmode="numeric"]');
  const isZero = (value) => /^[+-]?0+(?:[.,]0+)?$/.test(String(value ?? "").trim());

  const clearZeroFields = (except) => {
    root.querySelectorAll(selector).forEach((input) => {
      if (input !== except && isNumeric(input) && isZero(input.value)) input.value = "";
    });
  };
  const scheduleCleanup = (except) => window.setTimeout(() => clearZeroFields(except), 0);

  // Wait until the calculator's own event handlers finish before clearing values.
  root.addEventListener("input", (event) => scheduleCleanup(event.target), true);
  root.addEventListener("change", () => scheduleCleanup(null), true);
  root.addEventListener("blur", (event) => {
    if (isNumeric(event.target)) scheduleCleanup(null);
  }, true);
  root.addEventListener("click", () => scheduleCleanup(null));

  const initialize = () => {
    scheduleCleanup(null);
    window.setTimeout(() => clearZeroFields(null), 250);
    window.setTimeout(() => clearZeroFields(null), 900);
  };
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})();
