# gui/changelog_window.py

import customtkinter as ctk
import time

class ChangelogWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Historique des Versions")
        self.geometry("950x820")
        self.resizable(False, False)

        # Prend automatiquement le thème actuel
        self.configure(fg_color=ctk.ThemeManager.theme["CTk"]["fg_color"])

        self.attributes("-alpha", 0.0)
        self.fade_in()

        # Titre
        ctk.CTkLabel(
            self,
            text="📝 Journal des Mises à Jour",
            font=("Segoe UI", 26, "bold")
        ).pack(pady=(20, 5))

        # Conteneur principal
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(expand=True, fill="both", padx=20)

        # Scrollable
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.main_container,
            corner_radius=12,
            width=700,
            height=480
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Changelog contenu
        changelog = {
            "Version 1.0.6": [
                "Correction de bugs lié à la modification du bon de commande",
                "Correction de bugs lié au menu"
            ],

            "Version 1.0.5": [
                "Ajout d'une partie gestion technique",
                "Ajout de logs de suppresion des bons de commandes",
                "Ajout de logs de sauvegarde et restauration de la DB",
                "Ajout de la possibilité de sauvegarder et de restaurer la base de donnée",
                "Ajout du fait de donnée une raison pour la suppresion du bon de commande",
                "Ajout du nombre de bon de commandes encodés",
                "Corrections de bugs majeurs et mineurs",
                "Ajout du calcul du montant restant des bons de commandes"
            ],

            "Version 1.0.4": [
                "Correction du bug de changement de jour et nuit pour la modification du bon de commande",
                "Améliorations graphiques de différentes interfaces afin de rendre cela plus moderne",
            ],

            "Version 1.0.3": [
                "Ajout du mode jour et mode nuit activable depuis le menu",
                "Modification du logo. Passé du logo police au logo de la zone",
                "Correction de bugs mineurs"
            ],

            "Version 1.0.2": [
                "Correction de bugs mineurs",
                "Modification de certains rendus",
                "Ajout du tri par ID bon, N° de bon dans la visualisation de bons",
                "Ajout du tri ascendant/descendant lorsqu'on sélectionne plusieurs fois le même critère",
                "Optimisation de la fonction de tri",
                "Ajout du bouton pour aller vers l'ajout de facture /!\\ non implémenté pour le moment"
            ],
            "Version 1.0.1": [
                "Ajout d'une barre de défilement pour les vues longues",
                "Boutons toujours visibles en bas de page",
                "Pagination automatique selon la taille de la fenêtre",
                "Fenêtre de changelog ajoutée",
                "Modification du visuel des pages pour le rendre moins brut"
            ],
            "Version 1.0.0": [
                "Ajout de la fonctionnalité d'encodage des bons de commande",
                "Visualisation des bons de commandes avec filtre et tri",
                "Export des résultats vers Excel",
                "Ajout de la fonctionnalité de modification des bons de commande",
                "ID du bon encodable par l'utilisateur",
                "Clé primaire changée et gérée par le programme",
                "Correction de différents bugs",
                "Correction d'erreurs non prises en charge"
            ]
        }

        # Affichage
        for version, features in changelog.items():
            version_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=version,
                font=("Segoe UI", 18, "bold")
            )
            version_label.pack(anchor="w", padx=20, pady=(20, 5))

            for item in features:
                ctk.CTkLabel(
                    self.scrollable_frame,
                    text=f"• {item}",
                    font=("Segoe UI", 14)
                ).pack(anchor="w", padx=40)

        # Footer
        self.footer_frame = ctk.CTkFrame(self)
        self.footer_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkButton(
            self.footer_frame,
            text="❌ Fermer",
            command=self.close_window,
            font=("Segoe UI", 16, "bold"),
            width=240,
            height=55,
            corner_radius=12
        ).pack(pady=10)

    def fade_in(self):
        for i in range(0, 21):
            alpha = i / 20.0
            self.attributes("-alpha", alpha)
            self.update()
            time.sleep(0.015)

    def close_window(self):
        self.destroy()
        self.master.deiconify()
