# SaaS de Contratos ⚡️
MVP de uma plataforma para gerar contratos de prestação de serviço, com autenticação, CRUD de contratos e exportação em PDF já com cláusulas padrão e área de assinatura. Construído para rodar em Vercel com Flask + SQLite + Tailwind.

## Destaques que brilham para recrutadores
- Login/cadastro com hashing de senha e sessão protegida.
- Dashboard com métricas rápidas e navegação moderna (Tailwind CDN + Jinja).
- CRUD de contratos com validações e PDF completo (cláusulas genéricas, datas em dd/mm/aaaa, valores em reais por extenso e espaço para assinatura).
- SQLite com SQLAlchemy (fallback automático para `/tmp` em ambiente read-only).
- Pronto para Vercel: `requirements.txt`, entrypoint `main:app` e assets estáticos.

## Stack
- Python 3.9+
- Flask 3 (WSGI) + Blueprints
- SQLAlchemy 2 + SQLite
- Tailwind (CDN) + Jinja2
- fpdf2 para geração de PDF
- Gunicorn para ambiente local

## Arquitetura rápida
- `app/` (core): `controllers/` (auth, dashboard, contratos), `models/` (User, Contract), `views/` (layouts e telas), `db.py` (engine/sessão), `settings.py` (config).
- `main.py`: expõe `app` para a Vercel.
- `requirements.txt`: dependências para deploy.

## Rodando localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SECRET_KEY="dev-secret"               # defina o seu
export DATABASE_URL="sqlite:///instance/app.db"  # opcional, usa /tmp na Vercel
python main.py                               # http://localhost:3000
```

## Git Flow do projeto
- `main`: produção (deploy).
- `develop`: integração contínua.
- `feature/<nome>`: sai de `develop`, retorna para `develop`, depois seguimos para `main` (merge `--no-ff`). Limpeza das features após merge.

Exemplo:
```bash
git checkout develop && git pull
git checkout -b feature/minha-feature
# ... commits ...
git checkout develop && git merge --no-ff feature/minha-feature
git checkout main && git merge --no-ff develop
git push origin develop main
```
