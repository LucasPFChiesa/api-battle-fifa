# API Battle - FIFA

API REST do tema **Performances de jogadores na FIFA** (Arquiteturas de Software 2026/B).

Stack: **Python + FastAPI + SQLite** (simples, rápido e com documentação automática).

## Endpoints (os 5 exigidos)

| Método | Rota | O que faz |
|--------|------|-----------|
| POST | `/fifa` | insere um jogador |
| GET | `/fifa/count` | quantidade de jogadores |
| GET | `/fifa` | todos os jogadores |
| GET | `/fifa/id/{id}` | 1 jogador pela coluna `player_id` |
| GET | `/fifa/nat/{exp}` | jogadores pela regra `nationality = 'Brazil'` |

Documentação interativa (gerada automática): `/docs` (Swagger) e `/redoc`.

## Como rodar

1. Instalar dependências (uma vez):

```bash
cd fifa-api
uv venv .venv
uv pip install --python .venv -r requirements.txt
```

> Sem `uv`? Use `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
> (precisa do pacote `python3-venv`).

2. Carregar a base (inserção em lote a partir do CSV):

```bash
.venv/bin/python carregar_dados.py
```

3. Subir a API:

```bash
.venv/bin/uvicorn app:app --host 0.0.0.0 --port 29480
```

Na VM use `--host 0.0.0.0` para a API ficar acessível pela rede.

## Testar rápido

```bash
curl http://127.0.0.1:29480/fifa/count
curl http://127.0.0.1:29480/fifa/id/4
curl http://127.0.0.1:29480/fifa/nat/brazil
```

A coleção `API_Battle_FIFA.postman_collection.json` tem todas as rotas prontas
para importar no Postman/Insomnia (variável `base_url`).

## Arquivos

- `app.py` — a API (os 5 endpoints)
- `carregar_dados.py` — script de inserção em lote (lê o CSV e popula o SQLite)
- `requirements.txt` — dependências
- `API_Battle_FIFA.postman_collection.json` — coleção de testes
- `fifa.db` — banco SQLite (gerado pelo script de carga; 2800 jogadores)
