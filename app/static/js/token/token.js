(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      window.location.href = "/login";
      return;
    }
  
    try {
      const response = await fetch("http://127.0.0.1:8000/", {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` }
      });
  
      if (!response.ok) {
        const err = await response.json();
        alert(err.detail || "사용자 정보를 불러오는 중 오류");
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        return;
      }
      const data = await response.json();
    } catch {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
  })();
  