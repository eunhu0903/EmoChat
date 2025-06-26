const token = localStorage.getItem("access_token");

document.getElementById("search-btn").addEventListener("click", async () => {
  const query = document.getElementById("search-input").value.trim();
  const resultsUI = document.getElementById("search-results");
  resultsUI.innerHTML = "";

  if (!query) return;

  try {
    const res = await fetch(`http://127.0.0.1:8000/users/search?q=${encodeURIComponent(query)}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    if (!res.ok) throw new Error("검색 실패");

    const users = await res.json();

    if (users.length === 0) {
      resultsUI.innerHTML = "<li>검색 결과가 없습니다.</li>";
      return;
    }

    users.forEach(user => {
      const li = document.createElement("li");

      const usernameSpan = document.createElement("span");
      usernameSpan.textContent = user.username;
      li.appendChild(usernameSpan);

      const followBtn = document.createElement("button");
      followBtn.textContent = user.is_following ? "팔로잉" : "팔로우";
      followBtn.style.marginLeft = "10px";

      followBtn.addEventListener("click", async () => {
        try {
          if (followBtn.textContent === "팔로우") {
            const followRes = await fetch(`http://127.0.0.1:8000/follow/${user.id}`, {
              method: "POST",
              headers: {
                Authorization: `Bearer ${token}`
              }
            });

            if (!followRes.ok) {
              const err = await followRes.json();
              alert(err.detail || "팔로우 실패");
              return;
            }

            followBtn.textContent = "팔로잉";
          } else {
            const unfollowRes = await fetch(`http://127.0.0.1:8000/unfollow/${user.id}`, {
              method: "DELETE",
              headers: {
                Authorization: `Bearer ${token}`
              }
            });

            if (!unfollowRes.ok) {
              const err = await unfollowRes.json();
              alert(err.detail || "언팔로우 실패");
              return;
            }

            followBtn.textContent = "팔로우";
          }
        } catch (err) {
          alert("요청 중 오류 발생");
        }
      });

      li.appendChild(followBtn);
      resultsUI.appendChild(li);
    });
  } catch (err) {
    resultsUI.innerHTML = "<li>검색 중 오류가 발생했습니다.</li>";
  }
});
