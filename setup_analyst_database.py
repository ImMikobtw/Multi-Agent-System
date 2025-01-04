import sqlite3

def setup_analyst_database():
    conn = sqlite3.connect('analyst_knowledge.db')
    c = conn.cursor()

    # таблица для знаний
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, interpretation TEXT)''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_analyst_database()
