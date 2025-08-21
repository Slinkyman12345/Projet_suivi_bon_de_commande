# gui/main_window.py

import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from gui.encode_window import EncodeWindow
from gui.search_window import SearchWindow
from gui.changelog_window import ChangelogWindow
from gui.ajout_facture_window import AjoutFactureWindow
from gui.gestion_technique import GestionTechniqueWindow
from db import init_db

ctk.set_appearance_mode("Light")

init_db()

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Menu Principal")
        self.geometry("850x750")
        self.resizable(False, False)
        self.configure(fg_color=ctk.ThemeManager.theme["CTk"]["fg_color"])

        # Frame principale
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=20,
            border_width=2,
            border_color="#a3bffa",
            width=580,
            height=480
        )
        self.main_frame.place(relx=0.5, rely=0.52, anchor="center")

        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="  Gestion des Bons de Commande  ",
            font=("Segoe UI", 26, "bold")
        )
        self.title_label.pack(pady=(50, 15))

        self.subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Choisissez une action",
            font=("Segoe UI", 16)
        )
        self.subtitle.pack(pady=(0, 30))

        btn_style = {
            "font": ("Segoe UI", 16, "bold"),
            "corner_radius": 15,
            "height": 50,
            "width": 280
        }

        self.btn_encode = ctk.CTkButton(self.main_frame, text="➕ Encoder un Bon", command=self.open_encode, **btn_style)
        self.btn_encode.pack(pady=12)

        self.btn_search = ctk.CTkButton(self.main_frame, text="🔍 Visualiser les Bons", command=self.open_search, **btn_style)
        self.btn_search.pack(pady=12)

        self.btn_facture = ctk.CTkButton(self.main_frame, text="➕ Ajout d'une facture", command=self.open_ajout_facture, **btn_style)
        self.btn_facture.pack(pady=12)

        btn_technique = ctk.CTkButton(self.main_frame, text="⚙️ Gestion Technique", command=self.open_gestion_technique, **btn_style)
        btn_technique.pack(pady=12)

        self.btn_changelog = ctk.CTkButton(self.main_frame, text="🕘 Historique des Versions", command=self.open_changelog, **btn_style)
        self.btn_changelog.pack(pady=12)

        self.btn_quit = ctk.CTkButton(
            self.main_frame,
            text="❌ Quitter l'application",
            command=self.on_closing,
            fg_color="#d9534f",
            hover_color="#c9302c",
            text_color="white",
            **btn_style
        )
        self.btn_quit.pack(pady=30)

        # Logo Police
        logo_path = os.path.join("assets", "polnam_logo.png")
        if os.path.exists(logo_path):
            pil_image = Image.open(logo_path)
            self.logo_img = ctk.CTkImage(light_image=pil_image, size=(150, 150))
            self.logo_label = ctk.CTkLabel(self, image=self.logo_img, text="")
            self.logo_label.place(relx=0.02, rely=0.02, anchor="nw")
        else:
            self.logo_label = ctk.CTkLabel(self, text="Logo Police Belge", font=("Segoe UI", 10, "italic"))
            self.logo_label.place(relx=0.02, rely=0.02, anchor="nw")

        # Version
        self.version_label = ctk.CTkLabel(self, text="Version 1.0.6", font=("Segoe UI", 12, "italic"))
        self.version_label.place(relx=0.98, rely=0.98, anchor="se")

        # Bouton Thème
        self.theme_btn = ctk.CTkButton(
            self,
            text="🌙" if ctk.get_appearance_mode() == "Light" else "🌞",
            width=50,
            height=40,
            corner_radius=10,
            font=("Segoe UI", 18),
            command=self.toggle_theme
        )
        self.theme_btn.place(relx=0.02, rely=0.98, anchor="sw")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_theme = "Dark" if current == "Light" else "Light"
        ctk.set_appearance_mode(new_theme)

        # Met à jour l'icône
        self.theme_btn.configure(text="🌙" if new_theme == "Light" else "🌞")

        # Change le fond principal de la fenêtre
        self.configure(fg_color=ctk.ThemeManager.theme["CTk"]["fg_color"])

        # Petit toast de notification
        toast = ctk.CTkLabel(
            self,
            text=f"Thème {new_theme.lower()} activé",
            text_color="#fff" if new_theme == "Dark" else "#000",
            fg_color="#444" if new_theme == "Dark" else "#ddd",
            corner_radius=10,
            font=("Segoe UI", 14, "bold")
        )
        toast.place(relx=0.02, rely=0.05, anchor="nw")
        self.after(1500, toast.destroy)

    def open_encode(self):
        self.withdraw()
        encode = EncodeWindow(self)
        encode.protocol("WM_DELETE_WINDOW", lambda: [encode.destroy(), self.deiconify()])

    def open_search(self):
        self.withdraw()
        try:
            search = SearchWindow(self)
            search.protocol("WM_DELETE_WINDOW", lambda: [search.destroy(), self.deiconify()])
        except Exception as e:
            print("Erreur lors de l'ouverture de SearchWindow :", e)
            self.deiconify()

    def open_ajout_facture(self):
        self.withdraw()
        ajout_facture = AjoutFactureWindow(self)
        ajout_facture.protocol("WM_DELETE_WINDOW", lambda: [ajout_facture.destroy(), self.deiconify()])

    def open_gestion_technique(self):
        self.withdraw()
        gestion = GestionTechniqueWindow(self, bons_db_path="bons.db")
        gestion.protocol("WM_DELETE_WINDOW", lambda: [gestion.destroy(), self.deiconify()])

    def open_changelog(self):
        self.withdraw()
        changelog = ChangelogWindow(self)
        changelog.protocol("WM_DELETE_WINDOW", lambda: [changelog.destroy(), self.deiconify()])

    def on_closing(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application ?"):
            self.destroy()

