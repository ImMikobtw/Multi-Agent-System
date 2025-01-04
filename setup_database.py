import sqlite3

def setup_database():
    conn = sqlite3.connect('knowledge.db')
    c = conn.cursor()

    # Таблица гой братешка
    c.execute('''CREATE TABLE IF NOT EXISTS knowledge
                 (id INTEGER PRIMARY KEY, topic TEXT, content TEXT)''')

    # временная база для ресерчера
    knowledge_data = [
        (1, 'Python', 'Python is a high-level, interpreted programming language.'),
        (2, 'Machine Learning', 'Machine Learning is a subset of AI that involves training algorithms on data.'),
        (3, 'Databases', 'Databases are organized collections of data, generally stored and accessed electronically.'),
        (4, 'Cloud Computing', 'Cloud Computing provides on-demand computing services over the internet.'),
        (5, 'Data Science', 'Data Science involves extracting insights from data.'),
        (6, 'Cybersecurity', 'Cybersecurity protects systems and networks from digital attacks.'),
        (7, 'Artificial Intelligence', 'AI enables machines to mimic human intelligence.'),
        (8, 'Blockchain', 'Blockchain is a distributed ledger technology.'),
        (9, 'Quantum Computing', 'Quantum Computing uses quantum-mechanical phenomena to perform computation.'),
        (10, 'Big Data', 'Big Data involves large volumes of data that can be analyzed for insights.')
    ]

    c.executemany('INSERT OR REPLACE INTO knowledge (id, topic, content) VALUES (?, ?, ?)', knowledge_data)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
