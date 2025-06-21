document.getElementById("logout-btn").addEventListener("click", function () {
    localStorage.removeItem("access_token");
    alert("로그아웃 되었습니다.");
    window.location.href = "/login";
  });
  