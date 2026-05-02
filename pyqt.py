import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QMessageBox, QStackedWidget
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import pyodbc

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=NetflixLikeAppDb;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

class Baslangic_Pencere(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Netflix Giriş Ekranı")
        self.setFixedSize(625, 625)
        self.setStyleSheet("background-color: black;")

        self.stack = QStackedWidget(self)
        self.stack.setFixedSize(625, 625)

        self.baslangic = BaslangicEkrani(self)
        self.giris = GirisEkrani(self)
        self.kayit = KayitEkrani(self)

        self.stack.addWidget(self.baslangic)
        self.stack.addWidget(self.giris)
        self.stack.addWidget(self.kayit)

        self.stack.setCurrentIndex(0)

    def ekran_goster(self, index):
        self.stack.setCurrentIndex(index)

class BaslangicEkrani(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana

        self.setStyleSheet("""
            QWidget { background-color: black; }
            QPushButton {
                background-color: red;
                color: white;
                border-radius: 4px;
                padding: 9px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #f40612; }
            QComboBox {
                background-color: grey;
                color: white;
                border-radius: 4px;
                padding: 9px;
                font-size: 16px;
            }
        """)

        layout = QVBoxLayout(self)

        self.label = QLabel("NETFLIX")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Press Start 2P", 36, QFont.Bold))
        self.label.setStyleSheet("color: red;")

        self.secim = QComboBox()
        self.secim.addItems(["Üye Girişi", "Hesap Aç"])
        self.secim.setFixedHeight(36)

        self.devam_buton = QPushButton("Devam Et")
        self.devam_buton.setFixedHeight(49)
        self.devam_buton.clicked.connect(self.devam_et)

        layout.addStretch()
        layout.addWidget(self.label)
        layout.addSpacing(36)
        layout.addWidget(self.secim)
        layout.addSpacing(9)
        layout.addWidget(self.devam_buton)
        layout.addStretch()

        layout.setContentsMargins(100, 0, 100, 0)

    def devam_et(self):
        if self.secim.currentText() == "Üye Girişi":
            self.ana.ekran_goster(1)
        else:
            self.ana.ekran_goster(2)

class GirisEkrani(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana

        self.setStyleSheet("""
            QWidget { background-color: black; }
            QLabel { color: white; }
            QLineEdit {
                background-color: grey;
                color: white;
                border: 1px solid grey;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: red;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: red; }
            QPushButton#geri {
                background-color: #6B2414;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 0, 100, 0)

        baslik = QLabel("Giriş Yap")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Press Start 2P", 20, QFont.Bold))
        baslik.setStyleSheet("color: white;")

        self.mail = QLineEdit()
        self.mail.setPlaceholderText("e-mail:")
        self.mail.setFixedHeight(49)

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("şifre:")
        self.sifre.setEchoMode(QLineEdit.Password)
        self.sifre.setFixedHeight(49)

        self.giris_buton = QPushButton("Giriş Yap")
        self.giris_buton.setFixedHeight(49)
        self.giris_buton.clicked.connect(self.giris_yap)

        self.geri_buton = QPushButton("Geri")
        self.geri_buton.setObjectName("geri")
        self.geri_buton.setFixedHeight(40)
        self.geri_buton.clicked.connect(lambda: self.ana.ekran_goster(0))

        layout.addStretch()
        layout.addWidget(baslik)
        layout.addSpacing(25)
        layout.addWidget(self.mail)
        layout.addSpacing(9)
        layout.addWidget(self.sifre)
        layout.addSpacing(16)
        layout.addWidget(self.giris_buton)
        layout.addSpacing(9)
        layout.addWidget(self.geri_buton)
        layout.addStretch()

    def giris_yap(self):
        email = self.mail.text().strip()
        sifre = self.sifre.text().strip()

        if not email or not sifre:
            QMessageBox.warning(self, "E-posta ve şifre boş olamaz!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT KullaniciID FROM Kullanici WHERE Email = ? AND Sifre = ?",
                (email, sifre)
            )
            kullanici = cursor.fetchone()
            conn.close()

            if kullanici:
                QMessageBox.information(self, "Giriş yapıldı!")
            else:
                QMessageBox.warning(self, "E-posta veya şifre yanlış!")
        except Exception as e:
            QMessageBox.critical(self, "Bağlantı Hatası", str(e))

class KayitEkrani(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana

        self.setStyleSheet("""
            QWidget { background-color: black; }
            QLabel { color: white; }
            QLineEdit {
                background-color: grey;
                color: white;
                border: 1px solid grey;
                border-radius: 4px;
                padding: 9px;
                font-size: 16px;
            }
            QPushButton {
                background-color: red;
                color: white;
                border-radius: 4px;
                padding: 9px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6B2414 ; }
            QPushButton#geri {
                background-color: #63190A;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(100, 0, 100, 0)

        baslik = QLabel("Hesap Oluştur")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Press Start 2P", 20, QFont.Bold))
        baslik.setStyleSheet("color: white;")

        self.mail = QLineEdit()
        self.mail.setPlaceholderText("E-mail giriniz")
        self.mail.setFont(QFont("Press Start 2P", 20, QFont.Bold))
        self.mail.setFixedHeight(49)

        self.sifre = QLineEdit()
        self.sifre.setPlaceholderText("Şifre giriniz")
        self.sifre.setFont(QFont("Press Start 2P", 20, QFont.Bold))
        self.sifre.setEchoMode(QLineEdit.Password)
        self.sifre.setFixedHeight(49)

        self.sifre2 = QLineEdit()
        self.sifre2.setPlaceholderText("Şifreyi tekrar giriniz")
        self.sifre2.setFont(QFont("Press Start 2P", 20, QFont.Bold))
        self.sifre2.setEchoMode(QLineEdit.Password)
        self.sifre2.setFixedHeight(49)

        self.kayit_buton = QPushButton("Kayıt ol")
        self.kayit_buton.setFont(QFont("Press Start 2P", 20, QFont.Bold))
        self.kayit_buton.setFixedHeight(49)
        self.kayit_buton.clicked.connect(self.kayit_ol)

        self.geri_buton = QPushButton("Geri")
        self.geri_buton.setObjectName("geri")
        self.geri_buton.setFixedHeight(36)
        self.geri_buton.clicked.connect(lambda: self.ana.ekran_goster(0))

        layout.addStretch()
        layout.addWidget(baslik)
        layout.addSpacing(25)
        layout.addWidget(self.mail)
        layout.addSpacing(9)
        layout.addWidget(self.sifre)
        layout.addSpacing(9)
        layout.addWidget(self.sifre2)
        layout.addSpacing(16)
        layout.addWidget(self.kayit_buton)
        layout.addSpacing(9)
        layout.addWidget(self.geri_buton)
        layout.addStretch()

    def kayit_ol(self):
        email = self.mail.text().strip()
        sifre = self.sifre.text().strip()
        sifre2 = self.sifre2.text().strip()

        if not email or not sifre:
            QMessageBox.warning(self, "E-mail ve şifre boş olamaz.")
            return

        if sifre != sifre2:
            QMessageBox.warning(self, "Şifre eşleşmiyor.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO Kullanici (RolID, Ad, Soyad, Ulke, Email, Sifre) VALUES (1, ?, ?, ?, ?, ?)",
                ("Ad", "Soyad", "Türkiye", email, sifre)
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Hesap oluşturuldu.")
            self.ana.ekran_goster(1)
        except pyodbc.IntegrityError:
            QMessageBox.warning(self, "Bu e-mail zaten kayıtlı!")
        except Exception as e:
            QMessageBox.critical(self, "Bağlantı Hatası", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = Baslangic_Pencere()
    pencere.show()
    sys.exit(app.exec_())