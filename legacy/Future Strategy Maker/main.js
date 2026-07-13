document.addEventListener('DOMContentLoaded', (event) => {
  // Bind event listeners for prediction buttons
  document.getElementById('predict-btn1').addEventListener('click', async () => {
    const inputText = document.getElementById('input1').value;
    const response = await fetchPrediction(inputText);
    document.getElementById('prediction-result1').textContent = response;
  });

  document.getElementById('predict-btn2').addEventListener('click', async () => {
    const inputText = document.getElementById('input2').value;
    const response = await fetchPrediction(inputText);
    document.getElementById('prediction-result2').textContent = response;
  });

  document.getElementById('predict-btn3').addEventListener('click', async () => {
    const inputText = document.getElementById('input3').value;
    const response = await fetchPrediction(inputText);
    document.getElementById('prediction-result3').textContent = response;
  });

  document.getElementById('predict-btn4').addEventListener('click', async () => {
    const inputText = document.getElementById('input4').value;
    const response = await fetchPrediction(inputText);
    document.getElementById('prediction-result4').textContent = response;
  });

  document.getElementById('predict-btn-calendar').addEventListener('click', async () => {
    const inputText = document.getElementById('input-calendar').value;
    const response = await fetchPrediction(inputText);
    document.getElementById('prediction-result-calendar').textContent = response;
  });

  document.getElementById('predict-btn-timetable').addEventListener('click', async () => {
    const inputText = document.getElementById('input-timetable').value;
    const response = await fetchPrediction(inputText);
    document.getElementById('prediction-result-timetable').textContent = response;
  });

  document.getElementById('predict-btn-decision').addEventListener('click', async () => {
    const inputText = document.getElementById('input-decision').value;
    const response = await fetchPrediction(inputText);
    document.getElementById('prediction-result-decision').textContent = response;
  });

  async function fetchPrediction(inputText) {
    const response = await fetch('http://localhost:8000/predict/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ input_text: inputText }),
    });
    const data = await response.json();
    return data.prediction;
  }
});
