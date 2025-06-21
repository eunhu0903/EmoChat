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
      document.getElementById("user-info").innerText = userData.message;
  
    } catch (err) {
      alert("사용자 정보를 불러오는 중 오류 발생");
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
  })();
  