from flask import Flask, render_template, request
import datetime
import os

app = Flask(__name__)

LOG_FILE = "logs/ai_log.txt"

@app.route("/")
def index():
    status = "✅ Systemet är redo"
    log_text = ""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            log_text = f.read()[-5000:]
    return render_template("index.html", status=status, log=log_text)

@app.route("/start", methods=["POST"])
def start():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 🟢 Manuell körning startad via webb")
    # Här skulle vi anropa automatiseringsflödet
    return "AI-flöde påbörjat!"

if __name__ == "__main__":
    app.run(debug=True)
