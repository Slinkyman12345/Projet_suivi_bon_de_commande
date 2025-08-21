# gui/ajout_facture_window.py

import customtkinter as ctk

class AjoutFactureWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Ajout d'une facture")
        self.geometry("600x300")

        # Couleur de fond adaptative
        self.configure(fg_color=ctk.ThemeManager.theme["CTkToplevel"]["fg_color"])

        message = ctk.CTkLabel(
            self,
            text="Disponible à la version 1.1.0 du programme",
            font=("Segoe UI", 20, "bold"),
            text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        )
        message.pack(expand=True, pady=50)

        btn_retour = ctk.CTkButton(
            self,
            text="← Retour Menu",
            command=self.retour_menu
        )
        btn_retour.pack(pady=20)

        self.protocol("WM_DELETE_WINDOW", self.retour_menu)  # gestion fermeture fenêtre

    def retour_menu(self):
        self.destroy()
        self.master.deiconify()
