document.getElementById("search-btn").addEventListener("click", async () => {
    const query = document.getElementById("search-input").value.trim();
    const resultsUI = document.getElementById("search-results");
    resultsUI.innerHTML = "";
  
    if (!query) return;
  
    try {
      const res = await fetch(`http://127.0.0.1:8000/users/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("검색 실패");
  
      const users = await res.json();
      if (users.length === 0) {
        resultsUI.innerHTML = "<li>검색 결과가 없습니다.</li>";
        return;
      }
  
      users.forEach(user => {
        const li = document.createElement("li");
        li.textContent = user.username;
        resultsUI.appendChild(li);
      });
    } catch {
      resultsUI.innerHTML = "<li>검색 중 오류가 발생했습니다.</li>";
    }
  });
  