document.getElementById("change-password-btn").addEventListener("click", async () => {
    const current = document.getElementById("current-password").value;
    const newPass = document.getElementById("new-password").value;
    const confirm = document.getElementById("confirm-password").value;
    const token = localStorage.getItem("access_token");

    if (!current || !newPass || !confirm) return alert("모든 비밀번호를 입력해주세요.");

    try {
        const res = await fetch("http://127.0.0.1:8000/change-password", {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({
                current_password: current,
                new_password: newPass,
                confirm_password: confirm
            })
        });

        const data = await res.json();
        if (!res.ok) return alert(data.detail || "비밀번호 변경 실패");

        alert(data.message);
        location.reload();
    } catch {
        alert("비밀번호 변경 중 오류 발생");
    }
});