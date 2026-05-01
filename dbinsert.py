import pandas as pd
import pyodbc

server = 'localhost'
database = 'NetflixLikeAppDb'
driver = "{ODBC Driver 18 for SQL Server}"

conn_str = (
    f"Driver={driver};"
    f"Server={server};"
    f"Database={database};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)

#Dbye filmleri ekleyen fonksiyon.
try :
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Bağlantı tamamlandı.")
    eklenen_program_sayisi = 0

    df = pd.read_excel("Netflix_DB_Dolu.xlsx")

    for index, row in df.iterrows():
        program_adi = str(row["ProgramAdi"])
        tip = str(row["Tip"])
        aciklama = str(row["Aciklama"])
        yayin_yili = int(row["YayinYili"])
        bolum_sayisi = int(row["BolumSayisi"])
        turler = str(row["Turler"]).split(",")

        cursor.execute("""
            INSERT INTO Program(ProgramAdi, Tip, Aciklama, YayinYili, BolumSayisi)
            OUTPUT INSERTED.ProgramID
            VALUES (?, ?, ?, ?, ?)
        """, (program_adi, tip, aciklama, yayin_yili, bolum_sayisi))

        program_id = cursor.fetchone()[0]

        for tur in turler:
            tur_adi = tur.strip()
            if tur_adi == "":
                continue

            cursor.execute("SELECT TurID From Tur WHERE TurAdi = ?", (tur_adi,))
            tur_kaydi = cursor.fetchone()

            if tur_kaydi:
                tur_id = tur_kaydi[0]
            else:
                cursor.execute("""
                    INSERT INTO Tur (TurAdi)
                    OUTPUT INSERTED.TurID
                    VALUES (?)
                """, (tur_adi,))
                tur_id = cursor.fetchone()[0]

            try:
                cursor.execute("""
                    INSERT INTO ProgramTur (ProgramID, TurID)
                    VALUES (?, ?)
                """, (program_id, tur_id))
            except pyodbc.IntegrityError:
                pass
        eklenen_program_sayisi += 1
    conn.commit()
    print(f"Başarılı {eklenen_program_sayisi} program eklendi.")
except Exception as e:
    print(f"Bağlantı kurulamadı. Hata kodu{e}")
finally:
    if "cursor" in locals():
        cursor.close()
    if "conn" in locals():
        conn.close()

#Dbye rolleri ekleyen fonksiyon. Db arayüzünden de yapabilirsin burdan yapcaksan ctrl k crtl u yap bütün bölüme yorumdan çıksı yukardaki fonksiyonu da aynı şekilde yoruma al
# try:
#     conn = pyodbc.connect(conn_str)
#     cursor = conn.cursor()
#
#     a = "Kullanıcı"
#     b = "Yönetici"
#
#     cursor.execute("INSERT INTO Rol(RolAdi) VALUES (?)", (a,))
#     cursor.execute("INSERT INTO Rol(RolAdi) VALUES (?)",(b))
#     print("Tamamlandı")
#     conn.commit()
#
#     cursor.close()
#     conn.close()
# except Exception as e:
#     print(f"Hata: {e}")
