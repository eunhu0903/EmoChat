const token = localStorage.getItem("access_token");

async function loadFollowers() {
    const list = document.getElementById("follower-list")
    list.innerHTML = "";

    try {
        const res = await fetch("http://127.0.0.1:8000/followers", {
            method: "GET",
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!res.ok) throw new Error("팔로워 목록을 불러올 수 없습니다.");
        const data = await res.json();

        if (data.followers.length === 0) {
            list.innerHTML = "<li>팔로워가 없습니다.</li>";
        } else {
            data.followers.forEach(username => {
                const li = document.createElement("li");
                li.textContent = username;
                list.appendChild(li);
            });
        }
    } catch (err) {
        alert('팔로워 목록을 불러오는 중 오류 발생');
    }
}

async function loadFollowing() {
    const list = document.getElementById("following-list");
    list.innerHTML = "";

    try {
        const res = await fetch("http://127.0.0.1:8000/following", {
            method: "GET",
            headers: { Authorization: `Bearer ${token} `}
        });

        if (!res.ok) throw new Error("팔로잉 목록을 불러올 수 없습니다.");
        const data = await res.json()

        if (data.following.length === 0) {
            list.innerHTML = "<li>팔로잉한 사람이 없습니다.</li>";
        } else {
            data.following.forEach(username => {
                const li = document.createElement("li");
                li.textContent = username;
                list.appendChild(li);
            });
        }
    } catch (err) {
        alert("팔로잉 목록을 불러오는 중 오류 발생");
    }
}