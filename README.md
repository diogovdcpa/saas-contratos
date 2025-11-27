# SaaS de Contratos – Em Breve

Landing page simples construída em Flask para anunciar o futuro SaaS de geração de contratos de prestação de serviço. A view usa Jinja com Tailwind via CDN para entregar uma experiência moderna, pronta para deploy na Vercel.

## Stack
- Python 3.9+
- Flask 3 (WSGI)
- Tailwind CSS (CDN) + Jinja2
- Gunicorn para rodar localmente

## Rodando localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install flask gunicorn
gunicorn main:app
# app em http://localhost:8000
```

## Git Flow do projeto
- `main`: produção (deploy).
- `develop`: integração contínua.
- `feature/<nome>`: cada nova feature sai de `develop`, retorna para `develop` e depois segue para `main`.

Exemplo de fluxo:
```bash
git checkout develop && git pull
git checkout -b feature/minha-feature
# ... códigos e commits ...
git checkout develop
git merge --no-ff feature/minha-feature
git checkout main
git merge --no-ff develop
git push origin develop main
```
