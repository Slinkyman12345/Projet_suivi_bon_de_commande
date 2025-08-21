# gui/search_window.py

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import fetch_filtered, fetch_all, delete_bon, fetch_bon_by_id
from export import export_filtered_to_excel
from gui.edit_window import EditWindow
from PIL import Image
import datetime
import sqlite3
import os

class ReasonDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="Raison de suppression", width=500, height=300):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)  # Reste au-dessus de la fenêtre parent
        self.grab_set()  # Modalité : bloque les autres fenêtres
        self.reason = None

        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        label = ctk.CTkLabel(frame, text="Veuillez indiquer la raison de la suppression :", anchor="w", font=("Segoe UI", 14))
        label.pack(fill="x", pady=(0,10))

        self.textbox = tk.Text(frame, height=8, font=("Segoe UI", 12), wrap="word")
        self.textbox.pack(fill="both", expand=True)

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=15, fill="x")

        btn_ok = ctk.CTkButton(btn_frame, text="OK", width=100, command=self.on_ok)
        btn_ok.pack(side="right", padx=(0,10))
        btn_cancel = ctk.CTkButton(btn_frame, text="Annuler", width=100, command=self.on_cancel)
        btn_cancel.pack(side="right", padx=(0,10))

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

        self.textbox.focus_set()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()

        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        self.geometry(f"+{x}+{y}")

    def on_ok(self):
        texte = self.textbox.get("1.0", "end").strip()
        if not texte:
            messagebox.showerror("Erreur", "La raison ne peut pas être vide.")
            return
        self.reason = texte
        self.destroy()

    def on_cancel(self):
        self.reason = None
        self.destroy()

    def show(self):
        self.wait_window()
        return self.reason


class SearchWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Visualisation des Bons de Commande")
        self.geometry("1300x850")
        self.resizable(True, True)

        self.configure(fg_color=ctk.ThemeManager.theme["CTkToplevel"]["fg_color"])

        self.page = 0
        self.items_per_page = 20
        self.resultats = []

        self.tri_inverse = False
        self.tri_actuel = None

        import getpass
        self.user = getpass.getuser()

        self.create_widgets()
        self.afficher_tous()

    def create_widgets(self):
        logo_path = os.path.join("assets", "polnam_logo.png")
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(150, 150))
            logo_label = ctk.CTkLabel(self, image=logo_img, text="")
            logo_label.image = logo_img
            logo_label.place(x=10, y=10)

        self.title_label = ctk.CTkLabel(self, text="Visualisation des Bons de Commande", font=("Segoe UI", 26, "bold"))
        self.title_label.pack(pady=(20, 10))

        filtre_frame = ctk.CTkFrame(self, corner_radius=10)
        filtre_frame.pack(pady=10)

        self.annee_entry = ctk.CTkEntry(filtre_frame, placeholder_text="Année", width=120)
        self.annee_entry.grid(row=0, column=0, padx=10, pady=10)

        self.fournisseur_entry = ctk.CTkEntry(filtre_frame, placeholder_text="Fournisseur", width=150)
        self.fournisseur_entry.grid(row=0, column=1, padx=10)

        self.num_entry = ctk.CTkEntry(filtre_frame, placeholder_text="N° Bon", width=120)
        self.num_entry.grid(row=0, column=2, padx=10)

        ctk.CTkButton(filtre_frame, text="🔍 Rechercher", command=self.rechercher, width=140).grid(row=0, column=3, padx=10)
        ctk.CTkButton(filtre_frame, text="↺ Réinitialiser", command=self.afficher_tous, width=140).grid(row=0, column=4, padx=10)

        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=5)

        ctk.CTkButton(action_frame, text="⬇️ Exporter Excel", command=self.exporter).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="⬅️ Retour Menu", command=self.retour_menu).pack(side="left", padx=10)

        tri_options = ["ID Bon", "Année", "N° Bon", "Montant", "Livré", "Facturé"]
        self.sort_criteria = ctk.CTkComboBox(action_frame, values=tri_options, command=self.trier, width=200)
        self.sort_criteria.set("Trier par...")
        self.sort_criteria.pack(side="left", padx=10)

        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10)

        style = ttk.Style()
        style.theme_use("default")

        appearance = ctk.get_appearance_mode()
        is_dark = appearance == "Dark"

        bg = "#2b2b2b" if is_dark else "#ffffff"
        fg = "#ffffff" if is_dark else "#000000"
        heading_bg = "#3e3e3e" if is_dark else "#f2f2f2"
        selected_bg = "#44475a" if is_dark else "#cce5ff"

        style.configure("Treeview",
                        background=bg,
                        fieldbackground=bg,
                        foreground=fg,
                        font=("Segoe UI", 11),
                        rowheight=30)

        style.configure("Treeview.Heading",
                        background=heading_bg,
                        foreground=fg,
                        font=("Segoe UI", 11, "bold"))

        style.map("Treeview",
                  background=[("selected", selected_bg)],
                  foreground=[("selected", "#ffffff" if is_dark else "#000000")])

        self.tree = ttk.Treeview(tree_frame, columns=[str(i) for i in range(1, 17)], show='headings')

        headers = [
            "ID", "ID Bon", "Année", "N° Bon", "Montant", "Fournisseur", "Imputation",
            "Ville", "Entreprise", "Livré", "Facturé", "N° Facture",
            "Mt Facture", "Restant", "Description", "Commentaire"
        ]
        for i, h in enumerate(headers):
            self.tree.heading(str(i + 1), text=h)
            width = 100 if i in [0, 1, 2, 3] else 150
            self.tree.column(str(i + 1), width=width, anchor="center")

        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        y_scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.selection_action)

        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(side="bottom", fill="x", pady=10)

        self.page_label = ctk.CTkLabel(bottom_frame, text="", font=("Segoe UI", 14))
        self.page_label.pack(side="left", padx=20)

        ctk.CTkButton(bottom_frame, text="⬅️ Page précédente", command=self.page_precedente, width=160).pack(side="left", padx=10)
        ctk.CTkButton(bottom_frame, text="➡️ Page suivante", command=self.page_suivante, width=160).pack(side="left", padx=10)

        ctk.CTkButton(
            bottom_frame,
            text="🗑️ Supprimer le bon sélectionné",
            command=self.supprimer_selection,
            fg_color="#d9534f",
            hover_color="#c9302c",
            text_color="white"
        ).pack(side="right", padx=20)

    def retour_menu(self):
        self.destroy()
        self.master.deiconify()

    def oui_non(self, val):
        return "oui" if val == 1 else "non"

    def afficher_tous(self):
        self.resultats = fetch_all()
        self.page = 0
        self.afficher_resultats()

    def afficher_resultats(self):
        self.tree.delete(*self.tree.get_children())

        start = self.page * self.items_per_page
        end = start + self.items_per_page
        page_data = self.resultats[start:end]

        for row in page_data:
            row_mod = list(row)
            row_mod[3] = f"BONPOL/{row_mod[3]}"
            for i in [7, 8, 9, 10]:
                row_mod[i] = self.oui_non(row_mod[i])
            for i in [4, 12, 13]:
                row_mod[i] = f"{row_mod[i]} €" if row_mod[i] else ""

            # Gestion des factures multiples
            if row_mod[11]:  # N° Facture (colonne 12)
                if isinstance(row_mod[11], str):
                    factures = [f.strip() for f in row_mod[11].split(',')]
                    row_mod[11] = "\n".join(factures)
                elif isinstance(row_mod[11], list):
                    row_mod[11] = "\n".join(row_mod[11])

            self.tree.insert("", "end", values=row_mod)

        total_pages = max(1, (len(self.resultats) - 1) // self.items_per_page + 1)
        self.page_label.configure(text=f"Page {self.page + 1} sur {total_pages}")

    def page_suivante(self):
        total_pages = max(1, (len(self.resultats) - 1) // self.items_per_page + 1)
        if self.page < total_pages - 1:
            self.page += 1
            self.afficher_resultats()

    def page_precedente(self):
        if self.page > 0:
            self.page -= 1
            self.afficher_resultats()

    def trier(self, critere):
        index_map = {
            "ID Bon": 1, "Année": 2, "N° Bon": 3, "Montant": 4,
            "Livré": 9, "Facturé": 10
        }
        if critere not in index_map:
            return
        col_index = index_map[critere]
        self.resultats.sort(key=lambda x: x[col_index], reverse=self.tri_inverse)
        if self.tri_actuel == critere:
            self.tri_inverse = not self.tri_inverse
        else:
            self.tri_inverse = False
        self.tri_actuel = critere
        self.afficher_resultats()

    def rechercher(self):
        annee = self.annee_entry.get().strip()
        fournisseur = self.fournisseur_entry.get().strip()
        num_bon = self.num_entry.get().strip()
        self.resultats = fetch_filtered(annee, fournisseur, num_bon)
        self.page = 0
        self.afficher_resultats()

    def exporter(self):
        if not self.resultats:
            messagebox.showwarning("Attention", "Aucun résultat à exporter.")
            return
        filename = f"bons_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", initialfile=filename,
                                                filetypes=[("Excel Files", "*.xlsx")])
        if filepath:
            export_filtered_to_excel(self.resultats, filepath)
            messagebox.showinfo("Export", f"Export terminé : {filepath}")

    def selection_action(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = self.tree.item(selected_item)
        id_bon = item['values'][0]
        bon = fetch_bon_by_id(id_bon)
        if bon:
            EditWindow(self, bon_id=id_bon, parent_window=self)

    def supprimer_selection(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez sélectionner un bon à supprimer.")
            return
        item = self.tree.item(selected_item)
        id_bon = item['values'][0]

        reason_dialog = ReasonDialog(self)
        raison = reason_dialog.show()
        if not raison:
            return

        if messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer le bon ID {id_bon} ?"):
            delete_bon(id_bon)
            self.log_action(id_bon, raison)
            messagebox.showinfo("Suppression", f"Bon ID {id_bon} supprimé avec succès.")
            self.afficher_tous()

    def log_action(self, bon_id, reason):
        try:
            conn = sqlite3.connect("db.sqlite3")
            c = conn.cursor()
            c.execute("""
                INSERT INTO logs (user, action, bon_id, reason, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (self.user, "Suppression", bon_id, reason, datetime.datetime.now()))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Erreur de log", f"Erreur lors de l'enregistrement du log : {e}")

    def refresh_data(self):
        """Recharge les données et met à jour l'affichage"""
        try:
            # Recharger les données depuis la base 
            self.resultats = fetch_all()  

            # Remise à la première page (optionnel)
            self.page = 0

            # Rafraîchir l'affichage
            self.afficher_resultats()

            print("✅ Données rechargées avec succès")

        except Exception as e:
            print(f"❌ Erreur refresh_data() : {e}")
