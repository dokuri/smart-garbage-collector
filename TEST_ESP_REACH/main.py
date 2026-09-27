from __future__ import annotations

from datetime import datetime, timezone

from flask import Flask, request


app = Flask(__name__)


@app.get("/ping")
def ping():
    client_ip = request.remote_addr or "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"PING from {client_ip} | ua={user_agent} | {timestamp}", flush=True)
    return {
        "status": "ok",
        "client": client_ip,
        "server_time": timestamp,
    }


def main():
    print("Starting Flask ping server on 0.0.0.0:6900", flush=True)
    app.run(host="0.0.0.0", port=6900, debug=False)


if __name__ == "__main__":
    main()
