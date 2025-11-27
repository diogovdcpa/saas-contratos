# Plano: Plataforma de Contratos de Prestacao de Servico

## Objetivo
Entregar um MVP para gerar e gerir contratos de prestacao de servico: cadastro de usuarios, criacao/listagem de contratos, armazenamento em SQLite e interface web simples (Flask + Jinja + Tailwind).

## Stack e padroes
- Flask 3 com blueprints para controllers.
- ORM: SQLAlchemy + SQLite (arquivo local). Considerar Alembic se precisarmos de migracoes.
- MVC adaptado: controllers (regras e rotas), models (ORM), views (templates Jinja), static (assets).
- Deploy alvo: Vercel (WSGI). Manter inicializacao minimalista no entrypoint.

## Estrutura proposta de pastas
```
app/
  __init__.py           # cria app, configura DB, registra blueprints
  settings.py           # configs de ambiente (DB path, secrets minimos)
  db.py                 # instancia do SQLAlchemy e helper de sessao
  models/
    __init__.py
    user.py
    contract.py
  controllers/
    __init__.py
    users.py            # rotas de user
    contracts.py        # rotas de contrato
  views/
    layout.html
    usuarios/
      lista.html
      form.html
    contratos/
      lista.html
      form.html
  static/
    css/, js/, imgs/    # opcional: manter Tailwind CDN por enquanto
main.py                 # entrypoint Vercel importando app
```

## Modelagem inicial
- User: id, nome, email (unique), created_at.
- Contract: id, titulo, descricao, preco (decimal), status (draft/assinado), data_vencimento, user_id (FK), created_at/updated_at.
- Opcional proximos passos: Template de contrato (para textos padrao) e historico de status/assinatura.

## Fluxo de controllers e views
- Users
  - GET /usuarios: lista usuarios (view usuarios/lista.html)
  - GET /usuarios/novo + POST /usuarios: cria usuario (usuarios/form.html)
- Contracts
  - GET /contratos: lista contratos (contratos/lista.html)
  - GET /contratos/novo + POST /contratos: cria contrato vinculado a usuario (contratos/form.html)
  - GET /contratos/<id>: detalhes simples (pode reutilizar view de lista com destaque)
- Views com Jinja + Tailwind CDN e layout base em views/layout.html.

## Persistencia e sessao
- Banco: SQLite em `instance/app.db` (ou raiz) com caminho configuravel via env `DATABASE_URL`.
- Sessao SQLAlchemy por contexto de request; teardown para fechar sessao.
- Semeadura opcional: criar usuario e contrato exemplo para demonstracao.

## Backlog (ordem sugerida)
1) Reorganizar estrutura para app/ com init, db e settings.  
2) Configurar SQLAlchemy e criar models User e Contract.  
3) Criar blueprints controllers/users.py e controllers/contracts.py.  
4) Adicionar templates base/layout e pastas de entidades.  
5) Rotas de CRUD minimo (lista + create) e validacoes basicas.  
6) Semeadura de dados de exemplo e doc de uso.  
7) Avaliar migracoes (Alembic) se os modelos forem estabilizados.

## Historias de usuario (MVP)
- Como usuario, quero poder me cadastrar e fazer login para acessar o sistema.  
- Como usuario autenticado, ao logar quero cair em uma dashboard principal com opcoes de listar meus contratos e criar novo contrato.  
- Como usuario, ao clicar em "novo contrato" quero um formulario para inserir dados de prestacao de servico (contratado, contratante, servico, valores, forma de pagamento, cidade, datas etc.).  
- Como usuario, depois de preencher o formulario quero salvar o contrato.  
- Como usuario, ao listar meus contratos quero uma opcao de gerar/imprimir o contrato em PDF.  
- Como usuario, quero poder editar ou excluir um contrato existente.

## Metodologia Gitflow adotada
- `main`: branch de produção; recebe merge apenas após validação em `develop`.
- `develop`: branch de integração contínua; recebe as features finalizadas.
- `feature/<nome>`: cada demanda nasce de `develop`, recebe commits e depois é mergeada de volta em `develop` via `--no-ff`.
- Fluxo básico:  
  1) `git checkout develop && git pull`  
  2) `git checkout -b feature/nome-da-feature`  
  3) Commits na feature  
  4) `git checkout develop && git merge --no-ff feature/nome-da-feature`  
  5) `git checkout main && git merge --no-ff develop`  
  6) `git push origin develop main` (ou push separado, conforme governança)  
- Limpeza: branches de feature podem ser removidas após merge; mantemos apenas `main` e `develop` ativas.
