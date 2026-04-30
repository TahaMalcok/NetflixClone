import pyodbc

class DataBaseManager:
    def __init__(self):
        self.server = "localhost"
        self.database = "NetflixLikeAppDb"
        self.driver = "{ODBC Driver 18 for SQL Server}"
        self.connection_string = (
            f"Driver={self.driver};"
            f"Server={self.server};"
            f"Database={self.database};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = pyodbc.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            print("Veritabanı bağlantısı kuruldı.")
        except Exception as e:
            print(f"Veritabanı bağlantısı kurulamadı.\n Hata: {e}")

    def disconnect(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Veritabanı bağlantısı kapatıldı.")

if __name__ == "__main__":
    db = DataBaseManager()
    db.connect()
    db.disconnect()