/* Browser-only form preview. No event is created, stored or transmitted. */
(() => {
  const eventForm = document.getElementById('event-form');
  const formMessage = document.getElementById('event-message');
  if (!eventForm) return;
  const dateInput = document.getElementById('event-date-input');
  if (dateInput) {
    const today = new Date();
    const year = today.getFullYear(); const month = String(today.getMonth() + 1).padStart(2,'0');
    const day = String(today.getDate()).padStart(2,'0');
    dateInput.min = `${year}-${month}-${day}`;
  }
  eventForm.addEventListener('submit', event => {
    event.preventDefault();
    if (!eventForm.reportValidity()) return;
    formMessage.hidden = false;
    formMessage.textContent = 'Frontend preview only — the form is not connected to the events database yet. No event was saved.';
  });
  eventForm.addEventListener('reset', () => {
    formMessage.hidden = true;
    formMessage.textContent = '';
  });
})();
