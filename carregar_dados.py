"""
Script de insercao em lote (carga inicial da base).

Le o CSV do dataset (Base FIFA - Kaggle) e insere todos os registros
na tabela 'players' do SQLite.

Uso:
    python carregar_dados.py [caminho_do_csv]

Se nenhum caminho for passado, usa ../fifa_player_performance_market_value.csv
"""

import csv
import sqlite3
import sys
from pathlib import Path

PASTA = Path(__file__).parent
DB_PATH = PASTA / "fifa.db"
CSV_PADRAO = PASTA.parent / "fifa_player_performance_market_value.csv"

COLUMNS = [
    "player_id", "player_name", "age", "nationality", "club", "position",
    "overall_rating", "potential_rating", "matches_played", "goals", "assists",
    "minutes_played", "market_value_million_eur", "contract_years_left",
    "injury_prone", "transfer_risk_level",
]

INT_COLS = {
    "player_id", "age", "overall_rating", "potential_rating", "matches_played",
    "goals", "assists", "minutes_played", "contract_years_left",
}
FLOAT_COLS = {"market_value_million_eur"}


def criar_tabela(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            player_id                 INTEGER PRIMARY KEY,
            player_name               TEXT NOT NULL,
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_nationality ON players(nationality)")


def converter(coluna, valor):
    valor = valor.strip()
    if coluna in INT_COLS:
        return int(valor)
    if coluna in FLOAT_COLS:
        return float(valor)
    return valor


def main():
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CSV_PADRAO
    if not csv_path.exists():
        print(f"CSV nao encontrado: {csv_path}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    criar_tabela(conn)
    # Carga limpa: zera a tabela antes de inserir tudo de novo.
    conn.execute("DELETE FROM players")

    placeholders = ", ".join(["?"] * len(COLUMNS))
    sql = f"INSERT INTO players ({', '.join(COLUMNS)}) VALUES ({placeholders})"

    total = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        lote = []
        for linha in leitor:
            valores = [converter(c, linha[c]) for c in COLUMNS]
            lote.append(valores)
            if len(lote) >= 500:
                conn.executemany(sql, lote)
                total += len(lote)
                lote = []
        if lote:
            conn.executemany(sql, lote)
            total += len(lote)

    conn.commit()
    conn.close()
    print(f"Insercao em lote concluida: {total} jogadores inseridos em {DB_PATH}")


if __name__ == "__main__":
    main()
