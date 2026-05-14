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

    def oturum_log(self, kullanici_id):
        self.cursor.execute("""
            INSERT INTO OturumLog (kullanici_id) VALUES (?)
        """, (kullanici_id,))
        self.conn.commit()

    def giris_yap(self, email, sifre):
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

    def kayit_yap(self, ad, soyad, email, sifre, dogum_yili, cinsiyet, ulke, secilen_turler):
        self.cursor.execute("SELECT KullaniciID FROM Kullanici WHERE Email = ?", (email,))
        if self.cursor.fetchone():
            return "Bu mail adresi ile oluşturulmuş bir hesap bulunmakta."
        if len(sifre) < 6 or len(sifre) > 50:
            return "Şifre en az 6 karakter uzunluğunda en fazla 50 karakter uzunluğunda olabilir."
        if len(secilen_turler) != 3:
               return "3 tane favori türünüzü seçmeniz gerekiyor."

        rol_id = 1
        print("1")
        self.cursor.execute("""
            INSERT INTO Kullanici (RolID, Ad, Soyad, Ulke, Cinsiyet, DogumTarihi, Email, Sifre)
            OUTPUT INSERTED.KullaniciID
            Values(?, ?, ?, ?, ?, ?, ?, ?)
            """, (rol_id, ad, soyad, ulke, cinsiyet, dogum_yili, email, sifre))
        yeni_kullanici_id = self.cursor.fetchone()[0]
        print("2")
        for tur in secilen_turler:
            self.cursor.execute("SELECT TurID FROM Tur WHERE TurAdi = ?", (tur,))
            tur_id = self.cursor.fetchone()[0]
            print("3")
            self.cursor.execute("INSERT INTO KullaniciTur(KullaniciID, TurID) VALUES (?, ?)", (yeni_kullanici_id, tur_id))

        self.conn.commit()
        return "Kayıt başarılı."

    def tum_programlari_listele(self):
        self.cursor.execute("""
        SELECT
            p.ProgramID,
            p.ProgramAdi,
            p.Tip,
            p.YayinYili,
            p.BolumSayisi,
            STRING_AGG(t.TurAdi, ', ') AS Turler,
            ISNULL(AVG(CAST(kp.Puan AS FLOAT)), 0) AS OrtalamaPuan
        FROM Program p
        LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
        LEFT JOIN ProgramTur pt ON p.ProgramID = pt.ProgramID
        LEFT JOIN Tur t ON pt.TurID = t.TurID
        GROUP BY
            p.ProgramID, p.ProgramAdi, p.Tip, p.YayinYili, p.BolumSayisi
        ORDER BY p.ProgramAdi ASC
        """)
        satirlar = self.cursor.fetchall()
        program_listesi = []

        for satir in satirlar:
            program_listesi.append({
                "ProgramID": satir[0],
                "ProgramAdi": satir[1],
                "Tip": satir[2],
                "YayinYili": satir[3],
                "BolumSayisi": satir[4],
                "Turler": satir[5],
                "OrtalamaPuan": satir[6]
            })

        return program_listesi

    def ture_gore_arama(self, tur):
        self.cursor.execute("""
         SELECT
             p.ProgramID,
             p.ProgramAdi,
             p.Tip,
             p.YayinYili,
             p.BolumSayisi,
             STRING_AGG(t.TurAdi, ', ') AS Turler,
             ISNULL(AVG(CAST(kp.Puan AS FLOAT)), 0) AS OrtalamaPuan
         FROM Program p
         LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
         LEFT JOIN ProgramTur pt ON p.ProgramID = pt.program_id
         LEFT JOIN Tur t ON pt.TurID = t.TurID
         
         WHERE p.ProgramID IN (
            SELECT pt_alt.ProgramID FROM ProgramTur pt_alt
            INNER JOIN Tur t_alt ON pt_alt.TurID = t_alt.TurID
            WHERE TurAdi = ?
         )
         GROUP BY
             p.ProgramID, p.ProgramAdi, p.Tip, p.YayinYili, p.BolumSayisi
         ORDER BY p.ProgramAdi ASC
         """, (tur,))

        satirlar = self.cursor.fetchall()
        program_listesi = []

        for satir in satirlar:
            program_listesi.append({
                "ProgramID": satir[0],
                "ProgramAdi": satir[1],
                "Tip": satir[2],
                "YayinYili": satir[3],
                "BolumSayisi": satir[4],
                "Turler": satir[5],
                "OrtalamaPuan": satir[6]
            })

        return program_listesi

    def filtrele(self, tip):
        self.cursor.execute("""
               SELECT
                   p.ProgramID,
                   p.ProgramAdi,
                   p.Tip,
                   p.YayinYili,
                   p.BolumSayisi,
                   STRING_AGG(t.TurAdi, ', ') AS Turler,
                   ISNULL(AVG(CAST(kp.Puan AS FLOAT)), 0) AS OrtalamaPuan
               FROM Program p
               LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
               LEFT JOIN ProgramTur pt ON p.ProgramID = pt.ProgramID
               LEFT JOIN Tur t ON pt.TurID = t.TurID
               WHERE p.Tip = ?
               GROUP BY
                   p.ProgramID, p.ProgramAdi, p.Tip, p.YayinYili, p.BolumSayisi
               ORDER BY p.ProgramAdi ASC
               """, (tip,))
        satirlar = self.cursor.fetchall()
        program_listesi = []

        for satir in satirlar:
            program_listesi.append({
                "ProgramID": satir[0],
                "ProgramAdi": satir[1],
                "Tip": satir[2],
                "YayinYili": satir[3],
                "BolumSayisi": satir[4],
                "Turler": satir[5],
                "OrtalamaPuan": satir[6]
            })

        return program_listesi

    def detay(self, kullanici_id, program_id):
        self.cursor.execute("""
            SELECT 
                p.ProgramAdi, p.Aciklama, p.Tip, p.YayinYili, p.BolumSayisi,
                STRING_AGG(t.TurAdi, ', ') AS Turler,
                ISNULL(AVG(CAST(kp.Puan AS Float)), 0) AS OrtalamaPuan,
                (SELECT COUNT(*) FROM IzlemeLog WHERE ProgramID = p.ProgramID) AS ToplamIzlenme,
                (SELECT Puan FROM KullaniciProgram WHERE ProgramID = p.ProgramID AND  KullaniciID = ?) AS KullaniciPuan,
                (SELECT COUNT(*) FROM Favori WHERE ProgramID = p.ProgramID AND KullaniciID = ?) AS FavoriVarMi,
                (SELECT AVG(Uzunluk) FROM Bolum WHERE ProgramID = p.ProgramID) AS OrtalamaUzunluk
            FROM Program p 
            LEFT JOIN ProgramTur pt ON p.ProgramID = pt.ProgramID
            LEFT JOIN Tur t ON pt.TurID = t.TurID
            LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
            WHERE p.ProgramID = ?
            GROUP BY p.ProgramID, p.ProgramAdi, p.Aciklama, p.Tip, p.YayinYili, p.BolumSayisi
        """, (kullanici_id, kullanici_id, program_id))
        ana_veri = self.cursor.fetchone()

        self.cursor.execute("""
            SELECT TOP 1 b.BolumNo, i.IzlenenSure, i.BittiMi
            FROM IzlemeLog i
            JOIN Bolum b ON i.BolumID = b.BolumID
            WHERE i.KullaniciID = ? AND i.ProgramID = ?
            ORDER BY i.IzlemeTarihi DESC
        """, (kullanici_id, program_id))
        son_izleme = self.cursor.fetchone()

        bilgiler = {
            "ProgramID": program_id,
            "ProgramAdi": ana_veri[0],
            "Aciklama": ana_veri[1],
            "Tip": ana_veri[2],
            "YayinYili": ana_veri[3],
            "BolumSayisi": ana_veri[4],
            "Turler": ana_veri[5],
            "OrtalamaPuan": ana_veri[6],
            "ToplamIzlenme": ana_veri[7],
            "KullaniciPuan": ana_veri[8] if ana_veri[8] else "Puan Verilmedi",
            "Favori": True if ana_veri[9] > 0 else False,
            "OrtalamaUzunluk": int(ana_veri[10]),
            "DahaOnceIzlediMi": True if son_izleme else False,
            "KalınanBolum": son_izleme[0] if son_izleme else 1,
            "KalınanSure": son_izleme[1] if son_izleme else 0,
            "SonIzlemeBittiMi": son_izleme[2] if son_izleme else False
        }
        return bilgiler

    def bolum_listesi(self, program_id):
        self.cursor.execute("SELECT BolumNo, Uzunluk FROM Bolum WHERE ProgramID = ? ORDER BY BolumNo", (program_id,))
        satirlar = self.cursor.fetchall()
        bolumler = []

        for satir in satirlar:
            bolumler.append({
                "BolumNo": satir[0],
                "Sure": satir[1]
            })
        return  bolumler

    def favori_ekle(self, program_id, kullanici_id):
        self.cursor.execute("SELECT * FROM Favori WHERE KullaniciID= ? AND ProgramID = ? ", (kullanici_id, program_id))
        varmi = self.cursor.fetchone()
        if varmi:
            return "Zaten favorilerinizde."
        else:
            self.cursor.execute("INSERT INTO Favori VALUES (?, ?)", (kullanici_id, program_id))
            self.conn.commit()

    def favori_silme(self, program_id, kullanici_id):
        self.cursor.execute("DELETE FROM Favori WHERE KullaniciID = ? AND ProgramID = ?", (kullanici_id, program_id))
        self.conn.commit()

    def favori_listele(self, kullanici_id):
        self.cursor.execute("""
            SELECT p.ProgramID, p.ProgramAdi
            FROM Program p 
            INNER JOIN Favori f ON f.ProgramID = p.ProgramID
            WHERE f.KullaniciID = ?
        """, (kullanici_id,))
        filmler = self.cursor.fetchall()
        bilgi = []
        for film in filmler:
            bilgi.append({
                "ProgramID": film[0],
                "ProgramAdi": film[1]
            })
        return bilgi

    def puanlama(self, kullanici_id, program_id, puan):
        self.cursor.execute("""
            SELECT Puan FROM KullaniciProgram
            WHERE KullaniciID = ? AND ProgramID = ?
        """, (kullanici_id, program_id))
        mevcutkayit = self.cursor.fetchone()


        if mevcutkayit:
            self.cursor.execute("""
                UPDATE KullaniciProgram 
                SET Puan = ?
                WHERE KullaniciID = ? AND program_id = ?
            """, (puan, kullanici_id, program_id))
            mesaj = "Puanınız başarıyla güncelle."
        else:
            self.cursor.execute("""
                INSERT INTO KullaniciProgram(KullaniciID, ProgramID, Puan)
                VALUES (?, ?, ?)
            """, (kullanici_id, program_id, puan))
            mesaj = "Puanınız başarıyla kaydedildi."
        self.conn.commit()
        return mesaj

    def izleme_log(self, kullanici_id, program_id, bolum_no, izlenen_sure):
        self.cursor.execute("""
            SELECT BolumID, Uzunluk FROM Bolum
            WHERE BolumNo = ? AND ProgramID = ?
            """, (bolum_no, program_id))
        bolum_id = self.cursor.fetchone()

        bittimi = False
        if bolum_id[1] == izlenen_sure:
            bittimi = True
        else:
            bittimi = False

        self.cursor.execute("""
            INSERT INTO IzlemeLog (KullaniciID, ProgramID, BolumID, IzlenenSure, IzlemeTarihi, BittiMi)
            VALUES (?, ?, ?, ?, GETDATE(), ?)
            """, (kullanici_id, program_id, bolum_id[0], izlenen_sure, bittimi))
        self.conn.commit()

    def izleme_gecmisi(self, kullanici_id):
        self.cursor.execute("""
            SELECT p.ProgramAdi, b.BolumNo, i.IzlenenSure, i.IzlemeTarihi, i.BittiMi, kp.Puan
            FROM IzlemeLog i
            INNER JOIN Program p ON p.ProgramID = i.ProgramID
            INNER JOIN Bolum b ON b.BolumID = i.BolumID
            LEFT JOIN KullaniciProgram kp ON i.ProgramID = kp.ProgramID AND kp.KullaniciID = i.KullaniciID
            WHERE i.KullaniciID = ?
            ORDER BY i.IzlemeTarihi DESC
        """, (kullanici_id,))
        satirlar = self.cursor.fetchall()
        filmler = []

        for satir in satirlar:
            filmler.append({
                "ProgramAdi": satir[0],
                "BolumNo": satir[1],
                "IzlenenSure": satir[2],
                "IzlemeTarihi": satir[3].strftime("%d/%m/%Y %H:%M"),
                "BittiMi": True if satir[4] else False,
                "VerilenPuan": satir[5] if satir[5] is not None else "-"
            })
        return filmler

    def profil_bilgileri(self, kullanici_id):
        self.cursor.execute("""
            SELECT Ad, Soyad, Email, DogumTarihi, Ulke
            FROM Kullanici 
            WHERE KullaniciID = ?
        """, (kullanici_id,))
        bilgiler = self.cursor.fetchone()

        self.cursor.execute("""
            SELECT t.Turadi
            FROM Tur t
            INNER JOIN KullaniciTur kt ON t.TurID = kt.TurID
            WHERE kt.KullaniciID = ?
        """, (kullanici_id,))
        turler = [satir[0] for satir in self.cursor.fetchall()]

        self.cursor.execute("""
            SELECT ISNULL(SUM(IzlenenSure), 0) FROM IzlemeLog
            WHERE KullaniciID = ?
        """, (kullanici_id,))
        sure = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT ISNULL(AVG(CAST(Puan AS FLOAT)), 0) 
            FROM KullaniciProgram 
            WHERE KullaniciID = ?
        """, (kullanici_id,))
        puan = self.cursor.fetchone()[0]

        self.cursor.execute("""
            SELECT COUNT(DISTINCT ProgramID)
            FROM IzlemeLog
            WHERE KullaniciID = ?
        """, (kullanici_id,))
        izlenen_sayi = self.cursor.fetchone()[0]

        profil_bilgileri = {
            "Ad": bilgiler[0],
            "Soyad": bilgiler[1],
            "Email": bilgiler[2],
            "DoğumTarihi": bilgiler[3].strftime("%d/%m/%Y"),
            "Ülke": bilgiler[4],
            "FavoriTürler": turler,
            "İzlenenSüre": sure,
            "OrtalamaPuan": puan,
            "IzlenenSayi": izlenen_sayi
        }

        return profil_bilgileri

    def sifre_güncelleme(self, kullanici_ıd, yeni_sifre):
        self.cursor.execute("""
            UPDATE Kullanici 
            SET Sifre = ?
            WHERE KullaniciID = ?
        """, (yeni_sifre, kullanici_ıd))
        self.conn.commit()

    def isimle_arama(self, program_adi):
        self.cursor.execute("""
                SELECT
                    p.ProgramID,
                    p.ProgramAdi,
                    p.Tip,
                    p.YayinYili,
                    p.BolumSayisi,
                    STRING_AGG(t.TurAdi, ', ') AS Turler,
                    ISNULL(AVG(CAST(kp.Puan AS FLOAT)), 0) AS OrtalamaPuan
                FROM Program p
                LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
                LEFT JOIN ProgramTur pt ON p.ProgramID = pt.ProgramID
                LEFT JOIN Tur t ON pt.TurID = t.TurID
                WHERE p.ProgramAdi = ?
                GROUP BY
                    p.ProgramID, p.ProgramAdi, p.Tip, p.YayinYili, p.BolumSayisi
                ORDER BY p.ProgramAdi ASC
                """, (program_adi,))
        satirlar = self.cursor.fetchall()
        program_listesi = []

        for satir in satirlar:
            program_listesi.append({
                "ProgramID": satir[0],
                "ProgramAdi": satir[1],
                "Tip": satir[2],
                "YayinYili": satir[3],
                "BolumSayisi": satir[4],
                "Turler": satir[5],
                "OrtalamaPuan": satir[6]
            })

        return program_listesi

    def kullanici_turleri(self, kullanici_id):
        self.cursor.execute("""
            SELECT t.TurAdi
            FROM Tur t
            INNER JOIN KullaniciTur kt ON t.TurID = kt.TurID
            WHERE kt.KullaniciID = ?
        """, (kullanici_id,))

        return [satir[0] for satir in self.cursor.fetchall()]

    def oneri(self, kullanici_id):
        self.cursor.execute("""
                        SELECT t.TurAdi
                        FROM Tur t
                        INNER JOIN KullaniciTur kt ON t.TurID = kt.TurID
                        WHERE kt.KullaniciID = ?
                    """, (kullanici_id,))
        turler = [satir[0] for satir in self.cursor.fetchall()]

        oneriler = {}
        for tur in turler:
            self.cursor.execute("""
                SELECT TOP 2 
                p.ProgramID,
                p.ProgramAdi,
                p.Tip,
                p.YayinYili,
                p.BolumSayisi,
                (
                    SELECT STRING_AGG(t_alt.TurAdi, ', ') 
                    FROM ProgramTur pt_alt
                    INNER JOIN Tur t_alt ON pt_alt.TurID = t_alt.TurID
                    WHERE pt_alt.ProgramID = p.ProgramID
                ) AS Turler,
                ISNULL(AVG(CAST(kp.Puan AS FLOAT)), 0) AS OrtalamaPuan
                FROM Program p
                INNER JOIN ProgramTur pt ON p.ProgramID = pt.ProgramID
                INNER JOIN Tur t ON pt.TurID = t.TurID
                LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
                WHERE t.TurAdi = ?
                GROUP BY p.ProgramID, p.ProgramAdi, p.Tip, p.YayinYili, p.BolumSayisi
                ORDER BY OrtalamaPuan DESC
            """, (tur,))

            filmler = self.cursor.fetchall()
            oneriler[tur] = []

            for film in filmler:
                oneriler[tur].append({
                    "ProgramID": film[0],
                    "ProgramAdi": film[1],
                    "Tip": film[2],
                    "YayinYili": film[3],
                    "BolumSayisi": film[4],
                    "Turler": film[5],
                    "OrtalamaPuan": film[6]
                })

        return oneriler

    def bolum_goster(self, program_id):
        self.cursor.execute("""
            SELECT BolumNo, Uzunluk
            FROM Bolum
            WHERE ProgramID = ?
        """, (program_id,))
        return self.cursor.fetchall()

    def içerik_ekle(self, programadi, tip, aciklama, yayinyili, bolumsayisi, turler):
        self.cursor.execute("""
            INSERT INTO Program (ProgramAdi, Tip, Aciklama, YayinYili, BolumSayisi)
            OUTPUT INSERTED.ProgramID
            VALUES (?, ?, ?, ?, ?)
        """, (programadi, tip, aciklama, yayinyili, bolumsayisi))
        programıd = self.cursor.fetchone()[0]
        self.conn.commit()

        for tur in turler:
            self.cursor.execute("""
                SELECT TurID FROM Tur
                WHERE TurAdi = ?
            """, (tur,))
            turıd = self.cursor.fetchone()[0]

            self.cursor.execute("""
                INSERT INTO ProgramTur (ProgramID, TurID)
                VALUES (?, ?)
            """, (programıd, turıd))
        self.conn.commit()

    def içerik_sil(self, program_id):
        try:
            self.cursor.execute("DELETE FROM IzlemeLog WHERE ProgramID = ? ", (program_id,))
            self.cursor.execute("DELETE FROM Favori WHERE ProgramID = ?", (program_id,))
            self.cursor.execute("DELETE FROM ProgramTur WHERE ProgramID = ? ", (program_id,))
            self.cursor.execute("DELETE FROM Bolum WHERE ProgramID = ? ", (program_id,))
            self.cursor.execute("DELETE FROM KullaniciProgram WHERE ProgramID = ?", (program_id,))
            self.cursor.execute("DELETE FROM Program WHERE ProgramID = ?", (program_id,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            return "İçerik silinirken hata oluştu. Veriler korundu."
    def tur_ekle(self, turadi):
        self.cursor.execute("""
            SELECT * FROM Tur
            WHERE TurAdi = ?
        """, (turadi,))
        varmi = self.cursor.fetchone()

        if varmi:
            return "Hata bu tür zaten sistemde var."
        else:
            self.cursor.execute("""
                INSERT INTO Tur (TurAdi)
                VALUES (?)
            """, (turadi,))
            self.conn.commit()

    def tur_guncelleme(self, eskituradi, yenituradi):
        self.cursor.execute("""
            UPDATE Tur
            SET TurAdi = ?
            WHERE TurAdi = ?
        """, (yenituradi, eskituradi))
        self.conn.commit()

    def tur_sil(self, turadi):
        self.cursor.execute("""
            SELECT TurID FROM Tur WHERE TurAdi = ?
        """, (turadi,))
        turid = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT * FROM ProgramTur WHERE TurID = ?", (turid,))
        varmi = self.cursor.fetchone()

        if varmi:
            return "Bu türe ait programlar bulunduğu için silinemez."
        else:
            self.cursor.execute("DELETE FROM Tur WHERE TurID = ?", (turid,))
            self.conn.commit()

    def program_tur_ekle(self, eklenecektur, program_id):
        self.cursor.execute("""
            SELECT TurID FROM Tur WHERE TurAdi = ?
        """, (eklenecektur,))
        sonuc = self.cursor.fetchone()
        if not sonuc:
            return "Bu tür sistemde bulunamadı."

        turid = sonuc[0]
        self.cursor.execute("""
            SELECT * FROM ProgramTur
            WHERE ProgramID = ? AND TurID = ?
        """, (program_id, turid))
        varmi = self.cursor.fetchone()

        if varmi:
            return "Bu film zaten bu türe sahip."
        else:
            self.cursor.execute("""
                INSERT INTO ProgramTur (ProgramID, TurID)
                VALUES (?, ?) 
            """, (program_id, turid))
            self.conn.commit()

    def program_aciklama_degis(self, program_id, aciklama):
        self.cursor.execute("""
            UPDATE Program 
            SET Aciklama = ?
            WHERE ProgramID = ?
        """, (aciklama, program_id))
        self.conn.commit()

    def program_yil_degis(self, program_id, yil):
        self.cursor.execute("""  
            UPDATE Program
            SET YayinYili = ?
            WHERE ProgramID = ?
       """, (yil, program_id))
        self.conn.commit()

    def kullanicilari_listele(self):
        self.cursor.execute("SELECT Ad, Soyad, KullaniciID FROM Kullanici")
        satirlar = self.cursor.fetchall()
        kullanicilar = []

        for satir in satirlar:
            kullanicilar.append({
                "Ad": satir[0],
                "Soyad": satir[1],
                "KullaniciID": satir[2]
            })
        return kullanicilar

    def en_cok_izlenen(self):
        self.cursor.execute("""
            SELECT  TOP 10
                p.ProgramAdi,
                COUNT(i.İzlemeID) AS OynatilmaSayisi
            FROM Program
            LEFT JOIN IzlemeLog i ON p.ProgramID = i.ProgramID
            GROUP BY p.ProgramAdi
            ORDER BY OynatilmaSayisi DESC
        """)
        satirlar = self.cursor.fetchall()
        filmler = []

        for satir in satirlar:
            filmler.append({
                "ProgramAdi": satir[0],
                "IzlenmeSayisi": satir[1]
            })
        return filmler

    def en_yuksek_puanli(self):
        self.cursor.execute("""
            SELECT TOP 10
                p.ProgramAdi,
                ISNULL(AVG(CAST(kp.Puan AS Float)), 0) AS OrtalamaPuan
            FROM Program p 
            LEFT JOIN KullaniciProgram kp ON p.ProgramID = kp.ProgramID
            GROUP BY ProgramAdi, p.ProgramID
            ORDER BY OrtalamaPuan DESC
        """)
        satirlar = self.cursor.fetchall()
        filmler = []

        for satir in satirlar:
            filmler.append({
                "ProgramAdi": satir[0],
                "Puan": round(satir[1], 1)
            })
        return filmler

    def en_cok_izlenen_turler(self):
        self.cursor.execute("""
            SELECT TOP 3
                t.TurAdi,
                COUNT(i.IzlemeID) AS OynatilmaSayisi
            FROM Program p
            INNER JOIN IzlemeLog i ON p.ProgramID = i.ProgramID
            INNER JOIN ProgramTur pt ON p.ProgramID = pt.ProgramID
            INNER JOIN Tur t ON pt.TurID = t.TurID
            GROUP BY TurAdi
            ORDER BY OynatilmaSayisi DESC
        """)
        satirlar = self.cursor.fetchall()
        turler = []

        for satir in satirlar:
            turler.append({
                "TurAdi": satir[0],
                "OynatilmaSayisi": satir[1]
            })
        return turler

    def toplam_izlenme(self):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM IzlemeLog
        """)
        return self.cursor.fetchone()[0]

    def toplam_puan(self):
        self.cursor.execute("""
            SELECT COUNT(Puan)
            FROM KullaniciProgram
        """)
        return self.cursor.fetchone()[0]

    def toplam_icerik(self):
        self.cursor.execute("""
            SELECT COUNT(ProgramID)
            FROM Program
        """)
        return self.cursor.fetchone()[0]

    def toplam_izlenen_sure(self):
        self.cursor.execute("""
            SELECT ISNULL(SUM(IzlenenSure), 0)
            FROM IzlemeLog
        """)
        return self.cursor.fetchone()[0]

    def aktif_kullanicilar(self):
        self.cursor.execute("""
            SELECT TOP 5
                k.Ad,
                k.Soyad,
                COUNT(OturumID) AS GirisSayisi
            FROM Kullanici k 
            INNER JOIN OturumLog ol ON k.KullaniciID = ol.KullaniciID
            GROUP BY k.Ad, k.Soyad, k.KullaniciID
            ORDER BY GirisSayisi DESC
        """)
        satirlar = self.cursor.fetchall()
        kullanicilar = []

        for satir in satirlar:
            kullanicilar.append({
                "Ad": satir[0],
                "Soyad": satir[1],
                "GirisSayisi": satir[2]
            })
        return kullanicilar

if __name__ == "__main__":
    db = DataBaseManager()
    db.connect()
    db.disconnect()
