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

const loginBtn = document.getElementById("login-btn");
if (loginBtn) {
  loginBtn.addEventListener("click", () => {
    window.location.href = "/login";
  });
}

const signupBtn = document.getElementById("signup-btn");
if (signupBtn) {
  signupBtn.addEventListener("click", () => {
    window.location.href = "/signup";
  });
}
