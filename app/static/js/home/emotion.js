(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
  
    try {
      const checkRes = await fetch("http://127.0.0.1:8000/emotion/today", {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` }
      });
  
      if (!checkRes.ok) throw new Error("오늘 감정 선택 여부 확인 실패");
  
      const checkData = await checkRes.json();
  
      if (!checkData.selected) {
        document.getElementById("emotion-modal").style.display = "block";
      } else {
        document.getElementById("emotion-modal").style.display = "none";
      }
  
    } catch (err) {
      alert("사용자 정보를 불러오는 중 오류 발생");
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
  })();
  
  document.querySelectorAll(".emotion-button").forEach(btn => {
    btn.addEventListener("click", async () => {
      const mood = btn.dataset.emotion;
      const token = localStorage.getItem("access_token");
  
      try {
        const res = await fetch("http://127.0.0.1:8000/emotion", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ mood })
        });
  
        if (!res.ok) {
          const err = await res.json();
          alert(err.detail || "감정 저장 실패");
          return;
        }
  
        document.getElementById("emotion-modal").style.display = "none";
  
      } catch {
        alert("감정 저장 중 오류 발생");
      }
    });
  });
  