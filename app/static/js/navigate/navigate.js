const profileBtn = document.getElementById("profile-btn");
if (profileBtn) {
  profileBtn.addEventListener("click", () => {
    window.location.href = "/mypage";
  });
}

const homeBtn = document.getElementById("home-btn");
if (homeBtn) {
  homeBtn.addEventListener("click", () => {
    window.location.href = "/home";
  });
}
