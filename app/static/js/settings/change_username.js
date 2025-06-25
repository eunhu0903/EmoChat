document.getElementById("change-username-btn").addEventListener("click", async () => {
    const newUsername = document.getElementById("username-input").value.trim();
    const token = localStorage.getItem("access_token");

    if (!newUsername) return alert("새 유저네임을 입력해주세요.");

    try {
        const res = await fetch("http://127.0.0.1:8000/change-username", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ new_username: newUsername })
        });

        const data = await res.json();
        if (!res.ok) return alert(data.detail || "닉네임 변경 실패");

        alert(data.message);
        location.reload();
    } catch {
        alert("닉네임 변경 중 오류 발생");
    }
});