document.addEventListener('DOMContentLoaded', (event) => {
  const eventBoxes = document.querySelectorAll('.event-box');
  const calendarContainer = document.getElementById('calendar-container');

  eventBoxes.forEach(box => {
    box.addEventListener('dragstart', dragStart);
  });

  calendarContainer.addEventListener('dragover', dragOver);
  calendarContainer.addEventListener('drop', drop);

  function dragStart(e) {
    e.dataTransfer.setData('text', e.target.id);
  }

  function dragOver(e) {
    e.preventDefault();
  }

  function drop(e) {
    e.preventDefault();
    const data = e.dataTransfer.getData('text');
    const eventBox = document.getElementById(data);
    e.target.appendChild(eventBox);
  }
});
