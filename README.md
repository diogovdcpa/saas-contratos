# SaaS de Contratos ⚡️
Plataforma web para gerar contratos de prestação de serviço, com autenticação, CRUD e exportação em PDF com cláusulas padrão e área de assinatura. Pronta para rodar em Vercel com Flask + SQLite + Tailwind.

## Principais recursos
- Login e cadastro com hash de senha e sessão protegida.
- Dashboard com métricas e navegação moderna (Tailwind CDN + Jinja).
- CRUD de contratos com validações e PDF completo (cláusulas genéricas, datas em dd/mm/aaaa, valores em reais por extenso e espaço para assinatura).
- Persistência com SQLAlchemy + SQLite e fallback automático para `/tmp` em ambiente read-only.
- Preparado para Vercel: `requirements.txt`, entrypoint `main:app` e assets estáticos.

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
