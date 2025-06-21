document.getElementById("login-form").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
  
    try {
      const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
  
      if (response.ok) {
        const result = await response.json();
        localStorage.setItem("access_token", result.access_token);
        window.location.href = "/home";
      } else {
        const err = await response.json();
        alert(err.detail || "로그인 실패");
      }
    } catch (error) {
      alert("로그인 중 오류가 발생했습니다.");
    }
  });
  