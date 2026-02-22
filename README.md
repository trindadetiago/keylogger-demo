# Keylogger Demo - Seguranca Computacional UFPB

**DEMO EDUCACIONAL** - Apenas para apresentacao academica.

## O que faz

Demonstra o percurso completo de um ataque de keylogging usando um trojan:

1. **Trojan (Flappy Bird)** - Jogo que parece normal, mas roda um keylogger oculto em background
2. **Servidor C2** - Recebe as teclas e exibe num dashboard web em tempo real

## Requisitos

- Python 3.10+
- pip
- macOS: permissao de Acessibilidade para o Terminal

## Setup rapido

```bash
# 1. Criar e ativar virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar o servidor C2 (Terminal 1)
python server/app.py

# 4. Abrir o dashboard no navegador
# http://localhost:8080

# 5. Abrir o Flappy Bird trojan (Terminal 2 - com venv ativado)
python trojan/flappybird.py

# 6. A vitima joga Flappy Bird - tudo que digitar aparece no dashboard
```

## Gerar .app e .dmg

```bash
./trojan/build_app.sh
# Gera: dist/Flappy Bird.app e dist/FlappyBird-Install.dmg
```

## macOS - Permissao necessaria

No macOS, o Terminal precisa de permissao de Acessibilidade:
1. System Settings > Privacy & Security > Accessibility
2. Adicione o Terminal (ou iTerm2) na lista

## Estrutura

```
keylogger-demo/
  server/
    app.py              # Servidor C2 (Flask + WebSocket)
    templates/
      dashboard.html    # Dashboard web em tempo real
  trojan/
    flappybird.py       # Flappy Bird trojan com keylogger oculto
    generate_icon.py    # Gera icone do app
    build_app.sh        # Gera .app + .dmg
  requirements.txt
  venv/                 # Virtual environment
```
