# gui/new_invoice_window.py

import customtkinter as ctk
from tkinter import messagebox
from db import fetch_all, insert_bon


class NewInvoiceWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Nouvelle facture pour bon existant")
        self.geometry("1000x800")
        self.configure(fg_color="white")
        self.resizable(False, False)

        title = ctk.CTkLabel(
            self, text="Ajout d'une nouvelle facture",
            font=("Arial", 24), text_color="black"
        )
        title.pack(pady=20)

        # Zone de recherche
        search_frame = ctk.CTkFrame(self, fg_color="white")
        search_frame.pack(pady=10)

        self.recherche_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="ID ou N° de bon (BONPOL/xx)",
            text_color="black",
            fg_color="white",
            placeholder_text_color="gray"
        )
        self.recherche_entry.pack(side="left", padx=10)

        ctk.CTkButton(search_frame, text="Rechercher", command=self.rechercher_bon).pack(side="left", padx=5)

        # Résultat affiché
        self.bon_frame = ctk.CTkFrame(self, fg_color="#f5f5f5", corner_radius=10)
        self.bon_frame.pack(pady=15, padx=30, fill="x")

        self.labels_bon = {}
        champs = [
            ("ID", "id"),
            ("Année", "annee_comptable"),
            ("Numéro Bon", "numero_bon"),
            ("Fournisseur", "fournisseur"),
            ("Montant engagé", "montant_engage"),
            ("Montant restant (calculé)", "montant_restant"),
            ("Imputation", "imputation"),
            ("Description", "description")
        ]

        for i, (label, key) in enumerate(champs):
            ctk.CTkLabel(self.bon_frame, text=label + " :", font=("Arial", 14)).grid(row=i, column=0, sticky="e", padx=10, pady=5)
            champ = ctk.CTkLabel(self.bon_frame, text="", font=("Arial", 14), text_color="black")
            champ.grid(row=i, column=1, sticky="w", padx=10, pady=5)
            self.labels_bon[key] = champ

        # Formulaire de nouvelle facture
        facture_frame = ctk.CTkFrame(self, fg_color="white")
        facture_frame.pack(pady=20)

        self.numero_facture_entry = ctk.CTkEntry(
            facture_frame,
            placeholder_text="N° Facture",
            text_color="black",
            fg_color="white"
        )
        self.numero_facture_entry.grid(row=0, column=0, padx=10, pady=10)

        self.montant_facture_entry = ctk.CTkEntry(
            facture_frame,
            placeholder_text="Montant Facture (€)",
            text_color="black",
            fg_color="white"
        )
        self.montant_facture_entry.grid(row=0, column=1, padx=10, pady=10)

        self.commentaire_entry = ctk.CTkEntry(
            facture_frame,
            placeholder_text="Commentaire (optionnel)",
            text_color="black",
            fg_color="white"
        )
        self.commentaire_entry.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="we")

        ctk.CTkButton(self, text="Ajouter la facture", command=self.ajouter_facture, height=40, font=("Arial", 14), width=200).pack(pady=10)
        ctk.CTkButton(self, text="Retour vers le menu", command=self.retour_menu, height=40, font=("Arial", 14), width=200).pack(pady=10)

        self.bon_original = None
        self.montant_restant_calcule = 0.0

    def rechercher_bon(self):
        saisie = self.recherche_entry.get().strip()
        if not saisie:
            messagebox.showwarning("Erreur", "Veuillez entrer un ID ou un numéro de bon.")
            return

        tous_les_bons = fetch_all()

        # Extraction numéro si format BONPOL/xx
        if saisie.upper().startswith("BONPOL/"):
            saisie_num = saisie.split("/", 1)[1]
        else:
            saisie_num = saisie

        bons_correspondants = []
        for bon in tous_les_bons:
            id_str = str(bon[1])  # ID = colonne 1
            numero_bon_str = str(bon[2])  # N° Bon = colonne 2
            if saisie == id_str or saisie_num == numero_bon_str:
                bons_correspondants.append(bon)

        if not bons_correspondants:
            messagebox.showinfo("Aucun résultat", "Aucun bon trouvé pour cette saisie.")
            return

        self.bon_original = bons_correspondants[0]

        total_factures = sum(
            float(b[11]) for b in bons_correspondants if b[11] not in (None, "", " ")
        )
        self.montant_restant_calcule = round(self.bon_original[3] - total_factures, 2)

        numero_bon_affiche = self.bon_original[2]
        if not numero_bon_affiche.upper().startswith("BONPOL/"):
            numero_bon_affiche = "BONPOL/" + str(numero_bon_affiche)

        affichage = {
            "id": self.bon_original[1],
            "annee_comptable": self.bon_original[2],
            "numero_bon": numero_bon_affiche,
            "fournisseur": self.bon_original[4],
            "montant_engage": self.bon_original[3],
            "montant_restant": self.montant_restant_calcule,
            "imputation": self.bon_original[5],
            "description": self.bon_original[14]
        }

        for key, widget in self.labels_bon.items():
            widget.configure(text=str(affichage.get(key, "")), text_color="black")

    def ajouter_facture(self):
        if not self.bon_original:
            messagebox.showwarning("Erreur", "Veuillez d'abord rechercher un bon.")
            return

        numero_facture = self.numero_facture_entry.get().strip()
        try:
            montant_facture = float(self.montant_facture_entry.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "Montant facture invalide.")
            return

        commentaire = self.commentaire_entry.get().strip()

        if montant_facture > self.montant_restant_calcule:
            messagebox.showerror("Erreur", f"Montant dépasse le restant ({self.montant_restant_calcule} €).")
            return

        nouveau_restant = round(self.montant_restant_calcule - montant_facture, 2)

        new_bon = (
            self.bon_original[1],  # ID
            self.bon_original[2],  # année comptable
            self.bon_original[3],  # numéro de bon
            self.bon_original[4],  # montant engagé
            self.bon_original[5],  # fournisseur
            self.bon_original[6],  # imputation
            self.bon_original[7],  # envoyé ville
            self.bon_original[8],  # envoyé entreprise
            self.bon_original[9],  # livré
            1,                     # facture cochée
            numero_facture,
            montant_facture,
            nouveau_restant,
            self.bon_original[13],  # numéro article
            self.bon_original[14],  # description
            commentaire
        )

        insert_bon(new_bon)
        messagebox.showinfo("Succès", f"Facture ajoutée. Nouveau montant restant : {nouveau_restant} €")
        self.numero_facture_entry.delete(0, 'end')
        self.montant_facture_entry.delete(0, 'end')
        self.commentaire_entry.delete(0, 'end')
        self.rechercher_bon()

    def retour_menu(self):
        self.destroy()
        self.master.deiconify()
