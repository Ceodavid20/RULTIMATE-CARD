import os
from flask import Flask, request, send_from_directory, render_template_string
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "secret123")

# Twitter/X API
BEARER = os.getenv("X_BEARER_TOKEN")
API_BASE = "https://api.twitter.com/2"


def get_user(username):
    """Get user info by username"""
    url = f"{API_BASE}/users/by/username/{username}?user.fields=id,name,username,profile_image_url"
    r = requests.get(url, headers={"Authorization": f"Bearer {BEARER}"})
    if r.status_code == 200 and "data" in r.json():
        return r.json()["data"]
    print("Error fetching user:", r.text)
    return None


def user_has_said_rialo(user_id):
    """Check if user has said 'rialo' in last 100 tweets"""
    url = f"{API_BASE}/users/{user_id}/tweets"
    params = {
        "max_results": 100,
        "tweet.fields": "text"  # make sure we get full text
    }
    r = requests.get(url, headers={"Authorization": f"Bearer {BEARER}"}, params=params)

    if r.status_code != 200:
        print("Error fetching tweets:", r.text)
        return False

    tweets = r.json().get("data", [])
    found = False
    for t in tweets:
        text = t.get("text", "").lower()
        print("Tweet:", text)  # Debugging output
        if "rialo" in text:
            found = True
            break

    return found


@app.route("/")
def index():
    return send_from_directory("templates", "index.html")


@app.route("/check", methods=["POST"])
def check():
    username = request.form.get("username", "").strip().lower()
    if not username:
        return "⚠️ Please enter a username."

    user = get_user(username)
    if not user:
        return f"❌ User @{username} not found."

    if user_has_said_rialo(user["id"]):
        return render_template_string("""
        <!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>RIALO — Eligibility Card</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
    crossorigin="anonymous" referrerpolicy="no-referrer"></script>
 <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
  <style>
    :root {
      --cream: #e8e3d5;
      --black: #0f0f0f;
      --gold: #c8c48d;
      --beige: #d6d2c0;
      --accent: #bfc07e;
    }

    body {
      margin: 0;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: url("{{ url_for('static', filename='rialo.png') }}") no-repeat center/cover;
      color: white;
      font-family: 'Trebuchet MS', sans-serif;
    }

    .overlay {
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(0,0,0,0.7);
      z-index: -1;
    }

    .card {
      background: rgba(20,20,20,0.85);
      padding: 40px;
      border-radius: 20px;
      box-shadow: 0 0 40px rgba(200,196,141,0.4),
                  0 0 60px rgba(191,192,126,0.25);
      text-align: center;
      backdrop-filter: blur(6px);
    }

    .avatar {
      width: 140px;
      height: 140px;
      border-radius: 50%;
      border: 4px solid var(--gold);
      box-shadow: 0 0 20px rgba(191,192,126,0.8);
      margin-bottom: 20px;
    }

    .display-name {
      font-size: 42px;
      font-weight: bold;
      color: var(--accent);
      text-shadow:
        0 0 6px rgba(191,192,126,0.9),
        0 0 16px rgba(200,196,141,0.8),
        0 0 26px rgba(255,255,200,0.7),
        0 4px 12px rgba(0,0,0,0.8);
    }

    .handle {
      font-size: 20px;
      color: var(--beige);
      text-shadow:
        0 0 4px rgba(200,196,141,0.7),
        0 0 10px rgba(191,192,126,0.7);
      margin-bottom: 20px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 20px;
      border-radius: 14px;
      margin-top: 20px;
      font-size: 18px;
      font-weight: bold;
      background: linear-gradient(90deg, rgba(200,196,141,0.15), rgba(191,192,126,0.05));
      box-shadow: 0 0 20px rgba(200,196,141,0.6);
      color: var(--cream);
    }

    .badge .dot {
      width: 18px; height: 18px;
      border-radius: 50%;
      background: linear-gradient(90deg,var(--gold),var(--accent));
      box-shadow: 0 0 12px rgba(200,196,141,0.9);
    }

    .credit {
      margin-top: 30px;
      font-family: 'Brush Script MT', cursive;
      font-size: 18px;
      color: var(--beige);
      text-shadow: 0 0 10px rgba(200,196,141,0.6);
    }

    .btn {
      margin: 12px 6px;
      padding: 12px 20px;
      border: none;
      border-radius: 10px;
      font-weight: bold;
      font-size: 16px;
      cursor: pointer;
      background: linear-gradient(90deg,#c8c48d,#bfc07e);
      color: #111;
      box-shadow: 0 0 15px rgba(200,196,141,0.8);
      transition: transform 0.2s, box-shadow 0.3s;
    }

    .btn:hover {
      transform: scale(1.05);
      box-shadow: 0 0 25px rgba(200,196,141,1);
    }
  </style>
</head>
<body>
  <div class="overlay"></div>
  <div class="card" id="card-root">
    <img class="avatar" src="{{ user['profile_image_url'] }}" alt="avatar">
    <h1 class="display-name">{{ user['name'] or user['username'] }}</h1>
    <div class="handle">@{{ user['username'] }}</div>
    <div class="badge" id="badge-text">RIALO ROCKER<div class="dot"></div></div>
    <div class="credit">Rialo • by Subzero Labs</div>
    <div>
      <button class="btn" id="shareBtn">Share</button>
 
    </div>
  </div>
  <script>
document.getElementById("shareBtn").addEventListener("click", async function() {
  const card = document.getElementById("card-root");

  // Capture the card as an image
  const canvas = await html2canvas(card, {
    useCORS: true,
    backgroundColor: null
  });

  // Convert the captured canvas to a data URL
  const dataUrl = canvas.toDataURL("image/png");

  // Create a link element for download
  const link = document.createElement("a");
  link.href = dataUrl;
  link.download = "RialoCard.png";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Try opening native share dialog if supported
  if (navigator.share && navigator.canShare) {
    try {
      const response = await fetch(dataUrl);
      const blob = await response.blob();
      const file = new File([blob], "RialoCard.png", { type: "image/png" });

      if (navigator.canShare({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: "My Rialo Card",
          text: "Check out my new Rialo Card! Made on rialocards.com ✨"
        });
      }
    } catch (error) {
      console.error("Error sharing:", error);
    }
  }
});
</script>
</body>
</html>
        """, user=user)
    else:
        return render_template_string("""
        <!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>RIALO — Eligibility Card</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
    crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
.
  <style>
    :root {
      --cream: #e8e3d5;
      --black: #0f0f0f;
      --gold: #c8c48d;
      --beige: #d6d2c0;
      --accent: #bfc07e;
    }

    body {
      margin: 0;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: url("{{ url_for('static', filename='rialo.png') }}") no-repeat center/cover;
      color: white;
      font-family: 'Trebuchet MS', sans-serif;
    }

    .overlay {
      position: absolute;
      top: 0; left: 0;
      width: 100%; height: 100%;
      background: rgba(0,0,0,0.7);
      z-index: -1;
    }

    .card {
      background: rgba(20,20,20,0.85);
      padding: 40px;
      border-radius: 20px;
      box-shadow: 0 0 40px rgba(200,196,141,0.4),
                  0 0 60px rgba(191,192,126,0.25);
      text-align: center;
      backdrop-filter: blur(6px);
    }

    .avatar {
      width: 140px;
      height: 140px;
      border-radius: 50%;
      border: 4px solid var(--gold);
      box-shadow: 0 0 20px rgba(191,192,126,0.8);
      margin-bottom: 20px;
    }

    .display-name {
      font-size: 42px;
      font-weight: bold;
      color: var(--accent);
      text-shadow:
        0 0 6px rgba(191,192,126,0.9),
        0 0 16px rgba(200,196,141,0.8),
        0 0 26px rgba(255,255,200,0.7),
        0 4px 12px rgba(0,0,0,0.8);
    }

    .handle {
      font-size: 20px;
      color: var(--beige);
      text-shadow:
        0 0 4px rgba(200,196,141,0.7),
        0 0 10px rgba(191,192,126,0.7);
      margin-bottom: 20px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 20px;
      border-radius: 14px;
      margin-top: 20px;
      font-size: 18px;
      font-weight: bold;
      background: linear-gradient(90deg, rgba(200,196,141,0.15), rgba(191,192,126,0.05));
      box-shadow: 0 0 20px rgba(200,196,141,0.6);
      color: var(--cream);
    }

    .badge .dot {
      width: 18px; height: 18px;
      border-radius: 50%;
      background: linear-gradient(90deg,var(--gold),var(--accent));
      box-shadow: 0 0 12px rgba(200,196,141,0.9);
    }

    .credit {
      margin-top: 30px;
      font-family: 'Brush Script MT', cursive;
      font-size: 18px;
      color: var(--beige);
      text-shadow: 0 0 10px rgba(200,196,141,0.6);
    }

    .btn {
      margin: 12px 6px;
      padding: 12px 20px;
      border: none;
      border-radius: 10px;
      font-weight: bold;
      font-size: 16px;
      cursor: pointer;
      background: linear-gradient(90deg,#c8c48d,#bfc07e);
      color: #111;
      box-shadow: 0 0 15px rgba(200,196,141,0.8);
      transition: transform 0.2s, box-shadow 0.3s;
    }

    .btn:hover {
      transform: scale(1.05);
      box-shadow: 0 0 25px rgba(200,196,141,1);
    }
  </style>
</head>
<body>
  <div class="overlay"></div>
  <div class="card" id="card-root">
    <img class="avatar" src="{{ user['profile_image_url'] }}" alt="avatar">
    <h1 class="display-name">{{ user['name'] or user['username'] }}</h1>
    <div class="handle">@{{ user['username'] }}</div>
    <div class="badge" id="badge-text">RIALO ROCKER<div class="dot"></div></div>
    <div class="credit">Rialo • by Subzero Labs</div>
    <div>
      <button class="btn" id="shareBtn">Share</button>
 
    </div>
  </div>
  <script>
document.getElementById("shareBtn").addEventListener("click", async function() {
  const card = document.getElementById("card-root");

  // Capture the card as an image
  const canvas = await html2canvas(card, {
    useCORS: true,
    backgroundColor: null
  });

  // Convert the captured canvas to a data URL
  const dataUrl = canvas.toDataURL("image/png");

  // Create a link element for download
  const link = document.createElement("a");
  link.href = dataUrl;
  link.download = "RialoCard.png";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Try opening native share dialog if supported
  if (navigator.share && navigator.canShare) {
    try {
      const response = await fetch(dataUrl);
      const blob = await response.blob();
      const file = new File([blob], "RialoCard.png", { type: "image/png" });

      if (navigator.canShare({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: "My Rialo Card",
          text: "Check out my new Rialo Card! Made on rialocards.com ✨"
        });
      }
    } catch (error) {
      console.error("Error sharing:", error);
    }
  }
});
</script>
</body>
</html>

        """, user=user)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
