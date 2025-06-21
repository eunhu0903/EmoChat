document.getElementById("signup-form").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
  
    try {
      const response = await fetch("http://127.0.0.1:8000/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
  
      if (response.ok) {
        alert("회원가입이 완료되었습니다!");
        window.location.href = "/login";
      } else {
        const err = await response.json();
        alert(err.detail || "회원가입 실패");
      }
    } catch (error) {
      alert("회원가입 중 오류가 발생했습니다.");
    }
  });
  