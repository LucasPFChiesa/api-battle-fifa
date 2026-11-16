"""
API BATTLE - Performances de jogadores na FIFA
Arquiteturas de Software 2026/B

API REST com FastAPI + SQLite.

Endpoints exigidos no enunciado:
    POST   /fifa            -> insere um jogador
    GET    /fifa/count      -> quantidade de jogadores
    GET    /fifa            -> todos os jogadores
    GET    /fifa/id/{id}    -> 1 jogador pela coluna player_id
    GET    /fifa/nat/{exp}  -> jogadores pela regra nationality = 'Brazil'

A documentacao interativa (Swagger) fica em  /docs
e a alternativa (ReDoc) em  /redoc  (geradas automaticamente pelo FastAPI).
"""

import sqlite3
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Banco fica ao lado deste arquivo.
DB_PATH = Path(__file__).parent / "fifa.db"


def get_conn():
    """Abre uma conexao com o SQLite com acesso por nome de coluna."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Modelo de dados (mesmas colunas do dataset da Kaggle)
# ---------------------------------------------------------------------------
class Player(BaseModel):
    player_id: int
    player_name: str
    age: int
    nationality: str
    club: str
    position: str
    overall_rating: int
    potential_rating: int
    matches_played: int
    goals: int
    assists: int
    minutes_played: int
    market_value_million_eur: float
    contract_years_left: int
    injury_prone: str
    transfer_risk_level: str


# Para o POST o player_id e opcional: se nao vier, o banco gera (AUTOINCREMENT).
class PlayerIn(BaseModel):
    player_id: Optional[int] = None
    player_name: str
    age: int
    nationality: str
    club: str
    position: str
    overall_rating: int
    potential_rating: int
    matches_played: int
    goals: int
    assists: int
    minutes_played: int
    market_value_million_eur: float
    contract_years_left: int
    injury_prone: str
    transfer_risk_level: str


app = FastAPI(
    title="API Battle - FIFA",
    description="Performances de jogadores na FIFA. Arquiteturas de Software 2026/B.",
    version="1.0.0",
)


COLUMNS = [
    "player_id", "player_name", "age", "nationality", "club", "position",
    "overall_rating", "potential_rating", "matches_played", "goals", "assists",
    "minutes_played", "market_value_million_eur", "contract_years_left",
    "injury_prone", "transfer_risk_level",
]


def init_db():
    """Cria a tabela caso ainda nao exista."""
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            player_id                 INTEGER PRIMARY KEY,
            player_name               TEXT    NOT NULL,
            age                       INTEGER,
            nationality               TEXT,
            club                      TEXT,
            position                  TEXT,
            overall_rating            INTEGER,
            potential_rating          INTEGER,
            matches_played            INTEGER,
            goals                     INTEGER,
            assists                   INTEGER,
            minutes_played            INTEGER,
            market_value_million_eur  REAL,
            contract_years_left       INTEGER,
            injury_prone              TEXT,
            transfer_risk_level       TEXT
        )
        """
    )
    # Indices para acelerar as consultas que valem pontos por tempo.
    conn.execute("CREATE INDEX IF NOT EXISTS idx_nationality ON players(nationality)")
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post("/fifa", status_code=201)
def inserir_jogador(player: PlayerIn):
    """Insere um jogador. Se player_id nao for enviado, o banco gera um."""
    conn = get_conn()
    try:
        dados = player.model_dump()
        if dados["player_id"] is None:
            # Proximo id disponivel.
            row = conn.execute("SELECT COALESCE(MAX(player_id), 0) + 1 AS prox FROM players").fetchone()
            dados["player_id"] = row["prox"]

        placeholders = ", ".join(["?"] * len(COLUMNS))
        valores = [dados[c] for c in COLUMNS]
        conn.execute(
            f"INSERT INTO players ({', '.join(COLUMNS)}) VALUES ({placeholders})",
            valores,
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="player_id ja existe")
    finally:
        conn.close()
    return {"status": "inserido", "player_id": dados["player_id"]}


@app.get("/fifa/count")
def contar_jogadores():
    """Retorna a quantidade de jogadores cadastrados."""
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) AS total FROM players").fetchone()
    conn.close()
    return {"count": row["total"]}


@app.get("/fifa")
def listar_jogadores():
    """Retorna todos os jogadores."""
    conn = get_conn()
    rows = conn.execute("SELECT * FROM players").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/fifa/id/{player_id}")
def buscar_por_id(player_id: int):
    """Retorna 1 jogador pela coluna player_id."""
    conn = get_conn()
    row = conn.execute("SELECT * FROM players WHERE player_id = ?", (player_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="jogador nao encontrado")
    return dict(row)


@app.get("/fifa/nat/{exp}")
def buscar_por_nacionalidade(exp: str):
    """
    Consulta pela regra do enunciado: nationality = 'Brazil'.
    O parametro {exp} e recebido na rota; a regra fixa filtra por 'Brazil'.
    """
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM players WHERE nationality = ?", ("Brazil",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
