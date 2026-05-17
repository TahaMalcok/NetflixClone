import sys
import re
from datetime import datetime
import time
from PyQt5.QtCore import Qt, QTimer
import pyodbc
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QMessageBox, QStackedWidget, QCheckBox, QScrollArea,
    QFrame, QGridLayout, QDialog, QSpinBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from dbmanager import DataBaseManager

DIZAYN = """
QWidget { background-color: black; color: white; font-family: "Press Start 2P"; }
QDialog { background-color: black; font-family: Press Start 2P;}
QLineEdit {
    background-color: #222; color: white;
    border: 1px solid #444; border-radius: 4px;
    padding: 9px; font-size: 16px;
}
QLineEdit:focus { border: 1px solid red; }
QPushButton {
    background-color: red; color: white;
    border-radius: 4px; padding: 9px;
    font-size: 16px; font-weight: bold;
}
QPushButton:hover { background-color: #cc0000; }
QPushButton#ikincil { background-color: #333; font-size: 16px; }
QPushButton#ikincil:hover { background-color: #444; }
QComboBox {
    background-color: #222; color: white;
    border: 1px solid #444; border-radius: 4px;
    padding: 9px; font-size: 16px;
}
QComboBox QAbstractItemView {
    background-color: #222; color: white;
    selection-background-color: #444;
}
QCheckBox { color: white; font-size: 16px; }
QLabel { color: white; }
QScrollBar:vertical { background: #111; width: 9px; }
QScrollBar::handle:vertical { background: #444; border-radius: 4px; }
QSpinBox {
    background-color: #222; color: white;
    border: 1px solid #444; border-radius: 4px;
    padding: 6px; font-size: 16px;
}
"""

def _alan(placeholder, sifre=False, yukseklik=49):
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setFixedHeight(yukseklik)
    if sifre:
        w.setEchoMode(QLineEdit.Password)
    return w

class AnaPencere(QWidget):
    def __init__(self):
        super().__init__()
        self.db = DataBaseManager()
        self.db.connect()
        self.aktif_kullanici = None
        self.setWindowTitle("Netflix")
        self.setFixedSize(960, 720)

        self.setStyleSheet('background-color: black; color: white; font-family: "Press Start 2P";')

        self.stack = QStackedWidget(self)
        self.stack.setFixedSize(960, 720)

        self.giris_ekrani = GirisEkrani(self)
        self.kayit_ekrani = KayitEkrani(self)
        self.oneri_ekrani = OneriEkrani(self)
        self.ana_sayfa = AnaSayfa(self)
        self.profil_ekrani = ProfilEkrani(self)
        self.admin_panel = AdminPanel(self)

        for ekran in [
            self.giris_ekrani,
            self.kayit_ekrani,
            self.oneri_ekrani,
            self.ana_sayfa,
            self.profil_ekrani,
            self.admin_panel
        ]:
            self.stack.addWidget(ekran)

            ana_layout = QVBoxLayout(self)
            ana_layout.setContentsMargins(0, 0, 0, 0)
            ana_layout.addWidget(self.stack)

            self.stack.setCurrentIndex(0)

    def ekran_goster(self, index):
        self.stack.setCurrentIndex(index)

    def closeEvent(self, event):
        self.db.disconnect()
        event.accept()

class GirisEkrani(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana
        self.setStyleSheet(DIZAYN)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(225, 0, 225, 0)

        baslik = QLabel("NETFLIX")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Press Start 2P", 38, QFont.Bold))
        baslik.setStyleSheet("color: red; margin-bottom: 30px;")

        self.mail = _alan("Mail")
        self.sifre = _alan("Şifre", sifre=True)

        giris_btn = QPushButton("Giriş Yap")
        giris_btn.setFixedHeight(49)
        giris_btn.clicked.connect(self._giris)

        kayit_btn = QPushButton("Kayıt Ol")
        kayit_btn.setObjectName("ikincil")
        kayit_btn.setFixedHeight(40)
        kayit_btn.clicked.connect(lambda: self.ana.ekran_goster(1))

        yonetici_btn = QPushButton("Yönetici Girişi")
        yonetici_btn.setFixedHeight(49)
        yonetici_btn.clicked.connect(self._yonetici_giris)

        layout.addStretch()
        layout.addWidget(baslik)
        layout.addSpacing(10)
        layout.addWidget(QLabel("Mail"))
        layout.addWidget(self.mail)
        layout.addSpacing(9)
        layout.addWidget(QLabel("Şifre"))
        layout.addWidget(self.sifre)
        layout.addSpacing(16)
        layout.addWidget(giris_btn)
        layout.addSpacing(9)
        layout.addWidget(yonetici_btn)
        layout.addSpacing(9)
        layout.addWidget(kayit_btn)
        layout.addStretch()

    def _giris(self):
        email = self.mail.text().strip()
        sifre = self.sifre.text().strip()

        if not email or not sifre:
            QMessageBox.warning(self, "", "Mail ve şifre boş olamaz.")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            QMessageBox.warning(self, "", "Geçerli bir mail adresi girin.")
            return
        kullanici = self.ana.db.giris_yap(email, sifre)

        if kullanici:
            self.ana.aktif_kullanici = kullanici
            self.ana.ana_sayfa.icerikleri_yukle()
            self.ana.ekran_goster(3)
            self.mail.clear()
            self.sifre.clear()
        else:
            QMessageBox.warning(self, "", "Mail veya şifre yanlış.")

    def _yonetici_giris(self):
        email = self.mail.text().strip()
        sifre = self.sifre.text().strip()

        if not sifre or not email:
            QMessageBox.warning(self, "", "Mail veya şifre boş olamaz.")
            return

        kullanici = self.ana.db.giris_yap(email, sifre)

        if kullanici and kullanici[1] == 2:
            self.ana.aktif_kullanici = kullanici
            self.ana.ana_sayfa.icerikleri_yukle()
            self.ana.admin_panel.yukle()
            self.ana.ekran_goster(5)
            self.mail.clear()
            self.sifre.clear()
        elif kullanici:
            QMessageBox.warning(self, "Yetkisiz", "Yönetici yetkiniz yok.")
        else:
            QMessageBox.warning(self, "Hata", "Mail veya şifre yanlış.")

class KayitEkrani(QWidget):
    TUR_LISTESI = [
        "Aksiyon ve Macera", "Komedi", "Drama", "Korku", "Belgesel",
        "Romantik", "Bilim Kurgu ve Fantastik Yapımlar", "Anime", "Suç", "Gerilim"
    ]

    def __init__(self, ana):
        super().__init__()
        self.ana = ana
        self.setStyleSheet(DIZAYN)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll.setFixedSize(960, 720)

        icerik = QWidget()
        icerik.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(icerik)
        layout.setContentsMargins(256, 36, 256, 36)
        layout.setSpacing(6)

        baslik = QLabel("Hesap oluştur")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Press Start 2P", 24, QFont.Bold))
        baslik.setStyleSheet("color: red; margin-bottom: 16px;")
        layout.addWidget(baslik)

        self.ad = _alan("Ad")
        self.soyad = _alan("Soyad")
        self.mail = _alan("Mail")
        self.sifre = _alan("Şifre", sifre=True)
        self.sifre2 = _alan("Şifre Tekrar", sifre=True)
        self.dogum = _alan("Doğum Tarihi (Gün/Ay/Yıl)")
        self.ulke = _alan("Ülke")

        self.cinsiyet = QComboBox()
        self.cinsiyet.addItems(["Seçiniz", "Erkek", "Kadın", "Belirtmek istemiyorum"])
        self.cinsiyet.setFixedHeight(45)

        for etiket, widget in [
            ("Ad", self.ad), ("Soyad", self.soyad),
            ("Mail", self.mail), ("Şifre", self.sifre),
            ("Şifre Tekrar", self.sifre2),
            ("Doğum Tarihi", self.dogum),
            ("Cinsiyet", self.cinsiyet),
            ("Ülke", self.ulke),
        ]:
            layout.addWidget(QLabel(etiket))
            layout.addWidget(widget)
            layout.addSpacing(4)

        tur_lbl = QLabel("3 Favori Tür Seçin")
        tur_lbl.setStyleSheet("color: red; font-weight: bold; font-size: 15px; margin-top: 9px;")
        layout.addWidget(tur_lbl)

        self.tur_checkboxlar = []
        for tur in self.TUR_LISTESI:
            cb = QCheckBox(tur)
            cb.stateChanged.connect(self._tur_kontrol)
            self.tur_checkboxlar.append(cb)
            layout.addWidget(cb)

        layout.addSpacing(12)

        kayit_btn = QPushButton("Kayıt ol")
        kayit_btn.setFixedHeight(49)
        kayit_btn.clicked.connect(self._kayit)
        layout.addWidget(kayit_btn)

        geri_btn = QPushButton("Geri")
        geri_btn.setObjectName("ikincil")
        geri_btn.setFixedHeight(40)
        geri_btn.clicked.connect(lambda: self.ana.ekran_goster(0))
        layout.addWidget(geri_btn)

        scroll.setWidget(icerik)

    def _tur_kontrol(self):
        secili = [cb for cb in self.tur_checkboxlar if cb.isChecked()]
        if len(secili) > 3:
            self.sender().setChecked(False)

    def _kayit(self):
        ad = self.ad.text().strip()
        soyad = self.soyad.text().strip()
        mail = self.mail.text().strip()
        sifre = self.sifre.text().strip()
        sifre2 = self.sifre2.text().strip()
        dogum = self.dogum.text().strip()
        ulke = self.ulke.text().strip()
        cinsiyet = self.cinsiyet.currentText()
        turler = [cb.text() for cb in self.tur_checkboxlar if cb.isChecked()]

        if not all([ad, soyad, mail, sifre, sifre2, dogum, ulke]):
            QMessageBox.warning(self, "Tüm alanları doldurun.");
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", mail):
            QMessageBox.warning(self, "", "Geçerli bir mail girin.");
            return
        if sifre != sifre2:
            QMessageBox.warning(self, "", "Şifreler eşleşmiyor.");
            return
        if cinsiyet == "Seçiniz":
            QMessageBox.warning(self, "", "Cinsiyet seçin.");
            return
        if len(turler) != 3:
            QMessageBox.warning(self, "", "Tam 3 tür seçin.");
            return

        try:
            dt = datetime.strptime(dogum, "%d/%m/%Y")
            if dt >= datetime.today():
                QMessageBox.warning(self, "Doğum tarihi bugünden büyük olamaz.");
                return
            dogum_str = dt.strftime("%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Tarih Gün/Ay/Yıl formatında olmalı.");
            return

        sonuc = self.ana.db.kayit_yap(ad, soyad, mail, sifre, dogum_str, cinsiyet, ulke, turler)

        if sonuc == "Kayıt başarılı.":
            QMessageBox.information(self, "Başarılı", sonuc)
            kullanici = self.ana.db.giris_yap(mail, sifre)
            if kullanici:
                self.ana.aktif_kullanici = kullanici
                self.ana.ana_sayfa.icerikleri_yukle()
                self.ana.ekran_goster(3)
        else:
            QMessageBox.warning(self, "Uyarı", str(sonuc))

class OneriEkrani(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana
        self.setStyleSheet(DIZAYN)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)

        baslik = QLabel("Sana Özel Öneriler")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Press Start 2P", 18, QFont.Bold))
        baslik.setStyleSheet("color: red; margin-bottom: 10px;")
        layout.addWidget(baslik)

        self.alt_baslik = QLabel("")
        self.alt_baslik.setAlignment(Qt.AlignCenter)
        self.alt_baslik.setStyleSheet("color: #aaa; font-size: 13px;")
        layout.addWidget(self.alt_baslik)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        self.icerik = QWidget()
        self.icerik_layout = QVBoxLayout(self.icerik)
        self.icerik_layout.setSpacing(10)
        scroll.setWidget(self.icerik)
        layout.addWidget(scroll)

        devam_btn = QPushButton("Ana Sayfaya Git")
        devam_btn.setFixedHeight(48)
        devam_btn.clicked.connect(self._ana_sayfaya)
        layout.addWidget(devam_btn)

    def _ana_sayfaya(self):
        self.ana.ana_sayfa.icerikleri_yukle()
        self.ana.ekran_goster(3)

    def onerileri_yukle(self, oneriler, turler):
        for i in reversed(range(self.icerik_layout.count())):
            w = self.icerik_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        self.alt_baslik.setText(f"Seçtiğin türler: {', '.join(turler)}")

        if not oneriler:
            lbl = QLabel("Henüz öneri yok.")
            lbl.setStyleSheet("color: #aaa; font-size: 14px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.icerik_layout.addWidget(lbl)
            return

        for tur_adi, filmler in oneriler.items():
            for film in filmler:
                kart = QFrame()
                kart.setStyleSheet(
                    "QFrame { background-color: #1a1a1a; border: 1px solid #333;"
                    " border-radius: 9px; padding: 9px; }"
                )
                kl = QVBoxLayout(kart)
                t = QLabel(tur_adi)
                t.setStyleSheet("color: red; font-size: 12px; font-weight: bold;")
                program_adi = film.get("ProgramAdi")
                a = QLabel(str(program_adi) if program_adi else "İsimsiz İçerik")
                a.setFont(QFont("Press Start 2P", 11, QFont.Bold))
                b = QLabel(
                    f"{film.get('Tip', '')}  •  {film.get('YayinYili', '')}  •  ⭐ {film.get('OrtalamaPuan', 0)}/10")
                b.setStyleSheet("color: #aaa; font-size: 12px;")
                kl.addWidget(t);
                kl.addWidget(a);
                kl.addWidget(b)
                self.icerik_layout.addWidget(kart)

class AnaSayfa(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana
        self.setStyleSheet(DIZAYN)
        self.tum_icerikler = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        ust = QWidget()
        ust.setFixedHeight(64)
        ust.setStyleSheet("background-color: #111; border-bottom: 1px solid #222;")
        ul = QHBoxLayout(ust)
        ul.setContentsMargins(25, 0, 25, 0)

        logo = QLabel("NETFLIX")
        logo.setFont(QFont("Press Start 2P", 22, QFont.Bold))
        logo.setStyleSheet("color: red;")

        self.arama = QLineEdit()
        self.arama.setPlaceholderText("İçerik ara.")
        self.arama.setFixedSize(200, 36)
        self.arama.textChanged.connect(self._filtrele)

        self.tip_filtre = QComboBox()
        self.tur_filtre = QComboBox()
        self.tur_filtre.addItems([
            "Tüm Türler",
            "Aksiyon ve Macera",
            "Komedi",
            "Drama",
            "Korku",
            "Belgesel",
            "Romantik",
            "Bilim Kurgu ve Fantastik Yapımlar",
            "Anime",
            "Suç",
            "Gerilim"
        ])
        self.tur_filtre.setFixedSize(220, 36)
        self.tip_filtre.addItems(["Tümü", "Film", "Dizi"])
        self.tip_filtre.setFixedSize(100, 36)
        self.tur_filtre.currentTextChanged.connect(self._filtrele)

        profil_btn = QPushButton("Profil")
        self.admin_btn = QPushButton("Yönetici")
        self.admin_btn.setObjectName("ikincil")
        self.admin_btn.setFixedSize(110, 36)
        self.admin_btn.clicked.connect(
            lambda: self.ana.ekran_goster(5)
        )

        self.admin_btn.hide()
        profil_btn.setObjectName("ikincil")
        profil_btn.setFixedSize(90, 36)
        profil_btn.clicked.connect(self._profile_git)

        cikis_btn = QPushButton("Çıkış")
        cikis_btn.setObjectName("ikincil")
        cikis_btn.setFixedSize(70, 36)
        cikis_btn.clicked.connect(self._cikis)

        oneri_btn = QPushButton("Öneriler")
        oneri_btn.setObjectName("ikincil")
        oneri_btn.setFixedSize(100, 36)

        oneri_btn.clicked.connect(self._onerilere_git)

        self.favori_modu = False
        self.fav_ekran_btn = QPushButton("Favoriler")
        self.fav_ekran_btn.setObjectName("İkincil")
        self.fav_ekran_btn.setFixedSize(140, 36)
        self.fav_ekran_btn.clicked.connect(self._favori_ekran)

        ul.addWidget(logo)
        ul.addStretch()
        ul.addWidget(self.arama)
        ul.addSpacing(8)
        ul.addWidget(self.tip_filtre)
        ul.addSpacing(8)
        ul.addWidget(profil_btn)
        ul.addWidget(self.admin_btn)
        ul.addSpacing(6)
        ul.addWidget(oneri_btn)
        ul.addSpacing(6)
        ul.addWidget(self.fav_ekran_btn)
        ul.addWidget(cikis_btn)
        ul.addWidget(self.tur_filtre)

        layout.addWidget(ust)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: black;")
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet("background-color: black;")
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(25, 25, 25, 25)
        scroll.setWidget(self.grid_widget)
        layout.addWidget(scroll)

    def _onerilere_git(self):
        oneriler = self.ana.db.oneri(self.ana.aktif_kullanici[0])
        turler = self.ana.db.kullanici_turleri(self.ana.aktif_kullanici[0])
        self.ana.oneri_ekrani.onerileri_yukle(oneriler, turler)
        self.ana.ekran_goster(2)

    def _cikis(self):
        self.ana.aktif_kullanici = None
        self.ana.ekran_goster(0)

    def _favori_ekran(self):
        kullanici_id = self.ana.aktif_kullanici[0]

        if not self.favori_modu:
            self.favori_modu = True
            self.fav_ekran_btn.setText("Tüm İçerikler")
            self.fav_ekran_btn.setStyleSheet("color: red; border: 1px solid red;")
            fav_listesi = self.ana.db.favori_listele(kullanici_id)
            self._kartlari_goster(fav_listesi)
        else:
            self.favori_modu = False
            self.fav_ekran_btn.setText("Favoriler")
            self.fav_ekran_btn.setStyleSheet("")
            self.icerikleri_yukle()

    def _profile_git(self):
        self.ana.profil_ekrani.yukle()
        self.ana.ekran_goster(4)

    def icerikleri_yukle(self):
        if self.ana.aktif_kullanici[1] == 2:
            self.admin_btn.show()
        else:
            self.admin_btn.hide()
        self.tum_icerikler = self.ana.db.tum_programlari_listele()
        self._kartlari_goster(self.tum_icerikler)

    def _filtrele(self):
        arama = self.arama.text().strip().lower()
        tip = self.tip_filtre.currentText()
        secilen_tur = self.tur_filtre.currentText()
        kullanici_id = self.ana.aktif_kullanici[0]
        ana_liste = self.ana.db.favori_listele(kullanici_id) if self.favori_modu else self.tum_icerikler
        sonuc = []
        for row in ana_liste:
            if arama and arama not in str(row.get("ProgramAdi", "")).lower():
                continue

            if tip != "Tümü" and tip != str(row.get("Tip", "")):
                continue

            film_turleri = str(row.get("Turler", ""))
            if secilen_tur != "Tüm Türler" and secilen_tur not in film_turleri:
                continue
            sonuc.append(row)

        self._kartlari_goster(sonuc)

    def _kartlari_goster(self, liste):
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w: w.deleteLater()

        sutun = 4
        if not liste:
            lbl = QLabel("İçerik bulunamadı.")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #aaa; font-size: 16px;")
            self.grid_layout.addWidget(lbl, 0, 0, 1, sutun)
            return

        for idx, row in enumerate(liste):
            kart = self._kart_olustur(row)
            self.grid_layout.addWidget(kart, idx // sutun, idx % sutun)

    def _kart_olustur(self, row):
        program_id = row.get("ProgramID")
        ad = str(row.get("ProgramAdi", ""))
        tip = str(row.get("Tip", ""))
        yil = str(row.get("YayinYili", ""))
        turler = str(row.get("Turler", ""))
        ort_puan = row.get("OrtalamaPuan", 0.0)

        kart = QFrame()
        kart.setFixedSize(210, 200)
        kart.setCursor(Qt.PointingHandCursor)
        kart.setStyleSheet(
            "QFrame { background-color: #1a1a1a; border: 1px solid #333; border-radius: 9px; }"
            "QFrame:hover { border: 2px solid red; background-color: #222; }"
        )

        kl = QVBoxLayout(kart)
        kl.setContentsMargins(10, 10, 10, 10)
        kl.setSpacing(4)

        tip_renk = "#E50914" if tip == "Film" else "#1DB954"
        tip_lbl = QLabel(tip)
        tip_lbl.setFixedWidth(45)
        tip_lbl.setAlignment(Qt.AlignCenter)
        tip_lbl.setStyleSheet(
            f"background-color: {tip_renk}; color: white; border-radius: 4px;"
            " padding: 2px 4px; font-size: 9px; font-weight: bold;"
        )

        ad_lbl = QLabel(ad)
        ad_lbl.setFont(QFont("Press Start 2P", 9, QFont.Bold))
        ad_lbl.setWordWrap(True)
        ad_lbl.setStyleSheet("color: white;")

        yil_lbl = QLabel(yil)
        yil_lbl.setStyleSheet("color: #aaa; font-size: 11px;")

        tur_lbl = QLabel(turler)
        tur_lbl.setStyleSheet("color: #aaa; font-size: 11px;")

        puan_lbl = QLabel(f"⭐ {ort_puan}/10")
        puan_lbl.setStyleSheet("color: #aaa; font-size: 10px;")

        kl.addWidget(tip_lbl)
        kl.addWidget(ad_lbl)
        kl.addWidget(yil_lbl)
        kl.addWidget(tur_lbl)
        kl.addStretch()
        kl.addWidget(puan_lbl)

        kart.mousePressEvent = lambda e, r=row: self._detay_ac(r)
        return kart

    def _detay_ac(self, row):
        dlg = DetayDialog(row, self.ana.aktif_kullanici[0], self.ana.db, self.ana.aktif_kullanici[1], self)
        dlg.exec_()
        self.icerikleri_yukle()

class DetayDialog(QDialog):
    def __init__(self, row, kullanici_id, db, kullanici_rolu, parent=None):
        super().__init__(parent)
        self.kullanici_id = kullanici_id
        self.kullanici_rolu = kullanici_rolu
        self.program_id = row.get("ProgramID")
        self.program_adi = str(row.get("ProgramAdi", ""))
        self.db = db
        self.detay_verisi = self.db.detay(self.kullanici_id, self.program_id)

        self.setWindowTitle(self.program_adi)
        self.setFixedSize(580, 540)
        self.setStyleSheet("""
            QDialog  { background-color: #111; color: white; }
            QLabel   { color: white; }
            QPushButton {
                background-color: red; color: white;
                border-radius: 4px; padding: 9px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #cc0000; }
            QPushButton#ikincil { background-color: #333; }
            QPushButton#ikincil:hover { background-color: #444; }
            QLineEdit {
                background-color: #222; color: white;
                border: 1px solid #444; border-radius: 4px;
                padding: 6px; font-size: 14px;
            }
            QSpinBox {
                background-color: #222; color: white;
                border: 1px solid #444; border-radius: 4px;
                padding: 6px; font-size: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(8)

        baslik = QLabel(self.program_adi)
        baslik.setFont(QFont("Press Start 2P", 14, QFont.Bold))
        baslik.setWordWrap(True)
        layout.addWidget(baslik)

        layout.addWidget(QLabel(f"{row.get('Tip', '')}  •  {row.get('YayinYili', '')}"))
        ort_puan = round(float(row.get("OrtalamaPuan", 0) or 0), 1)
        self._satir(layout, "Bölüm Sayısı", str(row.get("BolumSayisi", "")))

        turler = self.detay_verisi.get("Turler", "")

        tur = QLabel(str(turler))
        tur.setStyleSheet("color: #ccc; font-size: 12px; margin-top: 6px;")
        layout.addWidget(tur)

        if self.detay_verisi:
            aciklama = self.detay_verisi.get("Aciklama", "")
            if aciklama and str(aciklama).strip():
                ac = QLabel(str(aciklama))
                ac.setWordWrap(True)
                ac.setStyleSheet("color: #ccc; font-size: 12px; margin-top: 6px;")
                layout.addWidget(ac)

        layout.addStretch()

        if self.kullanici_rolu == 2:
            admin_lbl = QLabel("Yönetici İşlemleri")
            admin_lbl.setStyleSheet("color: red; font-weight: bold; margin-top: 10px;")
            admin_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(admin_lbl)

            acik_lay = QHBoxLayout()
            self.acik_kutu = QLineEdit()
            self.acik_kutu.setPlaceholderText("Açıklama:")
            acik_btn = QPushButton("Açıklamayı Güncelle")
            acik_btn.clicked.connect(self._aciklama_guncelle)
            acik_lay.addWidget(self.acik_kutu)
            acik_lay.addWidget(acik_btn)
            layout.addLayout(acik_lay)

            yil_lay = QHBoxLayout()
            self.yil_kutu = QLineEdit()
            self.yil_kutu.setPlaceholderText("Yeni Yıl:")
            yil_btn = QPushButton("Yılı Güncelle")
            yil_btn.clicked.connect(self._yil_guncelle)
            yil_lay.addWidget(self.yil_kutu)
            yil_lay.addWidget(yil_btn)
            layout.addLayout(yil_lay)

            tur_lay = QHBoxLayout()
            self.tur_kutu = QLineEdit()
            self.tur_kutu.setPlaceholderText("Eklenecek Tür Adı:")
            tur_btn = QPushButton("Tür Ekle")
            tur_btn.clicked.connect(self._tur_ekle)
            tur_lay.addWidget(self.tur_kutu)
            tur_lay.addWidget(tur_btn)
            layout.addLayout(tur_lay)

            kapat_btn = QPushButton("Kapat")
            kapat_btn.setObjectName("ikincil")
            kapat_btn.setFixedHeight(44)
            kapat_btn.clicked.connect(self.close)
            layout.addWidget(kapat_btn)

        else:
            puan_lay = QHBoxLayout()
            self.puan_spin = QSpinBox()
            self.puan_spin.setRange(1, 10)
            self.puan_spin.setValue(5)
            self.puan_spin.setFixedHeight(40)
            puan_btn = QPushButton("Puanla")
            puan_btn.setFixedHeight(40)
            puan_btn.clicked.connect(self._puan_ver)
            puan_lay.addWidget(QLabel("Puan (1-10):"))
            puan_lay.addWidget(self.puan_spin)
            puan_lay.addWidget(puan_btn)
            layout.addLayout(puan_lay)

            btn_lay = QHBoxLayout()
            self.favorimi = self.detay_verisi.get("Favori", False)
            btn_txt = "Favoriden Çıkar" if self.favorimi else "Favoriye Ekle"
            self.fav_btn = QPushButton(btn_txt)
            self.fav_btn.setObjectName("ikincil")
            self.fav_btn.setFixedHeight(44)
            self.fav_btn.clicked.connect(self._favoriye_ekle)

            kapat_btn = QPushButton("Kapat")
            kapat_btn.setObjectName("ikincil")
            kapat_btn.setFixedHeight(44)
            kapat_btn.clicked.connect(self.close)

            izle_btn = QPushButton("İzle")
            izle_btn.setFixedHeight(44)
            izle_btn.clicked.connect(self._izleme_ekrani_ac)

            btn_lay.addWidget(izle_btn)
            btn_lay.addWidget(self.fav_btn)
            btn_lay.addWidget(kapat_btn)
            layout.addLayout(btn_lay)

    def _satir(self, layout, etiket, deger):
        h = QHBoxLayout()
        et = QLabel(etiket)
        et.setStyleSheet("color: #aaa; font-size: 12px; min-width: 130px;")
        dg = QLabel(deger)
        dg.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        h.addWidget(et);
        h.addWidget(dg);
        h.addStretch()
        layout.addLayout(h)

    def _favoriye_ekle(self):
        if self.favorimi:
            self.db.favori_silme(self.program_id, self.kullanici_id)
            self.favorimi = False
            self.fav_btn.setText("Favoriye Ekle")
            QMessageBox.information(self, "Bilgi", "Favorilerden çıkarıldı.")
        else:
            sonuc = self.db.favori_ekle(self.program_id, self.kullanici_id)
            if sonuc:
                QMessageBox.information(self, "Bilgi", str(sonuc))
            else:
                self.favorimi = True
                self.fav_btn.setText("Favoriden Çıkar")
                QMessageBox.information(self, "Bilgi", "Favorilere Eklendi")

    def _puan_ver(self):
        puan = self.puan_spin.value()
        sonuc = self.db.puanlama(self.kullanici_id, self.program_id, puan)
        QMessageBox.information(self, "Bilgi", str(sonuc))

    def _yil_guncelle(self):
        yeni_yil = self.yil_kutu.text().strip()
        if not yeni_yil.isdigit():
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir yıl giriniz.")
            return

        self.db.program_yil_degis(self.program_id, yeni_yil)
        QMessageBox.information(self, "Başarılı", "Yayın yılı güncellendi.")
        self.yil_kutu.clear()

    def _tur_ekle(self):
        yeni_tur = self.tur_kutu.text().strip()
        if not yeni_tur:
            QMessageBox.warning(self, "Hata", "Tür adı boş olamaz.")
            return

        sonuc = self.db.program_tur_ekle(yeni_tur, self.program_id)
        if sonuc:
            QMessageBox.warning(self, "Hata", str(sonuc))
        else:
            QMessageBox.information(self, "Başarılı", "Yeni tür başarıyla eklendi.")
            self.tur_kutu.clear()

    def _aciklama_guncelle(self):
        yeni_acik = self.acik_kutu.text().strip()
        if not yeni_acik:
            QMessageBox.warning(self, "Hata", "Açıklama boş olamaz.")
            return

        self.db.program_aciklama_degis(self.program_id, yeni_acik)
        QMessageBox.information(self, "Başarılı", "Açıklama başarıyla güncellendi")

    def _izleme_ekrani_ac(self):
        dlg = IzlemeDialog(
            self.detay_verisi,
            self.db,
            self
        )
        dlg.exec_()

class BolumOynatDialog(QDialog):
    def __init__(self, program_adi, bolum_no, sure, k_id, p_id, db, kalinan_sure=0,parent=None):
        super().__init__(parent)
        self.k_id = k_id
        self.p_id = p_id
        self.bolum_no = bolum_no
        self.db = db
        self.kaldigimiz_saniye = kalinan_sure * 60
        self.setWindowTitle("Bölüm Oynatılıyor")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog { background-color: black; color: white; }
            QLabel { color: white; }
            QPushButton {
                background-color: red; color: white; padding: 10px;
                border-radius: 5px; font-size: 14px; font-weight: bold;
            }
        """)
        layout = QVBoxLayout(self)

        baslik = QLabel(f"{program_adi}\n\nBölüm {bolum_no}")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Press Start 2P", 14, QFont.Bold))
        layout.addStretch()
        layout.addWidget(baslik)

        oynuyor = QLabel("Şu anda oynatılıyor.")
        oynuyor.setAlignment(Qt.AlignCenter)
        oynuyor.setStyleSheet("background-color: #111; border: 1px solid #333; padding: 40px; font-size: 18px;")
        layout.addWidget(oynuyor)

        self.izleme_lbl = QLabel(f"İzlenen Süre: {kalinan_sure} dk 0 sn")
        self.izleme_lbl.setAlignment(Qt.AlignCenter)
        self.izleme_lbl.setStyleSheet("color: red; font-size: 15px; font-weight: bold;")
        layout.addWidget(self.izleme_lbl)

        layout.addStretch()
        kapat_btn = QPushButton("Kapat")
        kapat_btn.clicked.connect(self.close)
        layout.addWidget(kapat_btn)

        self.baslama_zamani = time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._sure_guncelle)
        self.timer.start(1000)

    def _sure_guncelle(self):
        gecen_saniye_anlik = int(time.time() - self.baslama_zamani)
        gecen_sure = gecen_saniye_anlik + self.kaldigimiz_saniye
        dakika = gecen_sure // 60
        saniye = gecen_sure % 60

        if dakika == 0:
            self.izleme_lbl.setText(f"İzlenen Süre: {saniye} sn")
        else:
            self.izleme_lbl.setText(f"İzlenen Süre: {dakika} dk {saniye} sn")

    def closeEvent(self, event):
        self.timer.stop()
        gecen_saniye_anlik = int(time.time() - self.baslama_zamani)
        gecen_sure = gecen_saniye_anlik + self.kaldigimiz_saniye
        dakika = gecen_sure // 60

        kaydedilecek_dakika = 1 if (dakika == 0 and gecen_sure > 0) else dakika

        self.db.izleme_log(self.k_id, self.p_id, self.bolum_no, kaydedilecek_dakika)

        print(f"Bölüm kapatıldı. Veritabanına {kaydedilecek_dakika} dk izleme yazıldı.")
        event.accept()

class IzlemeDialog(QDialog):
    def __init__(self, veri, db, parent=None):
        super().__init__(parent)
        self.veri = veri
        self.db = db

        self.setWindowTitle("İzleme Ekranı")
        self.setFixedSize(600, 600)
        self.setStyleSheet("""
            QDialog { background-color: black; color: white; }
            QLabel { color: white; }
            QPushButton {
                background-color: red; color: white; padding: 10px;
                border-radius: 5px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #cc0000; }
        """)
        layout = QVBoxLayout(self)

        program_adi = veri.get("ProgramAdi", "")
        self.tip = veri.get("Tip", "")

        baslik = QLabel(program_adi)
        baslik.setFont(QFont("Press Start 2P", 16, QFont.Bold))
        baslik.setWordWrap(True)
        layout.addWidget(baslik)

        daha_once_izledimi = bool(self.veri.get("DahaOnceIzlediMi", False))
        bitti_mi = bool(self.veri.get("SonIzlemeBittiMi", False))
        ham_sure = self.veri.get("KalınanSure")
        self.kaldigimiz_dakika = int(ham_sure) if ham_sure is not None else 0

        if bitti_mi or daha_once_izledimi:
            self.kaldigimiz_dakika = 0
        self.kaldigimiz_saniye = self.kaldigimiz_dakika * 60

        if self.tip == "Film":
            self.izleme_lbl = QLabel(f"İzlenen Süre: {self.kaldigimiz_dakika} dk 0 sn")
            self.izleme_lbl.setStyleSheet("color: red; font-size: 15px; font-weight:bold;")
            layout.addWidget(self.izleme_lbl)
            layout.addSpacing(20)

            film_lbl = QLabel("Film izleniyor.")
            film_lbl.setAlignment(Qt.AlignCenter)
            film_lbl.setStyleSheet("background-color: #111; border: 1px solid #333; padding: 100px; font-size: 20px;")
            layout.addWidget(film_lbl)

            self.baslama_zamani = time.time()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._sure_guncelle)
            self.timer.start(1000)

        else:
            bolum_lbl = QLabel("Bölümler:")
            bolum_lbl.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
            layout.addWidget(bolum_lbl)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("border: none; background-color: #262525;")
            scroll_icerik = QWidget()
            scroll_layout = QVBoxLayout(scroll_icerik)
            scroll_layout.setSpacing(10)

            bolum_sayisi = int(veri.get("BolumSayisi") or 0)
            ham_bolum = self.veri.get("KalınanBolum")
            son_izlenen_bolum = int(ham_bolum) if ham_bolum is not None else 1

            for i in range(1, bolum_sayisi + 1):
                btn_txt = f"Bölüm {i}"

                if daha_once_izledimi and (i == son_izlenen_bolum) and not bitti_mi:
                    btn_txt += " (Kaldığın Yer)"

                bolum_btn = QPushButton(btn_txt)
                bolum_btn.setFixedHeight(45)
                kalinan = self.kaldigimiz_dakika if (i == son_izlenen_bolum and  daha_once_izledimi and not bitti_mi) else 0
                bolum_btn.clicked.connect(lambda _, x=i, k=kalinan: self._bolum_oynat(x, k))
                scroll_layout.addWidget(bolum_btn)

            scroll_layout.addStretch()
            scroll.setWidget(scroll_icerik)
            layout.addWidget(scroll)

        layout.addStretch()
        kapat_btn = QPushButton("Kapat")
        kapat_btn.clicked.connect(self.close)
        layout.addWidget(kapat_btn)

    def _sure_guncelle(self):
        gecen_saniye_anlik = int(time.time() - self.baslama_zamani)
        gecen_sure = gecen_saniye_anlik + self.kaldigimiz_saniye


        dakika = gecen_sure // 60
        saniye = gecen_sure % 60

        if dakika == 0:
            self.izleme_lbl.setText(f"İzlenen Süre: {saniye} sn")
        else:
            self.izleme_lbl.setText(f"İzlenen Süre: {dakika} dk {saniye} sn")

    def _bolum_oynat(self, bolum_no, kalinan_sure = 0):
        k_id = self.parent().kullanici_id
        p_id = self.parent().program_id
        sure = self.veri.get("Sure", 0)

        dlg = BolumOynatDialog(self.veri.get("ProgramAdi"), bolum_no, sure, k_id, p_id, self.db, kalinan_sure,self)
        dlg.exec_()

    def closeEvent(self, event):
        if self.tip == "Film":
            self.timer.stop()
            gecen_saniye_anlik = int(time.time() - self.baslama_zamani)
            gecen_sure = gecen_saniye_anlik + self.kaldigimiz_saniye
            dakika = gecen_sure // 60
            kaydedilecek_dakika = 1 if (dakika == 0 and gecen_sure > 0) else dakika

            k_id = self.parent().kullanici_id
            p_id = self.parent().program_id
            self.db.izleme_log(k_id, p_id, 1, kaydedilecek_dakika)
            print(f"Film kapatıldı. Veritabanına {kaydedilecek_dakika} dk izleme yazıldı.")

        event.accept()

class AdminPanel(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana
        self.setStyleSheet(DIZAYN)
        layout = QVBoxLayout(self)

        baslik = QLabel("Yönetici Paneli")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(
            QFont("Press Start 2P", 20)
        )
        baslik.setStyleSheet("""
                    color: red;
                    margin-bottom: 20px;
                """)
        layout.addWidget(baslik)

        kullanici_btn = QPushButton(
            "Kullanıcıları Listele"
        )

        kullanici_btn.clicked.connect(
            self._kullanicilar
        )
        layout.addWidget(kullanici_btn)
        sil_btn = QPushButton(
            "İçerik Sil"
        )
        sil_btn.clicked.connect(
            self._icerik_sil
        )
        layout.addWidget(sil_btn)
        ekle_btn = QPushButton(
            "İçerik Ekle"
        )
        ekle_btn.clicked.connect(
            self._icerik_ekle
        )

        ana_sayfa_btn = QPushButton("Ana Sayfa")
        ana_sayfa_btn.clicked.connect(self._ana_sayfaya_git)
        layout.addWidget(ana_sayfa_btn)
        layout.addWidget(ekle_btn)

        tur_btn = QPushButton("Tür Ekle")
        tur_btn.clicked.connect(self._tur_ekle_panel)
        layout.addWidget(tur_btn)

        en_cok_btn = QPushButton("En Çok İzlenenler")
        en_cok_btn.clicked.connect(self._en_cok_izlenen)
        layout.addWidget(en_cok_btn)

        en_cok_tur_btn = QPushButton("En Çok İzlenen Türler")
        en_cok_tur_btn.clicked.connect(self._en_cok_izlenen_tur)
        layout.addWidget(en_cok_tur_btn)

        puan_btn = QPushButton("En Yüksek Puanlılar")
        puan_btn.clicked.connect(self._en_yuksek_puanli)
        layout.addWidget(puan_btn)

        top_izlenme_btn = QPushButton("Toplam İzlenme")
        top_izlenme_btn.clicked.connect(self._toplam_izlenme)
        layout.addWidget(top_izlenme_btn)

        top_puan_btn = QPushButton("Toplam Verilen Puan")
        top_puan_btn.clicked.connect(self._toplam_puan)
        layout.addWidget(top_puan_btn)

        cikis_btn = QPushButton("Çıkış")
        cikis_btn.clicked.connect(
            lambda: self.ana.ekran_goster(0)
        )
        layout.addWidget(cikis_btn)
        layout.addStretch()

    def _en_cok_izlenen(self):
        try:
            veriler = self.ana.db.en_cok_izlenen()
            dlg = QDialog(self)
            dlg.setWindowTitle("En Çok İzlenen 10 Film")
            dlg.setFixedSize(400, 500)
            dlg.setStyleSheet(DIZAYN)
            layout = QVBoxLayout(dlg)
            if not veriler:
                layout.addWidget(QLabel("Henüz izlenme verisi yok."))
            for i, film in enumerate(veriler, start=1):
                ad = film.get("ProgramAdi", "Bilinmeyen İçerik")
                sayi = film.get("IzlenmeSayisi") or film.get("OynatilmaSayisi", 0)
                lbl = QLabel(f"{i}. {ad} - {sayi} izlenme")
                layout.addWidget(lbl)
            dlg.exec_()
        except Exception as e:
            print(f"Çökme engellendi: {e}")

    def _en_cok_izlenen_tur(self):
        try:
            veriler = self.ana.db.en_cok_izlenen_turler()
            dlg = QDialog(self)
            dlg.setWindowTitle("En Çok İzlenen 3 Tür")
            dlg.setFixedSize(400, 500)
            dlg.setStyleSheet(DIZAYN)
            layout = QVBoxLayout(dlg)
            if not veriler:
                layout.addWidget(QLabel("Henüz izlenme verisi yok."))
            for t, tur in enumerate(veriler, start=1):
                ad = tur.get("TurAdi", "Bilinmeyen Tür")
                sayi = tur.get("OynatilmaSayisi", 0)
                lbl = QLabel(f"{t}. {ad} - {sayi} izlenme")
                layout.addWidget(lbl)
            dlg.exec()
        except Exception as e:
            print(f"Çökme engellendi: {e}")

    def _toplam_izlenme(self):
        try:
            veri = self.ana.db.toplam_izlenme()
            dlg = QDialog(self)
            dlg.setWindowTitle("Toplam İzlenme")
            dlg.setFixedSize(400, 500)
            dlg.setStyleSheet(DIZAYN)
            layout = QVBoxLayout(dlg)
            if not veri:
                layout.addWidget(QLabel("Henüz izlenme verisi yok."))
            lbl = QLabel(f"Toplam İzlenme: {veri}")
            layout.addWidget(lbl)
            dlg.exec_()
        except Exception as e:
            print(f"Çökme engellendi: {e}")

    def _toplam_puan(self):
        try:
            veri = self.ana.db.toplam_puan()
            dlg = QDialog(self)
            dlg.setWindowTitle("Toplam Verilen Puan")
            dlg.setFixedSize(400, 500)
            dlg.setStyleSheet(DIZAYN)
            layout = QVBoxLayout(dlg)
            if not veri:
                layout.addWidget("Henüz puan verisi yok.")
            lbl = QLabel(f"Toplam Verilen Puan: {veri}")
            layout.addWidget(lbl)
            dlg.exec_()
        except Exception as e:
            print(f"Hata engellendi: {e}")

    def _en_yuksek_puanli(self):
        try:
            veriler = self.ana.db.en_yuksek_puanli()
            dlg = QDialog(self)
            dlg.setWindowTitle("En Yüksek Puanlı 10 Film")
            dlg.setFixedSize(400, 500)
            dlg.setStyleSheet(DIZAYN)
            layout = QVBoxLayout(dlg)

            if not veriler:
                layout.addWidget(QLabel("Henüz puan verisi yok."))
            for i, film in enumerate(veriler, start=1):
                ad = film.get("ProgramAdi", "Bilinmeyen İçerik")
                puan = film.get("Puan") or film.get("OrtalamaPuan", 0)
                lbl = QLabel(f"{i}. {ad} - ⭐ {puan}")
                layout.addWidget(lbl)
            dlg.exec_()
        except Exception as e:
            print(f"Çökme engellendi: {e}")

    def _ana_sayfaya_git(self):
        self.ana.ana_sayfa.icerikleri_yukle()
        self.ana.ekran_goster(3)

    def _tur_ekle_panel(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Tür Ekle")
        dlg.setFixedSize(300, 200)
        dlg.setStyleSheet(DIZAYN)
        layout = QVBoxLayout(dlg)
        tur_adi = QLineEdit()
        tur_adi.setPlaceholderText("Tür adı")

        ekle_btn = QPushButton("Ekle")

        def kaydet():
            yeni_tur = tur_adi.text().strip()

            if not yeni_tur:
                QMessageBox.warning(
                    self,
                    "Hata",
                    "Tür adı boş olamaz"
                )
                return

            sonuc = self.ana.db.tur_ekle(yeni_tur)

            if sonuc:
                QMessageBox.warning(
                    self,
                    "Hata",
                    str(sonuc)
                )
            else:
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Tür eklendi"
                )
                dlg.close()

        ekle_btn.clicked.connect(kaydet)

        layout.addWidget(tur_adi)
        layout.addWidget(ekle_btn)

        dlg.exec_()

    def yukle(self):
        pass

    def _kullanicilar(self):
        kullanicilar = self.ana.db.kullanicilari_listele()
        dlg = QDialog(self)
        dlg.setWindowTitle("Kullanıcılar")
        dlg.setFixedSize(500, 500)
        dlg.setStyleSheet(DIZAYN)
        layout = QVBoxLayout(dlg)
        for k in kullanicilar:
            lbl = QLabel(
                f"{k['KullaniciID']} - "
                f"{k['Ad']} {k['Soyad']}"
            )
            layout.addWidget(lbl)
        dlg.exec_()

    def _icerik_sil(self):
        programlar = self.ana.db.tum_programlari_listele()
        dlg = QDialog(self)
        dlg.setWindowTitle("İçerik Sil")
        dlg.setFixedSize(500, 500)
        dlg.setStyleSheet(DIZAYN)
        ana_layout = QVBoxLayout(dlg)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")
        icerik = QWidget()
        icerik_layout = QVBoxLayout(icerik)

        if not programlar:
            lbl = QLabel("İçerik bulunamadı.")
            icerik_layout.addWidget(lbl)

        for p in programlar:
            btn = QPushButton(
                f"{p['ProgramAdi']} ({p['Tip']})"
            )
            btn.clicked.connect(
                lambda checked, x=p["ProgramID"], d=dlg: self._sil(x, d)
            )
            icerik_layout.addWidget(btn)

        icerik_layout.addStretch()
        scroll.setWidget(icerik)
        ana_layout.addWidget(scroll)
        dlg.exec_()

    def _sil(self, program_id, dlg):
        sonuc = self.ana.db.içerik_sil(program_id)
        self.ana.ana_sayfa.icerikleri_yukle()

        QMessageBox.information(
            self,
            "Başarılı",
            "İçerik sistemden tamamen silindi."
        )
        dlg.close()

    def _icerik_ekle(self):
        dlg = QDialog(self)
        dlg.setFixedSize(400, 500)
        dlg.setStyleSheet(DIZAYN)
        layout = QVBoxLayout(dlg)
        ad = QLineEdit()
        ad.setPlaceholderText("Program adı")
        tip = QComboBox()
        tip.addItems(["Film", "Dizi"])
        aciklama = QLineEdit()
        aciklama.setPlaceholderText(
            "Açıklama"
        )
        yil = QSpinBox()
        yil.setRange(1900, 2100)
        bolum = QSpinBox()
        bolum.setRange(1, 999)
        tur = QLineEdit()
        tur.setPlaceholderText(
            "Türler virgüllü"
        )
        ekle_btn = QPushButton("Ekle")

        def kaydet():
            if not ad.text().strip():
                QMessageBox.warning(
                    self,
                    "Hata",
                    "Program adı boş olamaz"
                )
                return

            turler = [
                x.strip()
                for x in tur.text().split(",")
            ]
            self.ana.db.içerik_ekle(
                ad.text(),
                tip.currentText(),
                aciklama.text(),
                yil.value(),
                bolum.value(),
                turler
            )
            QMessageBox.information(
                self,
                "Başarılı",
                "İçerik eklendi"
            )
            dlg.close()
        ekle_btn.clicked.connect(kaydet)
        layout.addWidget(ad)
        layout.addWidget(tip)
        layout.addWidget(aciklama)
        layout.addWidget(yil)
        layout.addWidget(bolum)
        layout.addWidget(tur)
        layout.addWidget(ekle_btn)
        dlg.exec_()

class ProfilEkrani(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana
        self.setStyleSheet(DIZAYN)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll.setFixedSize(960, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        self.icerik = QWidget()
        self.icerik.setStyleSheet("background-color: black;")
        self.layout_main = QVBoxLayout(self.icerik)
        self.layout_main.setContentsMargins(260, 36, 260, 36)
        self.layout_main.setSpacing(10)

        scroll.setWidget(self.icerik)

    def yukle(self):
        for i in reversed(range(self.layout_main.count())):
            w = self.layout_main.itemAt(i).widget()
            if w: w.deleteLater()

        kullanici_id = self.ana.aktif_kullanici[0]
        bilgi = self.ana.db.profil_bilgileri(kullanici_id)

        if not bilgi:
            self.layout_main.addWidget(QLabel("Profil bilgisi alınamadı."))
            return

        geri_btn = QPushButton("Ana Sayfaya Dön")
        baslik = QLabel("Profilim")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Press Start 2P", 22, QFont.Bold))
        baslik.setStyleSheet("color: red; margin-bottom: 16px;")
        self.layout_main.addWidget(baslik)

        alanlar = [
            ("Ad Soyad", f"{bilgi.get('Ad', '')} {bilgi.get('Soyad', '')}"),
            ("Email", bilgi.get("Email", "")),
            ("Doğum Tarihi", bilgi.get("DoğumTarihi", "")),
            ("Ülke", bilgi.get("Ülke", "")),
            ("Favori Türler", ", ".join(bilgi.get("FavoriTürler", []))),
            ("Toplam İzleme (dk)", str(bilgi.get("İzlenenSüre", 0))),
            ("Ortalama Puan", str(bilgi.get("OrtalamaPuan", 0))),
        ]

        for etiket, deger in alanlar:
            satir = QFrame()
            satir.setStyleSheet(
                "QFrame { background-color: #1a1a1a; border: 1px solid #333;"
                " border-radius: 7px; padding: 8px; }"
            )
            sl = QHBoxLayout(satir)
            et = QLabel(etiket)
            et.setStyleSheet("color: #aaa; font-size: 13px; min-width: 160px;")
            dg = QLabel(deger)
            dg.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
            dg.setWordWrap(True)
            sl.addWidget(et);
            sl.addWidget(dg);
            sl.addStretch()
            self.layout_main.addWidget(satir)

        self.layout_main.addSpacing(10)
        sifre_lbl = QLabel("Şifre güncelleme")
        sifre_lbl.setStyleSheet("color: red; font-weight: bold; font-size: 15px;")
        self.layout_main.addWidget(sifre_lbl)

        self.yeni_sifre = _alan("Yeni şifre", sifre=True)
        self.layout_main.addWidget(self.yeni_sifre)

        guncelle_btn = QPushButton("Şifreyi Güncelle")
        guncelle_btn.setFixedHeight(44)
        guncelle_btn.clicked.connect(self._sifre_guncelle)
        self.layout_main.addWidget(guncelle_btn)

        gecmis_btn = QPushButton("İzleme Geçmişi")
        gecmis_btn.setFixedHeight(44)
        gecmis_btn.clicked.connect(self._izleme_gecmisi)
        self.layout_main.addWidget(gecmis_btn)

        geri_btn = QPushButton("Ana Sayfaya Dön")
        geri_btn.setObjectName("ikincil")
        geri_btn.setFixedHeight(40)
        geri_btn.clicked.connect(lambda: self.ana.ekran_goster(3))
        self.layout_main.addWidget(geri_btn)

    def _izleme_gecmisi(self):
        gecmis = self.ana.db.izleme_gecmisi(
            self.ana.aktif_kullanici[0]
        )
        dlg = QDialog(self)
        dlg.setWindowTitle("İzleme Geçmişi")
        dlg.setFixedSize(600, 500)
        dlg.setStyleSheet(DIZAYN)
        layout = QVBoxLayout(dlg)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        icerik = QWidget()
        ic_layout = QVBoxLayout(icerik)
        for kayit in gecmis:
            kart = QFrame()
            kart.setStyleSheet("""
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
            """)
            kl = QVBoxLayout(kart)
            lbl = QLabel(
                f"{kayit['ProgramAdi']} "
                f"- Bölüm {kayit['BolumNo']}"
            )
            lbl.setFont(
                QFont("Press Start 2P", 12, QFont.Bold)
            )
            sure = QLabel(
                f"{kayit['IzlenenSure']} dk izlendi"
            )
            tarih = QLabel(
                kayit["IzlemeTarihi"]
            )
            kl.addWidget(lbl)
            kl.addWidget(sure)
            kl.addWidget(tarih)
            ic_layout.addWidget(kart)

        scroll.setWidget(icerik)
        layout.addWidget(scroll)
        dlg.exec_()

    def _sifre_guncelle(self):
        yeni = self.yeni_sifre.text().strip()
        if len(yeni) < 6:
            QMessageBox.warning(self, "Şifre en az 6 karakter olmalı.")
            return
        sonuc = self.ana.db.sifre_güncelleme(self.ana.aktif_kullanici[0], yeni)
        if sonuc:
            QMessageBox.warning(self, "Hata", str(sonuc))
        else:
            QMessageBox.information(self, "Şifre güncellendi.")
            self.yeni_sifre.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = AnaPencere()
    pencere.show()
    sys.exit(app.exec_())