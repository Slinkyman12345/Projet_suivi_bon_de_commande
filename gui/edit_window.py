import customtkinter as ctk
import sqlite3
from tkinter import messagebox

class EditWindow(ctk.CTkToplevel):
    def __init__(self, master, bon, visualisation_instance=None):
        super().__init__(master)

        self.master = master
        self.visualisation_instance = visualisation_instance

        # Si "bon" est juste un ID (int), on va chercher la ligne complète dans la base
        if isinstance(bon, int):
            bon_data = self.fetch_bon_by_id(bon)
            if bon_data is None:
                messagebox.showerror("Erreur", f"Aucun bon trouvé avec l'ID {bon}")
                self.destroy()
                return
            self.bon_data = bon_data
        else:
            self.bon_data = bon

        self.title("Modifier Bon de Commande")
        self.geometry("1200x850")
        self.resizable(True, True)

        self.configure(
            padx=20,
            pady=20,
            fg_color=ctk.ThemeManager.theme["CTk"]["fg_color"]
        )

        # Données originales
        self.original_id = self.bon_data[0]
        self.bon = self.bon_data

        self.fields = {
            "ID Bon": self.bon[1],
            "Année Comptable": self.bon[2],
            "Numéro Bon": self.bon[3],
            "Montant Engagé": self.bon[4],
            "Fournisseur": self.bon[5],
            "Imputation": self.bon[6],
            "Montant Restant": self.bon[13],
            "Description": self.bon[14],
            "Commentaire": self.bon[15],
        }

        self.booleens = {
            "Envoyé Ville": bool(self.bon[7]),
            "Envoyé Entreprise": bool(self.bon[8]),
            "Livré": bool(self.bon[9]),
            "Facturé": bool(self.bon[10]),
        }

        self.facture_fields = {
            "Numéro Facture": self.bon[11],
            "Montant Facture": self.bon[12],
        }

        self.entries = {}
        self.checkboxes = {}

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=12,
            border_width=1,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        self.scrollable_frame.pack(fill="both", expand=True)

        self.create_info_frame()
        self.create_modification_fields()
        self.create_statut_checkboxes()
        self.create_facture_frame()
        self.create_buttons()

        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.toggle_facture_fields(initial=True)

    def fetch_bon_by_id(self, id_interne):
        """Récupère un bon complet par son ID dans la base bons.db"""
        try:
            with sqlite3.connect("bons.db") as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM bons_de_commande WHERE id=?", (id_interne,))
                return cur.fetchone()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de récupérer le bon : {e}")
            return None

    def create_info_frame(self):
        self.info_frame = ctk.CTkFrame(
            self.scrollable_frame,
            corner_radius=15,
            border_width=1,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        self.info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 20))
        self.info_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            self.info_frame,
            text="📄 Informations du Bon",
            font=("Segoe UI", 20, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(10, 15))

        infos_affichage = [
            ("ID Bon", str(self.bon[1])),
            ("Année Comptable", str(self.bon[2])),
            ("Numéro Bon", f"BONPOL/{self.bon[3]}"),
            ("Fournisseur", str(self.bon[5])),
            ("Imputation", str(self.bon[6])),
            ("Montant Restant", f"{self.bon[13]} €"),
            ("Description", str(self.bon[14]))
        ]

        for i, (label, value) in enumerate(infos_affichage, start=1):
            col = 0 if i <= 3 else 1
            row = i if i <= 3 else i - 3
            ctk.CTkLabel(
                self.info_frame,
                text=f"{label} :",
                font=("Segoe UI", 14, "bold"),
                anchor="w"
            ).grid(row=row, column=col*2, sticky="w", padx=(15, 5), pady=4)
            ctk.CTkLabel(
                self.info_frame,
                text=value,
                font=("Segoe UI", 14),
                anchor="w",
                wraplength=300
            ).grid(row=row, column=col*2+1, sticky="w", padx=(0, 15), pady=4)

    def create_modification_fields(self):
        title_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Modification du Bon de Commande",
            font=("Helvetica", 22, "bold")
        )
        title_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))

        label_opts = {"anchor": "w", "font": ("Helvetica", 13)}

        row = 2
        for label, value in self.fields.items():
            lbl = ctk.CTkLabel(self.scrollable_frame, text=label, **label_opts)
            lbl.grid(row=row, column=0, sticky="w", padx=20, pady=12)

            entry = ctk.CTkEntry(self.scrollable_frame, font=("Helvetica", 13))
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, sticky="ew", padx=20, pady=12)

            entry.bind("<Return>", lambda e, r=row+1: self.focus_next(r))

            self.entries[label] = entry
            row += 1

        self.entries["Montant Restant"].configure(state="disabled")

        separator = ctk.CTkFrame(
            self.scrollable_frame,
            height=3,
            fg_color=ctk.ThemeManager.theme["CTkFrame"].get("top_fg_color", "#4a4a4a")
        )
        separator.grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=(30, 15))
        self.separator_row = row + 1

    def create_statut_checkboxes(self):
        cb_label = ctk.CTkLabel(self.scrollable_frame, text="Statut du Bon", font=("Helvetica", 16, "bold"))
        cb_label.grid(row=self.separator_row, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 15))
        row = self.separator_row + 1

        for label, value in self.booleens.items():
            cb = ctk.CTkCheckBox(self.scrollable_frame, text=label, font=("Helvetica", 13))
            if value:
                cb.select()
            cb.grid(row=row, column=0, columnspan=2, sticky="w", padx=40, pady=10)
            if label == "Facturé":
                cb.configure(command=self.toggle_facture_fields)
            self.checkboxes[label] = cb
            row += 1
        self.checkboxes_row = row

    def create_facture_frame(self):
        self.facture_frame = ctk.CTkFrame(
            self.scrollable_frame,
            corner_radius=10,
            border_width=1,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        self.facture_frame.grid(row=self.checkboxes_row, column=0, columnspan=2, sticky="ew", padx=40, pady=(15, 30))
        self.facture_frame.grid_columnconfigure(1, weight=1)

        facture_title = ctk.CTkLabel(self.facture_frame, text="Détails Facture", font=("Helvetica", 14, "bold"))
        facture_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 15), padx=15)

        self.facture_entries = {}
        f_row = 1
        for label, value in self.facture_fields.items():
            lbl = ctk.CTkLabel(self.facture_frame, text=label, font=("Helvetica", 13))
            lbl.grid(row=f_row, column=0, sticky="w", padx=15, pady=10)

            entry = ctk.CTkEntry(self.facture_frame, font=("Helvetica", 13))
            entry.insert(0, str(value))
            entry.grid(row=f_row, column=1, sticky="ew", padx=15, pady=10)
            self.facture_entries[label] = entry
            f_row += 1

    def create_buttons(self):
        self.button_frame = ctk.CTkFrame(
            self,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        )
        self.button_frame.pack(fill="x", pady=10)

        self.back_btn = ctk.CTkButton(
            self.button_frame,
            text="← Retour à la visualisation",
            font=("Helvetica", 14, "bold"),
            command=self.retour_visualisation
        )
        self.back_btn.pack(side="left", padx=10)

        self.save_btn = ctk.CTkButton(
            self.button_frame,
            text="Mettre à jour",
            font=("Helvetica", 16, "bold"),
            command=self.save
        )
        self.save_btn.pack(side="right", padx=10)

    def toggle_facture_fields(self, initial=False):
        facture_active = self.checkboxes["Facturé"].get() == 1
        if facture_active:
            self.facture_frame.grid()
            for entry in self.facture_entries.values():
                entry.configure(state="normal")
        else:
            self.facture_frame.grid_remove()
            if not initial:
                for entry in self.facture_entries.values():
                    entry.delete(0, "end")

    def focus_next(self, row):
        widgets = list(self.entries.values())
        if row < len(widgets):
            widgets[row].focus_set()

    def retour_visualisation(self):
        self.destroy()
        if self.visualisation_instance:
            try:
                print("Appel refresh_data() sur visualisation_instance...")
                self.visualisation_instance.refresh_data()
                print("refresh_data() appelé.")
            except Exception as e:
                print(f"Erreur refresh visualisation: {e}")
        else:
            print("Pas de visualisation_instance, tentative de déiconification master...")
            if hasattr(self.master, "deiconify"):
                self.master.deiconify()

    def save(self):
        try:
            engage = float(self.entries["Montant Engagé"].get().replace(",", "."))
            facture = 0.0
            if self.checkboxes["Facturé"].get() == 1:
                facture_text = self.facture_entries["Montant Facture"].get().strip()
                facture = float(facture_text.replace(",", ".")) if facture_text else 0.0
            restant = engage - facture

            self.entries["Montant Restant"].configure(state="normal")
            self.entries["Montant Restant"].delete(0, "end")
            self.entries["Montant Restant"].insert(0, f"{restant:.2f}")
            self.entries["Montant Restant"].configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur calcul Montant Restant : {e}")
            return

        values = {k: self.entries[k].get().strip() for k in self.entries}
        bools = {k: int(self.checkboxes[k].get()) for k in self.checkboxes}  # Int pour stocker en DB (0/1)
        facture_vals = {k: self.facture_entries[k].get().strip() for k in self.facture_entries}

        try:
            with sqlite3.connect("bons.db") as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE bons_de_commande SET
                        id_bon=?, annee_comptable=?, numero_bon=?, montant_engage=?, fournisseur=?, imputation=?,
                        envoye_ville=?, envoye_entreprise=?, livre=?, facture=?, numero_facture=?,
                        montant_facture=?, montant_restant=?, description=?, commentaire=?
                    WHERE id=?
                """, (
                    values["ID Bon"], values["Année Comptable"], values["Numéro Bon"], values["Montant Engagé"],
                    values["Fournisseur"], values["Imputation"], bools["Envoyé Ville"],
                    bools["Envoyé Entreprise"], bools["Livré"], bools["Facturé"],
                    facture_vals["Numéro Facture"], facture_vals["Montant Facture"],
                    values["Montant Restant"], values["Description"], values["Commentaire"], self.original_id
                ))
                conn.commit()

            messagebox.showinfo("Succès", "Le bon de commande a été mis à jour avec succès.")
            self.retour_visualisation()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {e}")
