import pyodbc
from datetime import datetime

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

    def oturum_log(self, kullaniciıd):
        self.cursor.execute("""
            INSERT INTO OturumLog (KullaniciID) VALUES (?)
        """, (kullaniciıd,))

    def giris_yap(self, email, sifre):
        try:
            self.cursor.execute("""
                SELECT KullaniciID, RolID, Ad, Soyad
                FROM Kullanici
                WHERE Email = ? AND Sifre = ?
            """, (email, sifre))

            kullanici = self.cursor.fetchone()
            print(kullanici)

            if kullanici:
                self.cursor.execute("INSERT INTO OturumLog (KullaniciID) VALUES (?)", (kullanici[0],))
                self.conn.commit()
                print(f"Hoşgeldin {kullanici[2]} {kullanici[3]}")
                return kullanici
            else:
                print("Hatalı email veya şifre.")
                return None
        except Exception as e:
            print(f"Giriş sırasında hata oluştu. Hata kodu{e}")
            return None

    def kayit_yap(self, ad, soyad, email, sifre, dogum_yili, cinsiyet, ulke, secilen_turler):
        try:
            self.cursor.execute("SELECT KullaniciID FROM Kullanici WHERE Email = ?", (email,))
            if self.cursor.fetchone():
                return "Bu mail adresi ile oluşturulmuş bir hesap bulunmakta."
            if len(sifre) < 6 or len(sifre) > 50:
                return "Şifre en az 6 karakter uzunluğunda en fazla 50 karakter uzunluğunda olabilir."
            if len(secilen_turler) != 3:
                return "3 tane favori türünüzü seçmeniz gerekiyor."

            try:
                dogum_tarihi = datetime.strptime(dogum_yili, "%Y-%m-%d").date()
                bugun = datetime.now().date()
                if dogum_tarihi > bugun:
                    return "Geçerli bir doğum tarihi giriniz."
            except ValueError:
                return "Geçerli formatta bir tarih giriniz. (YYYY-AA-GG)"

            rol_ıd = 1

            self.cursor.execute("""
                INSERT INTO Kullanici(RolID, Ad, Soyad, Ulke, Cinsiyet, DogumTarihi, Email, Sifre)
                OUTPUT INSERTED.KullaniciID
                Values(?, ?, ?, ?, ?, ?, ?, ?)
                """, (rol_ıd, ad, soyad, ulke, cinsiyet, dogum_yili, email, sifre))
            yeni_kullanici_ıd = self.cursor.fetchone()[0]

            for tur in secilen_turler:
                self.cursor.execute("SELECT TurID FROM Tur WHERE TurAdi = ?", (tur,))
                tur_ıd = self.cursor.fetchone()[0]

                self.cursor.execute("INSERT INTO KullaniciTur(KullaniciID, TurID) VALUES (?, ?)", (yeni_kullanici_ıd, tur_ıd))

            self.conn.commit()
            return "Kayıt başarılı."

        except Exception as e:
            return f"Hata oluştu. Hata kodu {e}"

    def ortalama_puan_hesapla(self, program):
        try:
            self.cursor.execute("SELECT ProgramID FROM Program WHERE ProgramAdi = ?", (program,))
            programıd = self.cursor.fetchone()

            self.cursor.execute("""
                SELECT ISNULL(AVG(CAST(Puan AS FLOAT)), 0)
                FROM KullaniciProgram
                WHERE ProgramID = ?
                """, (programıd[0],))

            ortalama = self.cursor.fetchone()[0]
            return round(ortalama, 1)
        except Exception as e:
            return f"Hata oluştu: {e} hata kodu."

    def tum_programlari_listele(self):
        try:
            self.cursor.execute("""
            SELECT
                p.ProgramID,
                p.ProgramAdi,
                p.Tip,
                p.Aciklama,
                p.YayinYili,
                p.BolumSayisi,
                ISNULL(AVG(CAST(kp.Puan AS FLOAT)), 0) AS OrtalamaPuan
            FROM Program p
            LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
            GROUP BY
                p.ProgramID, p.ProgramAdi, p.Tip, p.Aciklama, p.YayinYili, p.BolumSayisi
            ORDER BY p.ProgramAdi ASC
            """)

            return self.cursor.fetchall()
        except Exception as e:
            return f"Hata oluştu: {e} hata kodu."

    def ture_gore_arama(self, tur):
        try:
            self.cursor.execute("""
                SELECT p.*
                FROM Program
                INNER JOIN ProgramTur pt ON p.ProgramID = pt.ProgramID
                INNER JOIN Tur t ON pt.TurID = t.TurID
                WHERE t.TurAdi = ?
            """, (tur,))
            return self.cursor.fetchall()
        except Exception as e:
            return f"Hata oluştu: {e} hata kodu."

    def filtrele(self, tip):
        try:
            self.cursor.execute("SELECT * FROM Program WHERE Tip = ?", (tip,))
            programlar = self.cursor.fetchall()

            return programlar
        except Exception as e:
            return f"Hata oluştu: {e} hata kodu."

    def favori_ekle(self, program, kullaniciıd):
        try:
            self.cursor.execute("SELECT ProgramID FROM Program WHERE ProgramAdi = ?", (program,))
            programıd = self.cursor.fetchone()
            self.cursor.execute("INSERT INTO Favori VALUES (?, ?)", (kullaniciıd, programıd[0]))
            self.conn.commit()
        except Exception as e:
            return f"Hata oluştu: {e} hata kodu."

    def puanlama(self, kullaniciıd, program, puan):
        if not ( 1 <= puan <= 10):
            return "Hata: Puan 1 ile 10 arasında olmalı."

        self.cursor.execute("SELECT ProgramID FROM Program WHERE ProgramAdi = ?", (program,))
        programıd = self.cursor.fetchone()

        try:
            self.cursor.execute("""
                SELECT Puan FROM KullaniciProgram
                WHERE KullaniciID = ? AND ProgramID = ?
            """, (kullaniciıd[0], programıd[0]))
            mevcutkayit = self.cursor.fetchone()

            if mevcutkayit:
                self.cursor.execute("""
                    UPDATE KullaniciProgram 
                    SET Puan = ?
                    WHERE KullaniciID = ? AND ProgramID = ?
                """, (puan, kullaniciıd, programıd))
                mesaj = "Puanınız başarıyla güncelle."
            else:
                self.cursor.execute("""
                    INSERT INTO KullaniciProgram(KullaniciID, ProgramID, Puan)
                    VALUES (?, ?, ?)
                """, (kullaniciıd[0], programıd[0], puan))
                mesaj = "Puanınız başarıyla kaydedildi."
            self.conn.commit()
            return mesaj
        except Exception as e:
            self.conn.rollback()
            return f"Puanlama sırasında hata oluştu: {e}"

if __name__ == "__main__":
    db = DataBaseManager()
    db.connect()
    db.oturum_log("Ahmet")
    db.disconnect()

#Hep normal kullanıcı olarak giriş yapıyo yönetici olarak yapmıyo.
#Kayıt olurken türlerin ıdleri ile alıyo isimleri ile almalı