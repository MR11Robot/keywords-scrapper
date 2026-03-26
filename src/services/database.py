# database.py

import sqlite3

class Database:
    def __init__(self, name: str, keywords_table_name: str):
        self.name = name
        self.keywords_table_name = keywords_table_name
        self.create_table_if_not()

    def create_table_if_not(self):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute(f"CREATE TABLE IF NOT EXISTS {self.keywords_table_name}(words TEXT, country TEXT)")
        conn.commit()
        conn.close()

    def insert_words_with_country(self, headers: dict, all_data: dict):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        
        for sheet_name in headers.keys():
            if sheet_name == "Sheet1":
                continue
            
            for i, row in enumerate(all_data[sheet_name]):
                word = row[0]
                
                cur.execute(f"""INSERT INTO {self.keywords_table_name} VALUES (?, ?);""", (word, sheet_name))
            print("----------------------------")

        
            
        conn.commit()
        conn.close()
    
    def delete_keywords(self):
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {self.keywords_table_name}")
        conn.commit()
        conn.close()

    def get_keywords(self, country_code: str) -> list:
        conn = sqlite3.connect(self.name)
        cur = conn.cursor()
        
        cur.execute(
            f"SELECT * FROM {self.keywords_table_name} WHERE country = ?;",
            (country_code,)
        )
        keywords = [row[0] for row in cur.fetchall()]
        
        conn.commit()
        conn.close()
        
        return keywords