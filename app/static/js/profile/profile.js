(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
  
    try {
      const response = await fetch("http://127.0.0.1:8000/profile", {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` }
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        alert(errorData.detail || "프로필 정보를 불러오지 못했습니다.");
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        return;
      }
  
      const data = await response.json();
  
      document.getElementById("user-info").innerText = `유저네임: ${data.username}`;
  
      const calendarContainer = document.getElementById("emotion-calendar");
      calendarContainer.innerHTML = ""; // 초기화
  
      const today = new Date();
      const startDate = new Date();
      startDate.setDate(today.getDate() - 29);
  
      // 로컬 날짜 문자열 변환 함수 (YYYY-MM-DD)
      function toLocalDateString(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
      }
  
      const emotionHistory = data.emotion_history || [];
      const emotionMap = {};
      emotionHistory.forEach(e => {
        emotionMap[e.date] = e.mood;  // e.date는 이미 YYYY-MM-DD 형식임
      });
  
      for (let d = new Date(startDate); d <= today; d.setDate(d.getDate() + 1)) {
        const dateStr = toLocalDateString(d); // 로컬 날짜 문자열 사용
        const mood = emotionMap[dateStr] || null;
  
        const dayDiv = document.createElement("div");
        dayDiv.classList.add("day-cell");
  
        if (mood) {
          dayDiv.classList.add(`emotion-${mood}`);
          dayDiv.title = mood;
        } else {
          dayDiv.classList.add("no-emotion");
          dayDiv.title = "감정 기록 없음";
        }
  
        dayDiv.textContent = `${d.getMonth() + 1}/${d.getDate()}`;
  
        calendarContainer.appendChild(dayDiv);
      }
    } catch (error) {
      alert("프로필 로딩 중 오류가 발생했습니다.");
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
  })();
  