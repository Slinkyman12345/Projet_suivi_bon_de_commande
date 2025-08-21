import os
import shutil
import sqlite3
import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class GestionTechniqueWindow(ctk.CTkToplevel):
    LOGS_PAGE_SIZE = 20  # Nombre de logs par page

    def __init__(self, parent, bons_db_path="bons.db", tech_db_path="gestion_technique.db"):
        super().__init__(parent)
        self.title("Gestion Technique")
        self.geometry("950x850")
        self.resizable(False, False)

        self.parent = parent
        self.bons_db_path = bons_db_path
        self.tech_db_path = tech_db_path

        self.current_logs_page = 0  # Pagination des logs

        # Initialisation base logs technique
        self.init_tech_db()

        # --- UI ---
        self._build_ui()

        # Chargement initial
        self.load_dashboard()
        self.load_logs()

    def _build_ui(self):
        # Dashboard frame
        dash_frame = ctk.CTkFrame(self, corner_radius=12)
        dash_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(dash_frame, text="Dashboard", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(10, 15))
        self.bons_count_label = ctk.CTkLabel(dash_frame, text="Chargement...", font=ctk.CTkFont(size=18))
        self.bons_count_label.pack(pady=(0, 5))

        # Nouveau label pour le montant restant total
        self.total_remaining_label = ctk.CTkLabel(dash_frame, text="Calcul en cours...", font=ctk.CTkFont(size=18))
        self.total_remaining_label.pack(pady=(0, 15))

        # Sauvegarde / restauration frame
        backup_frame = ctk.CTkFrame(self, corner_radius=12)
        backup_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(backup_frame, text="Sauvegarde et Restauration", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        btn_save = ctk.CTkButton(backup_frame, text="Sauvegarder la base de données", command=self.backup_database)
        btn_save.pack(pady=8)

        btn_restore = ctk.CTkButton(backup_frame, text="Restaurer la base de données", command=self.restore_database)
        btn_restore.pack(pady=8)

        # Logs frame
        logs_frame = ctk.CTkFrame(self, corner_radius=12)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(logs_frame, text="Historique des logs", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Textbox readonly pour afficher logs
        self.logs_textbox = ctk.CTkTextbox(logs_frame, width=900, height=350, font=ctk.CTkFont(size=12))
        self.logs_textbox.pack(padx=10, pady=5)
        self.logs_textbox.configure(state="disabled")

        # Pagination logs
        pagination_frame = ctk.CTkFrame(logs_frame)
        pagination_frame.pack(pady=(5, 10))

        self.btn_prev_page = ctk.CTkButton(pagination_frame, text="<< Page précédente", command=self.prev_logs_page)
        self.btn_prev_page.grid(row=0, column=0, padx=10)

        self.page_label = ctk.CTkLabel(pagination_frame, text="Page 1")
        self.page_label.grid(row=0, column=1, padx=10)

        self.btn_next_page = ctk.CTkButton(pagination_frame, text="Page suivante >>", command=self.next_logs_page)
        self.btn_next_page.grid(row=0, column=2, padx=10)

        # Bouton retour menu principal
        btn_return = ctk.CTkButton(self, text="← Retour au menu principal", command=self.return_to_menu, fg_color="#6c757d", hover_color="#5a6268")
        btn_return.pack(pady=15)

    def init_tech_db(self):
        # Crée la base logs si pas existante avec la structure complète souhaitée
        conn = sqlite3.connect(self.tech_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                utilisateur TEXT,
                action TEXT,
                num_externe TEXT,
                num_interne TEXT,
                raison TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_action(self, utilisateur, action, num_externe=None, num_interne=None, raison=None):
        try:
            conn = sqlite3.connect(self.tech_db_path)
            cursor = conn.cursor()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """
                INSERT INTO logs (date, utilisateur, action, num_externe, num_interne, raison)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (now, utilisateur, action, num_externe, num_interne, raison)
            )
            conn.commit()

            # Supprime les anciens logs si > 500
            cursor.execute("SELECT COUNT(*) FROM logs")
            count = cursor.fetchone()[0]
            if count > 500:
                surplus = count - 500
                cursor.execute(f"DELETE FROM logs WHERE id IN (SELECT id FROM logs ORDER BY date ASC LIMIT {surplus})")
                conn.commit()

            conn.close()
        except Exception as e:
            print(f"Erreur lors de l'écriture du log : {e}")

    def get_bons_count(self):
        try:
            conn = sqlite3.connect(self.bons_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bons_de_commande")
            count = cursor.fetchone()[0]
            conn.close()
            return count or 0
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de récupérer le nombre de bons : {e}")
            return 0

    def get_total_remaining_amount(self):
        """Calcule la somme du montant restant de tous les bons."""
        try:
            conn = sqlite3.connect(self.bons_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(montant_restant) FROM bons_de_commande")
            total = cursor.fetchone()[0]
            conn.close()
            return total or 0.0
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de calculer le montant restant : {e}")
            return 0.0

    def load_dashboard(self):
        count = self.get_bons_count()
        total_remaining = self.get_total_remaining_amount()
        self.bons_count_label.configure(text=f"Nombre total de bons encodés : {count}")
        self.total_remaining_label.configure(text=f"Montant restant total : {total_remaining:,.2f} €")

    def backup_database(self):
        dest_path = filedialog.asksaveasfilename(defaultextension=".sqlite", filetypes=[("Fichiers SQLite", "*.sqlite")])
        if dest_path:
            try:
                shutil.copy(self.bons_db_path, dest_path)
                messagebox.showinfo("Sauvegarde", "Sauvegarde réalisée avec succès.")
                self.log_action("SYSTEM", f"Sauvegarde base bons vers {dest_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

    def restore_database(self):
        source_path = filedialog.askopenfilename(filetypes=[("Fichiers SQLite", "*.sqlite")])
        if source_path:
            try:
                shutil.copy(source_path, self.bons_db_path)
                messagebox.showinfo("Restauration", "Restauration réalisée avec succès. Redémarrez l'application.")
                self.log_action("SYSTEM", f"Restauration base bons depuis {source_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la restauration : {e}")

    def load_logs(self):
        try:
            offset = self.current_logs_page * self.LOGS_PAGE_SIZE
            conn = sqlite3.connect(self.tech_db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT date, utilisateur, action, num_externe, num_interne, raison
                FROM logs
                ORDER BY id DESC
                LIMIT ? OFFSET ?
                """,
                (self.LOGS_PAGE_SIZE, offset)
            )
            logs = cursor.fetchall()

            # Compte total logs pour la pagination
            cursor.execute("SELECT COUNT(*) FROM logs")
            total_logs = cursor.fetchone()[0]
            conn.close()

            # Mise à jour pagination boutons
            max_page = (total_logs - 1) // self.LOGS_PAGE_SIZE if total_logs > 0 else 0
            self.btn_prev_page.configure(state="normal" if self.current_logs_page > 0 else "disabled")
            self.btn_next_page.configure(state="normal" if self.current_logs_page < max_page else "disabled")
            self.page_label.configure(text=f"Page {self.current_logs_page + 1} / {max_page + 1}")

            # Affichage logs
            self.logs_textbox.configure(state="normal")
            self.logs_textbox.delete("1.0", ctk.END)
            if not logs:
                self.logs_textbox.insert(ctk.END, "Aucun log disponible.\n")
            else:
                for date, utilisateur, action, num_externe, num_interne, raison in logs:
                    log_line = f"[{date}] {utilisateur} : {action}"
                    details = []
                    if num_externe:
                        details.append(f"N° externe: {num_externe}")
                    if num_interne:
                        details.append(f"N° interne: {num_interne}")
                    if raison:
                        details.append(f"Raison: {raison}")
                    if details:
                        log_line += " (" + " | ".join(details) + ")"
                    self.logs_textbox.insert(ctk.END, log_line + "\n")
            self.logs_textbox.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des logs : {e}")

    def next_logs_page(self):
        self.current_logs_page += 1
        self.load_logs()

    def prev_logs_page(self):
        if self.current_logs_page > 0:
            self.current_logs_page -= 1
            self.load_logs()

    def return_to_menu(self):
        self.destroy()
        if self.parent:
            self.parent.deiconify()  # Remet la fenêtre principale visible


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x200")

    def open_gestion_tech():
        root.withdraw()
        GestionTechniqueWindow(root)

    btn = ctk.CTkButton(root, text="Ouvrir Gestion Technique", command=open_gestion_tech)
    btn.pack(pady=50)

    root.mainloop()
