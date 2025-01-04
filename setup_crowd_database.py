import sqlite3

def setup_crowd_database():
    conn = sqlite3.connect('crowd_knowledge.db')
    c = conn.cursor()

    # Таблица для знаний от чуваков
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, content TEXT)''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_crowd_database()
