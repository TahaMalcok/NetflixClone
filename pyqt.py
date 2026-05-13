import sys
import re
from datetime import datetime

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
QWidget { background-color: black; color: white; font-family: Arial; }
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
        self.setStyleSheet("background-color: black;")

        self.stack = QStackedWidget(self)
        self.stack.setFixedSize(960, 720)

        self.giris_ekrani = GirisEkrani(self)
        self.kayit_ekrani = KayitEkrani(self)
        self.oneri_ekrani = OneriEkrani(self)
        self.ana_sayfa = AnaSayfa(self)
        self.profil_ekrani = ProfilEkrani(self)

        for ekran in [self.giris_ekrani, self.kayit_ekrani,
                      self.oneri_ekrani, self.ana_sayfa, self.profil_ekrani]:
            self.stack.addWidget(ekran)

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
        layout.addWidget(kayit_btn)
        layout.addStretch()

    def _giris(self):
        email = self.mail.text().strip()
        sifre = self.sifre.text().strip()

        if not email or not sifre:
            QMessageBox.warning(self, "", "Mail ve şifre boş olamaz.")
            return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            QMessageBox.warning(self, "" ,"Geçerli bir mail adresi girin.")
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
            QMessageBox.warning(self, "Tüm alanları doldurun."); return
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", mail):
            QMessageBox.warning(self, "", "Geçerli bir mail girin."); return
        if sifre != sifre2:
            QMessageBox.warning(self, "", "Şifreler eşleşmiyor."); return
        if cinsiyet == "Seçiniz":
            QMessageBox.warning(self, "", "Cinsiyet seçin."); return
        if len(turler) != 3:
            QMessageBox.warning(self, "", "Tam 3 tür seçin."); return

        try:
            dt = datetime.strptime(dogum, "%d/%m/%Y")
            if dt >= datetime.today():
                QMessageBox.warning(self, "Doğum tarihi bugünden büyük olamaz."); return
            dogum_str = dt.strftime("%Y-%m-%d")
        except ValueError:
            QMessageBox.warning(self, "Tarih Gün/Ay/Yıl formatında olmalı."); return

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
                b = QLabel(f"{film.get('Tip','')}  •  {film.get('YayinYili','')}  •  ⭐ {film.get('OrtalamaPuan',0)}/10")
                b.setStyleSheet("color: #aaa; font-size: 12px;")
                kl.addWidget(t); kl.addWidget(a); kl.addWidget(b)
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
        self.tip_filtre.addItems(["Tümü", "Film", "Dizi"])
        self.tip_filtre.setFixedSize(100, 36)
        self.tip_filtre.currentTextChanged.connect(self._filtrele)

        profil_btn = QPushButton("Profil")
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

        ul.addWidget(logo)
        ul.addStretch()
        ul.addWidget(self.arama)
        ul.addSpacing(8)
        ul.addWidget(self.tip_filtre)
        ul.addSpacing(8)
        ul.addWidget(profil_btn)
        ul.addSpacing(6)
        ul.addWidget(cikis_btn)
        ul.addWidget(oneri_btn)
        ul.addSpacing(6)
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

    def _profile_git(self):
        self.ana.profil_ekrani.yukle()
        self.ana.ekran_goster(4)

    def icerikleri_yukle(self):
        self.tum_icerikler = self.ana.db.tum_programlari_listele()
        self._kartlari_goster(self.tum_icerikler)

    def _filtrele(self):
        arama = self.arama.text().strip().lower()
        tip = self.tip_filtre.currentText()

        sonuc = []
        for row in self.tum_icerikler:
            if arama and arama not in str(row.get("ProgramAdi", "")).lower():
                continue
            if tip != "Tümü" and tip != str(row.get("Tip", "")):
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

        puan_lbl = QLabel(f"⭐ {ort_puan}/10")
        puan_lbl.setStyleSheet("color: #aaa; font-size: 10px;")

        kl.addWidget(tip_lbl)
        kl.addWidget(ad_lbl)
        kl.addWidget(yil_lbl)
        kl.addStretch()
        kl.addWidget(puan_lbl)

        kart.mousePressEvent = lambda e, r=row: self._detay_ac(r)
        return kart

    def _detay_ac(self, row):
        dlg = DetayDialog(row, self.ana.aktif_kullanici[0], self.ana.db, self)
        dlg.exec_()
        self.icerikleri_yukle()

class DetayDialog(QDialog):
    def __init__(self, row, kullanici_id, db, parent=None):
        super().__init__(parent)
        self.kullanici_id = kullanici_id
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
        if self.detay_verisi:
            aciklama = self.detay_verisi.get("Aciklama", "")
            if aciklama and str(aciklama).strip():
                ac = QLabel(str(aciklama))
                ac.setWordWrap(True)
                ac.setStyleSheet("color: #ccc; font-size: 12px; margin-top: 6px;")
                layout.addWidget(ac)

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

        layout.addStretch()

        btn_lay = QHBoxLayout()
        fav_btn = QPushButton(" Favoriye Ekle")
        fav_btn.setObjectName("ikincil")
        fav_btn.setFixedHeight(44)
        fav_btn.clicked.connect(self._favoriye_ekle)

        kapat_btn = QPushButton("Kapat")
        kapat_btn.setObjectName("ikincil")
        kapat_btn.setFixedHeight(44)
        kapat_btn.clicked.connect(self.close)

        btn_lay.addWidget(fav_btn)
        btn_lay.addWidget(kapat_btn)
        layout.addLayout(btn_lay)

    def _satir(self, layout, etiket, deger):
        h = QHBoxLayout()
        et = QLabel(etiket)
        et.setStyleSheet("color: #aaa; font-size: 12px; min-width: 130px;")
        dg = QLabel(deger)
        dg.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")
        h.addWidget(et); h.addWidget(dg); h.addStretch()
        layout.addLayout(h)

    def _favoriye_ekle(self):
        sonuc = self.db.favori_ekle(self.program_id, self.kullanici_id)
        if sonuc:
            QMessageBox.information(self, "Bilgi", str(sonuc))
        else:
            QMessageBox.information(self, "asd","Favoriye eklendi.")

    def _puan_ver(self):
        puan = self.puan_spin.value()
        sonuc = self.db.puanlama(self.kullanici_id, self.program_id, puan)
        QMessageBox.information(self, "Bilgi", str(sonuc))

class ProfilEkrani(QWidget):
    def __init__(self, ana):
        super().__init__()
        self.ana = ana
        self.setStyleSheet(DIZAYN)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll.setFixedSize(960, 720)

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

        baslik = QLabel("Profilim")
        baslik.setAlignment(Qt.AlignCenter)
        baslik.setFont(QFont("Arial Black", 22, QFont.Bold))
        baslik.setStyleSheet("color: red; margin-bottom: 16px;")
        self.layout_main.addWidget(baslik)

        alanlar = [
            ("Ad Soyad", f"{bilgi.get('Ad','')} {bilgi.get('Soyad','')}"),
            ("Email",    bilgi.get("Email", "")),
            ("Doğum Tarihi", bilgi.get("DoğumTarihi", "")),
            ("Ülke",     bilgi.get("Ülke", "")),
            ("Favori Türler", ", ".join(bilgi.get("FavoriTürler", []))),
            ("Toplam İzleme (dk)", str(bilgi.get("IzlenenSure", 0))),
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
            sl.addWidget(et); sl.addWidget(dg); sl.addStretch()
            self.layout_main.addWidget(satir)

        self.layout_main.addSpacing(10)
        sifre_lbl = QLabel("Şifre güncelle")
        sifre_lbl.setStyleSheet("color: red; font-weight: bold; font-size: 15px;")
        self.layout_main.addWidget(sifre_lbl)

        self.yeni_sifre = _alan("Yeni şifre", sifre=True)
        self.layout_main.addWidget(self.yeni_sifre)

        guncelle_btn = QPushButton("Şifreyi Güncelle")
        guncelle_btn.setFixedHeight(44)
        guncelle_btn.clicked.connect(self._sifre_guncelle)
        self.layout_main.addWidget(guncelle_btn)

        geri_btn = QPushButton("Ana Sayfaya Dön")
        geri_btn.setObjectName("ikincil")
        geri_btn.setFixedHeight(40)
        geri_btn.clicked.connect(lambda: self.ana.ekran_goster(3))
        self.layout_main.addWidget(geri_btn)

    def _sifre_guncelle(self):
        yeni = self.yeni_sifre.text().strip()
        if len(yeni) < 6:
            QMessageBox.warning(self, "Şifre en az 6 karakter olmalı.")
            return
        sonuc = self.ana.db.sifre_güncelle(self.ana.aktif_kullanici[0], yeni)
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