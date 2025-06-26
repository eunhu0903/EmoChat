document.getElementById("follower-btn").addEventListener("click", () => {
    document.getElementById("follower-modal").style.display = "block";
    loadFollowers();
});
  
document.getElementById("close-follower-modal").addEventListener("click", () => {
    document.getElementById("follower-modal").style.display = "none";
});
  
document.getElementById("following-btn").addEventListener("click", () => {
    document.getElementById("following-modal").style.display = "block";
    loadFollowing();
});
  
document.getElementById("close-following-modal").addEventListener("click", () => {
    document.getElementById("following-modal").style.display = "none";
});
  