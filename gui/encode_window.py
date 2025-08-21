# gui/encode_window.py

import customtkinter as ctk
from tkinter import messagebox
from db import (
    insert_bon, update_bon, fetch_bon, fetch_factures_by_bon,
    add_facture, update_montants_bon
)
import sqlite3

class EncodeWindow(ctk.CTkToplevel):
    def __init__(self, master, bon=None):
        super().__init__(master)
        self.master = master
        self.bon = bon  # si None => encodage, sinon modification
        self.title("Encoder un bon de commande" if bon is None else "Modifier un bon de commande")
        self.geometry("1124x868")
        self.minsize(800, 600)
        self.configure(fg_color=ctk.ThemeManager.theme["CTkToplevel"]["fg_color"])

        label_text = "Encoder un bon de commande" if bon is None else "Modifier un bon de commande"
        title_label = ctk.CTkLabel(
            self,
            text=label_text,
            font=("Segoe UI", 28, "bold"),
            text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        )
        title_label.pack(pady=(30, 15))

        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            width=980,
            height=600,
            corner_radius=20,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"],
            border_width=1,
            border_color="#a3bffa"
        )
        self.scrollable_frame.pack(padx=40, pady=10, fill="both", expand=True)

        # Stockage UI
        self.entries = {}
        self.checkboxes = {}
        self.facture_rows = []  # liste de tuples (num_entry, montant_entry, delete_btn)

        # Champs textes principaux
        self.text_fields = [
            ("ID du bon", "ex: BON12345"),
            ("Année comptable", "ex: 2025"),
            ("N° du bon", "ex: 001"),
            ("Montant engagé", "ex: 1250.00"),
            ("Fournisseur", "ex: Fournisseur XYZ"),
            ("Imputation (Art.: 330/12402-02)", "ex: 330/12402-02"),
            ("Description", "Description détaillée du bon"),
            ("Commentaire", "Commentaires additionnels")
        ]

        # Checkbox fields (Facture gérée séparément)
        self.checkbox_fields = [
            "Envoyé à la ville",
            "Envoyé à l'entreprise",
            "Commande livrée"
        ]

        # Construction du formulaire principal
        row = 0
        for label_text, placeholder in self.text_fields:
            lbl = ctk.CTkLabel(
                self.scrollable_frame,
                text=label_text,
                anchor="w",
                text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"],
                font=("Segoe UI", 14, "bold")
            )
            lbl.grid(row=row, column=0, sticky="w", pady=8, padx=20)
            entry = ctk.CTkEntry(self.scrollable_frame, width=480, placeholder_text=placeholder, font=("Segoe UI", 13))
            entry.grid(row=row, column=1, pady=8, padx=20)
            entry.bind("<Return>", self.focus_next)
            self.entries[label_text] = entry
            row += 1

        # Checkbox simple
        for label_text in self.checkbox_fields:
            lbl = ctk.CTkLabel(
                self.scrollable_frame,
                text=label_text,
                anchor="w",
                text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"],
                font=("Segoe UI", 14, "bold")
            )
            lbl.grid(row=row, column=0, sticky="w", pady=8, padx=20)
            cb = ctk.CTkCheckBox(self.scrollable_frame, text="", hover_color="#5578d1", fg_color="#5578d1")
            cb.grid(row=row, column=1, pady=8, padx=20, sticky="w")
            self.checkboxes[label_text] = cb
            row += 1

        # Checkbox "Facture" qui active la section factures
        lbl = ctk.CTkLabel(
            self.scrollable_frame,
            text="Factures liées",
            anchor="w",
            text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"],
            font=("Segoe UI", 14, "bold")
        )
        lbl.grid(row=row, column=0, sticky="w", pady=8, padx=20)
        cb_facture = ctk.CTkCheckBox(self.scrollable_frame, text="", hover_color="#5578d1", fg_color="#5578d1")
        cb_facture.grid(row=row, column=1, pady=8, padx=20, sticky="w")
        # on stocke cette checkbox
        self.checkboxes["Facture"] = cb_facture
        # row suivant sert de départ pour la section facture
        self.facture_row_start = row + 1
        row = self.facture_row_start

        # Crée la zone facture (vide pour l'instant)
        self.create_facture_section(start_row=self.facture_row_start)

        # Ligne séparatrice
        ctk.CTkLabel(self, text="", height=1, fg_color="#d0d7e2").pack(fill="x", pady=(10, 0))

        # Buttons bas
        btn_frame = ctk.CTkFrame(self, fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"], height=80)
        btn_frame.pack(side="bottom", fill="x")
        btn_frame.columnconfigure((0, 1), weight=1)

        save_btn_text = "💾 Enregistrer" if bon is None else "✅ Mettre à jour"
        save_btn = ctk.CTkButton(
            btn_frame,
            text=save_btn_text,
            command=self.enregistrer,
            width=200,
            height=45,
            font=("Segoe UI", 15, "bold"),
            corner_radius=15,
            fg_color="#5578d1",
            hover_color="#3e5bbf",
            text_color="white"
        )
        save_btn.grid(row=0, column=0, pady=20)

        retour_btn = ctk.CTkButton(
            btn_frame,
            text="↩️ Retour Menu",
            command=self.retour_menu,
            width=200,
            height=45,
            font=("Segoe UI", 15, "bold"),
            fg_color="#d9534f",
            hover_color="#c9302c",
            corner_radius=15,
            text_color="white"
        )
        retour_btn.grid(row=0, column=1, pady=20)

        # Si on modifie un bon existant, charger ses valeurs et ses factures
        if self.bon is not None:
            self.load_bon(self.bon)
        else:
            # par défaut cacher la section facture
            self._update_facture_ui()

        # Bind pour la checkbox facture (clic)
        cb_facture.configure(command=self._update_facture_ui)

    # ----------------- SECTION FACTURES (UI) ----------------- #

    def create_facture_section(self, start_row):
        """Crée l'en-tête et le bouton + pour les factures."""
        # Entête colonnes
        lbl_num = ctk.CTkLabel(self.scrollable_frame, text="N° facture", font=("Segoe UI", 12, "bold"))
        lbl_num.grid(row=start_row, column=0, padx=20, sticky="w")
        lbl_mt = ctk.CTkLabel(self.scrollable_frame, text="Montant (€)", font=("Segoe UI", 12, "bold"))
        lbl_mt.grid(row=start_row, column=1, padx=20, sticky="w")

        # Bouton ajouter (à droite)
        add_btn = ctk.CTkButton(self.scrollable_frame, text="+ Ajouter facture", command=self._ui_add_facture)
        add_btn.grid(row=start_row, column=2, padx=10, sticky="e")

        # zone contenant les lignes de facture (on utilisera scrollable_frame pour placer les lignes)
        # Les lignes seront placées à partir de start_row+1
        self.factures_ui_start = start_row + 1

    def _ui_add_facture(self, num="", montant=""):
        """Ajoute une ligne facture dans l'UI (num et montant optionnels)."""
        # calcule la ligne à utiliser (après les en-têtes + déjà présentes)
        row = self.factures_ui_start + len(self.facture_rows)

        num_entry = ctk.CTkEntry(self.scrollable_frame, width=300)
        num_entry.insert(0, str(num))
        num_entry.grid(row=row, column=0, padx=20, pady=6, sticky="w")

        montant_entry = ctk.CTkEntry(self.scrollable_frame, width=200)
        montant_entry.insert(0, str(montant))
        montant_entry.grid(row=row, column=1, padx=20, pady=6, sticky="w")

        delete_btn = ctk.CTkButton(self.scrollable_frame, text="🗑", width=40,
                                   command=lambda e1=num_entry, e2=montant_entry, b=None: self._ui_delete_facture(e1, e2, delete_btn))
        delete_btn.grid(row=row, column=2, padx=10, pady=6, sticky="w")

        self.facture_rows.append((num_entry, montant_entry, delete_btn))
        # si on ajoute une facture, cocher la checkbox Facture
        self.checkboxes["Facture"].select()
        # pas de save automatique — tout sera sauvegardé au clic sur Enregistrer

    def _ui_delete_facture(self, num_entry, montant_entry, btn):
        """Supprime la ligne UI correspondante."""
        try:
            num_entry.destroy()
            montant_entry.destroy()
            btn.destroy()
            self.facture_rows = [(n, m, b) for (n, m, b) in self.facture_rows if n != num_entry]
        except Exception:
            pass
        # si plus aucune facture restante, décocher la checkbox Facture
        if not self.facture_rows:
            self.checkboxes["Facture"].deselect()

    def _update_facture_ui(self):
        """Affiche/masque la section facture selon checkbox."""
        show = self.checkboxes["Facture"].get() == 1
        start = self.facture_row_start
        # En-têtes et bouton + : présents sur lignes start (créés une fois), on masque/affiche toutes les lignes dynamiques
        if not show:
            # masquer toutes les lignes facture UI
            for (n, m, b) in list(self.facture_rows):
                try:
                    n.grid_remove()
                    m.grid_remove()
                    b.grid_remove()
                except Exception:
                    pass
        else:
            # afficher les lignes
            for idx, (n, m, b) in enumerate(self.facture_rows):
                row = self.factures_ui_start + idx
                n.grid(row=row, column=0, padx=20, pady=6, sticky="w")
                m.grid(row=row, column=1, padx=20, pady=6, sticky="w")
                b.grid(row=row, column=2, padx=10, pady=6, sticky="w")

    # ----------------- CHARGER UN BON EXISTANT ----------------- #

    def load_bon(self, bon):
        """Remplit l'UI avec les données du bon existant et charge ses factures."""
        # mapping champs -> indices de la table bons_de_commande
        mapping = {
            "ID du bon": bon[1],
            "Année comptable": bon[2],
            "N° du bon": bon[3],
            "Montant engagé": str(bon[4]),
            "Fournisseur": bon[5],
            "Imputation (Art.: 330/12402-02)": bon[6],
            "Description": bon[14],
            "Commentaire": bon[15]
        }
        for key, val in mapping.items():
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, str(val) if val is not None else "")

        # checkboxs
        self.checkboxes["Envoyé à la ville"].set(bon[7])
        self.checkboxes["Envoyé à l'entreprise"].set(bon[8])
        self.checkboxes["Commande livrée"].set(bon[9])

        # Récupère les factures liées au bon (table factures)
        factures = fetch_factures_by_bon(bon[0])
        # si il y a au moins une facture, on coche "Facture" et on affiche les lignes
        if factures:
            self.checkboxes["Facture"].select()
            # ajouter chaque facture comme une ligne éditable
            for f in factures:
                # f = (id, id_bon, num_facture, montant_facture)
                num = f[2] or ""
                montant = f[3] or ""
                self._ui_add_facture(num=num, montant=montant)
            # afficher les lignes
            self._update_facture_ui()
        else:
            # aucun facture existante: décocher et masquer
            self.checkboxes["Facture"].deselect()
            self._update_facture_ui()

    # ----------------- FOCUS UTIL ----------------- #

    def focus_next(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    # ----------------- ENREGISTRER ----------------- #

    def enregistrer(self):
        """Récupère les données de l'UI, enregistre le bon, puis (re)crée les factures assoc."""
        try:
            # Récupérer données principales
            data = {key: entry.get().strip() for key, entry in self.entries.items()}
            checks = {key: cb.get() for key, cb in self.checkboxes.items()}

            # Récupérer factures UI
            factures_to_save = []
            if checks.get("Facture") == 1:
                for (num_entry, montant_entry, _) in self.facture_rows:
                    num = num_entry.get().strip()
                    montant_txt = montant_entry.get().strip()
                    if not num and not montant_txt:
                        continue  # ignorer ligne vide
                    try:
                        montant_val = float(montant_txt.replace(",", ".")) if montant_txt else 0.0
                    except ValueError:
                        messagebox.showerror("Erreur", f"Montant facture invalide : '{montant_txt}'")
                        return
                    factures_to_save.append((num, montant_val))

            # Vérifications montants
            try:
                montant_engage = float(data["Montant engagé"].replace(",", "."))
                if montant_engage < 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Erreur", "Veuillez entrer un Montant engagé valide et positif.")
                self.entries["Montant engagé"].focus()
                return

            total_factures = sum(m for _, m in factures_to_save) if factures_to_save else 0.0
            montant_restant = montant_engage - total_factures

            # Préparer tuple pour insert/update (respecte la signature actuelle de insert_bon/update_bon)
            # On met en colonne numero_facture le premier numéro (ou ''), montant_facture la somme (redondant mais existant dans la table)
            premier_num = factures_to_save[0][0] if factures_to_save else ""
            total_montant_facture = total_factures

            insert_tuple = (
                data["ID du bon"],
                data["Année comptable"],
                data["N° du bon"],
                montant_engage,
                data["Fournisseur"],
                data["Imputation (Art.: 330/12402-02)"],
                checks.get("Envoyé à la ville", 0),
                checks.get("Envoyé à l'entreprise", 0),
                checks.get("Commande livrée", 0),
                1 if factures_to_save else 0,   # valeur facture (indicateur)
                premier_num,
                total_montant_facture,
                montant_restant,
                data["Description"],
                data["Commentaire"]
            )

            # --- INSERER ou METTRE A JOUR le bon ---
            if self.bon is None:
                # nouvel enregistrement
                insert_bon(insert_tuple)
                # récupérer le bon inséré : on utilise fetch_bon(numero_bon) et prend le dernier matching
                candidates = fetch_bon(insert_tuple[2])
                if not candidates:
                    messagebox.showwarning("Attention", "Le bon a été inséré mais impossible de retrouver son ID pour lier les factures.")
                    self.clear_fields()
                    return
                # prendre le dernier (le plus récent)
                inserted = candidates[-1]
                bon_id = inserted[0]
            else:
                # mise à jour
                bon_id = self.bon[0]
                # update_bon attend un tuple avec les mêmes champs + id à la fin
                update_tuple = insert_tuple + (bon_id,)
                update_bon(update_tuple)

            # --- (Re)créer les factures liées dans la table factures ---
            # Supprimer d'abord les factures existantes pour ce bon (si existent)
            try:
                with sqlite3.connect("bons.db") as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM factures WHERE id_bon=?", (bon_id,))
                    conn.commit()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de nettoyer les factures existantes : {e}")
                return

            # Insérer les factures présentes dans l'UI
            for num, montant in factures_to_save:
                add_facture(bon_id, num, montant)

            # Recalculer montants stockés dans bons_de_commande (montant_facture, montant_restant)
            try:
                update_montants_bon(bon_id)
            except Exception:
                # si update_montants_bon manquait, on peut recalculer manuellement (fallback)
                try:
                    with sqlite3.connect("bons.db") as conn:
                        cur = conn.cursor()
                        cur.execute("SELECT SUM(montant_facture) FROM factures WHERE id_bon=?", (bon_id,))
                        total_fact = cur.fetchone()[0] or 0.0
                        restant = montant_engage - total_fact
                        cur.execute("UPDATE bons_de_commande SET montant_facture=?, montant_restant=? WHERE id=?", (total_fact, restant, bon_id))
                        conn.commit()
                except Exception:
                    pass

            # Feedback utilisateur
            if self.bon is None:
                messagebox.showinfo("Succès", "Bon de commande enregistré avec succès.")
                self.clear_fields()
            else:
                messagebox.showinfo("Succès", "Bon de commande mis à jour avec succès.")
                # fermer la fenêtre et demander refresh dans la fenêtre parent si disponible
                try:
                    if hasattr(self.master, "afficher_tous"):
                        self.master.afficher_tous()
                except Exception:
                    pass
                self.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, "end")
        for cb in self.checkboxes.values():
            cb.deselect()
        # supprimer lignes factures UI
        for (n, m, b) in list(self.facture_rows):
            try:
                n.destroy(); m.destroy(); b.destroy()
            except Exception:
                pass
        self.facture_rows = []
        self._update_facture_ui()

    def retour_menu(self):
        self.destroy()
        try:
            if hasattr(self.master, "deiconify"):
                self.master.deiconify()
        except Exception:
            pass
