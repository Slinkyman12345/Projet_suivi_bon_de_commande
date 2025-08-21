import sqlite3
import datetime

TECH_DB_PATH = "gestion_technique.db"  # Chemin vers la base gestion technique

def log_action(utilisateur, action, tech_db_path=TECH_DB_PATH):
    try:
        conn = sqlite3.connect(tech_db_path)
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO logs (date, utilisateur, action) VALUES (?, ?, ?)", (now, utilisateur, action))
        conn.commit()

        # Nettoyage : garder max 500 logs
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        if count > 500:
            surplus = count - 500
            cursor.execute(f"DELETE FROM logs WHERE id IN (SELECT id FROM logs ORDER BY date ASC LIMIT {surplus})")
            conn.commit()

        conn.close()
    except Exception as e:
        print(f"Erreur lors de l'écriture du log : {e}")
