document.getElementById("delete-account-btn").addEventListener("click", async () => {
    const confirmDelete = confirm("정말 계정을 삭제하시겠습니까?");
    if (!confirmDelete) return;
  
    const password = prompt("비밀번호를 입력하세요:");
    const token = localStorage.getItem("access_token");
  
    try {
      const res = await fetch("http://127.0.0.1:8000/delete-user", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ password })
      });
  
      const data = await res.json();
      if (!res.ok) return alert(data.detail || "계정 삭제 실패");
  
      alert("계정이 삭제되었습니다.");
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    } catch {
      alert("계정 삭제 중 오류 발생");
    }
});
  