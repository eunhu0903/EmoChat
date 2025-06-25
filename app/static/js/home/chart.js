(async () => {
  const token = localStorage.getItem("access_token");
  if (!token) {
    window.location.href = "/login";
    return;
  }

  try {
    const userRes = await fetch("http://127.0.0.1:8000/", {
      method: "GET",
      headers: { Authorization: `Bearer ${token}` }
    });
    if (!userRes.ok) throw new Error("사용자 정보를 불러오는 중 오류");

    const userData = await userRes.json();

    const emotions = ["기쁨", "슬픔", "분노"];
    const topEmotions = userData.top_emotions_today || [];

    const emotionCounts = emotions.map(emotion => {
      const found = topEmotions.find(e => e.emotion === emotion);
      return found ? found.count : 0;
    });

    const ctx = document.getElementById("emotionChart").getContext("2d");
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: emotions,
        datasets: [{
          label: '감정 수',
          data: emotionCounts,
          backgroundColor: ['#f39c12', '#3498db', '#e74c3c'],
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        responsive: false,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: context => `${context.label}: ${context.raw}개`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1, font: { size: 12 } },
            grid: { color: "#eee" }
          },
          x: {
            barPercentage: 0.5,
            categoryPercentage: 0.6,
            ticks: { font: { size: 14 } },
            grid: { display: false }
          }
        }
      }
    });

  } catch (err) {
    alert("사용자 정보를 불러오는 중 오류 발생");
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  }
})();
