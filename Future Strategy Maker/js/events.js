const events = [];

function addEvent(event) {
  events.push(event);
  renderEvents();
}

function markEventCompleted(eventId) {
  const event = events.find(ev => ev.id === eventId);
  if (event) {
    event.completed = true;
    renderEvents();
  }
}

function renderEvents() {
  const calendarContainer = document.getElementById('calendar-container');
  calendarContainer.innerHTML = '';

  events.forEach(event => {
    const eventBox = document.createElement('div');
    eventBox.id = event.id;
    eventBox.classList.add('event-box');
    if (event.completed) {
      eventBox.classList.add('completed');
    }
    eventBox.textContent = event.title;
    calendarContainer.appendChild(eventBox);
  });

  // Reinitialize drag and drop handlers
  const eventBoxes = document.querySelectorAll('.event-box');
  eventBoxes.forEach(box => {
    box.setAttribute('draggable', true);
    box.addEventListener('dragstart', dragStart);
  });
}
