document.getElementById("connectBtn").addEventListener("click", () => {
  // Starts OAuth flow
  window.location = "/login";
});

// After redirect back, fetch profile & eligibility
async function loadResult() {
  try {
    const res = await fetch("/profile");
    if (!res.ok) return;
    const j = await res.json();
    document.getElementById("targetName").innerText = "{{TARGET_USERNAME}}"; // replace visually if needed

    if (j.eligible) {
      document.getElementById("profilePic").src = j.profile_image_url;
      document.getElementById("profileName").textContent = j.name;
      document.getElementById("card").classList.remove("hidden");
    } else {
      document.getElementById("notEligible").classList.remove("hidden");
    }
    document.getElementById("connectBtn").style.display = "none";
  } catch (e) {
    console.error(e);
  }
}

// run on page load (if user returned from OAuth)
window.addEventListener("load", loadResult);
