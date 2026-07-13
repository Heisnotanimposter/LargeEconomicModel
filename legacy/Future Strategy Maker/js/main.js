document.addEventListener('DOMContentLoaded', (event) => {
  // Your existing initialization code
  fetchEconomicData();
  renderEvents();

  // Example to add an event
  addEvent({ id: 'event1', title: 'Sample Event', completed: false });

  // Prediction request
  const predictBtn = document.getElementById('predict-btn');
  predictBtn.addEventListener('click', async () => {
    const inputText = document.getElementById('input-text').value;
    const response = await fetch('http://localhost:8000/predict/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input_text: inputText }),
    });
    const data = await response.json();
    document.getElementById('prediction-result').textContent = data.prediction;
  });
});
