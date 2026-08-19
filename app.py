from flask import Flask, request, send_file, jsonify, render_template, make_response
from datetime import datetime, timedelta
import requests
import io
import base64
import os

app = Flask(__name__)

tracking_data = {}
cache_geo = {}

TRANSPARENT_PIXEL = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
)

def get_city_from_ip(ip):
    if ip in ("127.0.0.1", "localhost", None, "") or ip.startswith("192.168.") or ip.startswith("10."):
        return "Local/Réseau privé"
    if ip in cache_geo:
        return cache_geo[ip]
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=city,status", timeout=3)
        data = response.json()
        if data.get("status") == "success":
            city = data.get("city", "Inconnue")
            cache_geo[ip] = city
            return city
    except Exception as e:
        print(f"[GEO] Erreur pour IP {ip}: {e}")
    return "Inconnue"

def get_or_create_session(token, now):
    user_data = tracking_data[token]
    if not user_data["opens"]:
        session_id = f"sess_1_{token[:4]}"
        user_data["sessions"].append({
            "session_id": session_id,
            "start": now.strftime("%Y-%m-%d %H:%M:%S"),
            "end": now.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_sec": 0
        })
        return session_id
    last_open = user_data["opens"][-1]
    last_time = datetime.strptime(last_open["time"], "%Y-%m-%d %H:%M:%S")
    if (now - last_time) < timedelta(minutes=2):
        return last_open["session_id"]
    session_id = f"sess_{len(user_data['sessions']) + 1}_{token[:4]}"
    user_data["sessions"].append({
        "session_id": session_id,
        "start": now.strftime("%Y-%m-%d %H:%M:%S"),
        "end": now.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_sec": 0
    })
    return session_id

@app.route("/pixel")
def track_pixel():
    token = request.args.get("id", "unknown")
    user_agent = request.headers.get("User-Agent", "Inconnu")
    # Récupérer l'IP réelle derrière le proxy Render
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip and "," in ip:
        ip = ip.split(",")[0].strip()
    city = get_city_from_ip(ip)
    now = datetime.now()
    if token not in tracking_data:
        tracking_data[token] = {
            "email": f"user_{token}@demo.fr",
            "first_seen": now,
            "opens": [],
            "sessions": [],
            "clicks": []
        }
    user_data = tracking_data[token]
    session_id = get_or_create_session(token, now)
    user_data["opens"].append({
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "ip": ip,
        "city": city,
        "user_agent": user_agent[:60],
        "session_id": session_id
    })
    for sess in user_data["sessions"]:
        if sess["session_id"] == session_id:
            sess["end"] = now.strftime("%Y-%m-%d %H:%M:%S")
            start_dt = datetime.strptime(sess["start"], "%Y-%m-%d %H:%M:%S")
            sess["duration_sec"] = int((now - start_dt).total_seconds())
            break
    print(f"[TRACK] Token={token[:12]} | IP={ip} | City={city} | Session={session_id}")
    
    # CORRECTION : make_response + send_file sans headers
    response = make_response(send_file(
        io.BytesIO(TRANSPARENT_PIXEL),
        mimetype="image/png"
    ))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/click")
def track_click():
    token = request.args.get("id", "unknown")
    url = request.args.get("url", "https://google.com")
    now = datetime.now()
    if token not in tracking_data:
        tracking_data[token] = {"email": f"user_{token}@demo.fr", "first_seen": now, "opens": [], "sessions": [], "clicks": []}
    tracking_data[token].setdefault("clicks", []).append({"time": now.strftime("%Y-%m-%d %H:%M:%S"), "url": url})
    return f"<script>window.location.href='{url}';</script>"

@app.route("/dashboard")
def dashboard():
    total_users = len(tracking_data)
    total_opens = sum(len(d["opens"]) for d in tracking_data.values())
    total_reopens = sum(max(0, len(d["opens"]) - len(d["sessions"])) for d in tracking_data.values())
    all_durations = []
    for d in tracking_data.values():
        for s in d["sessions"]:
            all_durations.append(s["duration_sec"])
    avg_duration = round(sum(all_durations) / len(all_durations), 1) if all_durations else 0
    users_list = []
    for token, data in tracking_data.items():
        users_list.append({
            "token": token,
            "opens": data["opens"],
            "sessions": data["sessions"],
            "clicks": data.get("clicks", []),
            "first_seen": data["first_seen"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(data["first_seen"], datetime) else str(data["first_seen"])
        })
    return render_template("dashboard.html",
        total_users=total_users,
        total_opens=total_opens,
        total_reopens=total_reopens,
        avg_duration=avg_duration,
        users=users_list
    )

@app.route("/api/data")
def api_data():
    export_data = {}
    for token, data in tracking_data.items():
        export_data[token] = {
            "email": data["email"],
            "first_seen": data["first_seen"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(data["first_seen"], datetime) else str(data["first_seen"]),
            "opens": data["opens"],
            "sessions": data["sessions"],
            "clicks": data.get("clicks", [])
        }
    return jsonify(export_data)

@app.route("/clear")
def clear_data():
    tracking_data.clear()
    cache_geo.clear()
    return """<script>window.location.href='/dashboard';</script>"""

@app.route("/")
def home():
    return """
    <html><body style="font-family:Arial;padding:40px;text-align:center;">
    <h1>📧 Email Tracker - Projet Éducatif</h1>
    <p>Le serveur est en ligne !</p>
    <div style="margin-top:30px;">
    <a href="/dashboard" style="display:inline-block;padding:15px 30px;background:#3b82f6;color:white;text-decoration:none;border-radius:8px;margin:10px;">📊 Dashboard</a>
    <a href="/api/data" style="display:inline-block;padding:15px 30px;background:#22c55e;color:white;text-decoration:none;border-radius:8px;margin:10px;">📡 API JSON</a>
    </div>
    </body></html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
