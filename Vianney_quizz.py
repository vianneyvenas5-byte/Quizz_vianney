import json
import math
import random
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")

COLOR_BG      = "#0d0d0d"
COLOR_ACCENT  = "#2ecc71"
COLOR_WRONG   = "#e74c3c"
COLOR_DEFAULT = "#1a3a5c"
COLOR_HOVER   = "#1f5080"
COLOR_TEXT    = "#ffffff"
COLOR_SUBTEXT = "#aaaaaa"

NIVEAUX = ["Facile", "Moyen", "Difficile"]
TEMPS_PAR_QUESTION = 20.0


class VianneyQuiz(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("VIANNEY QUIZ")
        self.geometry("1100x750")
        self.minsize(900, 650)
        self.configure(fg_color=COLOR_BG)

        self.score           = 0
        self.streak          = 0
        self.current_q_index = 0
        self.seconds_left    = TEMPS_PAR_QUESTION
        self.timer_id        = None
        self.repondu         = False   # evite double appel check_answer

        self.questions  = []
        self.categories = []
        self.data       = {}           # { cat: { niveau: [q, ...] } }

        if self.charger_data():
            self.afficher_accueil()

    # ═══════════════════════════════════════════════════════════════════ #
    #  CHARGEMENT & NORMALISATION                                        #
    # ═══════════════════════════════════════════════════════════════════ #
    def charger_data(self):
        fichiers = {
            "Informatique": "informatique.json",
            "Manga":        "manga.json",
            "Musique":      "musique.json",
            "Physique":     "physique.json",
            "Science":      "science.json",
            "Sport":        "sport.json",
        }
        try:
            for cat, fichier in fichiers.items():
                with open(fichier, encoding="utf-8") as f:
                    raw = json.load(f)
                self.data[cat] = self._normaliser(raw)
            self.categories = list(self.data.keys())
            return True
        except FileNotFoundError as e:
            messagebox.showerror(
                "Fichier manquant",
                f"Fichier introuvable : {e.filename}\n\n"
                "Place tous les JSON dans le meme dossier que quiz.py."
            )
            self.destroy()
            return False
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            self.destroy()
            return False

    def _normaliser(self, raw):
        """
        raw peut etre :
          - dict { "Facile": [...], "Moyen": [...], "Difficile": [...] }
          - list  [...]
        Retourne { "Facile": [...], "Moyen": [...], "Difficile": [...], "Tout": [...] }
        Chaque question : { question:str, options:[str,str,str,str], answer:str }
        """
        result = {n: [] for n in NIVEAUX}

        if isinstance(raw, dict):
            source = raw
        elif isinstance(raw, list):
            source = {"Facile": raw}
        else:
            return result

        for niveau, qs in source.items():
            if niveau not in result:
                continue
            seen = set()
            for q in qs:
                if not isinstance(q, dict):
                    continue
                opts = q.get("options", {})
                if isinstance(opts, dict):
                    opts_list = list(opts.values())
                elif isinstance(opts, list):
                    opts_list = opts
                else:
                    continue

                question_text = q.get("question", "").strip()
                answer        = q.get("answer", "").strip()

                # deduplication par (texte, reponse)
                key = (question_text, answer)
                if key in seen:
                    continue
                seen.add(key)

                result[niveau].append({
                    "question": question_text,
                    "options":  opts_list,
                    "answer":   answer,
                })

        return result

    # ═══════════════════════════════════════════════════════════════════ #
    #  UTILITAIRES                                                       #
    # ═══════════════════════════════════════════════════════════════════ #
    def nettoyer_ecran(self):
        self._annuler_timer()
        for w in self.winfo_children():
            w.destroy()

    def _annuler_timer(self):
        if self.timer_id is not None:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def _btn_retour(self, parent):
        """Cree un bouton retour standard."""
        ctk.CTkButton(
            parent,
            text="← Retour",
            command=self.afficher_accueil,
            fg_color="transparent",
            hover_color="#1a1a1a",
            border_width=1,
            border_color="#444444",
            text_color=COLOR_SUBTEXT,
            font=("Arial", 13),
            width=110,
            height=32,
        ).pack(side="left")

    # ═══════════════════════════════════════════════════════════════════ #
    #  ECRAN D'ACCUEIL                                                   #
    # ═══════════════════════════════════════════════════════════════════ #
    def afficher_accueil(self):
        self.nettoyer_ecran()

        # Fond principal
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(expand=True, fill="both")

        center = ctk.CTkFrame(main, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(center, text="🎭", font=("Arial", 90)).pack()

        ctk.CTkLabel(
            center, text="VIANNEY QUIZ",
            font=("Arial", 42, "bold"), text_color=COLOR_ACCENT,
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            center, text="Choisis ta categorie et ton niveau",
            font=("Arial", 14), text_color=COLOR_SUBTEXT,
        ).pack(pady=(0, 30))

        # Categorie
        ctk.CTkLabel(center, text="Categorie", font=("Arial", 13),
                     text_color=COLOR_SUBTEXT).pack(anchor="w")
        self.cat_var = ctk.StringVar(value=self.categories[0])
        ctk.CTkComboBox(
            center, values=self.categories,
            variable=self.cat_var, width=340, height=40,
            font=("Arial", 15), dropdown_font=("Arial", 14),
            button_color=COLOR_ACCENT, button_hover_color="#27ae60",
        ).pack(pady=(4, 16))

        # Niveau
        ctk.CTkLabel(center, text="Difficulte", font=("Arial", 13),
                     text_color=COLOR_SUBTEXT).pack(anchor="w")
        self.diff_var = ctk.StringVar(value="Tout")
        ctk.CTkComboBox(
            center, values=["Tout"] + NIVEAUX,
            variable=self.diff_var, width=340, height=40,
            font=("Arial", 15), dropdown_font=("Arial", 14),
            button_color=COLOR_ACCENT, button_hover_color="#27ae60",
        ).pack(pady=(4, 30))

        ctk.CTkButton(
            center, text="▶   JOUER",
            command=self.demarrer_jeu,
            fg_color=COLOR_ACCENT, hover_color="#27ae60",
            text_color="#000000", font=("Arial", 18, "bold"),
            width=340, height=54, corner_radius=12,
        ).pack()

    # ═══════════════════════════════════════════════════════════════════ #
    #  DEMARRAGE                                                         #
    # ═══════════════════════════════════════════════════════════════════ #
    def demarrer_jeu(self):
        cat   = self.cat_var.get()
        diff  = self.diff_var.get()
        niveaux_data = self.data.get(cat, {})

        if diff == "Tout":
            pool = []
            for n in NIVEAUX:
                pool.extend(niveaux_data.get(n, []))
        else:
            pool = list(niveaux_data.get(diff, []))

        if not pool:
            messagebox.showwarning("Vide",
                "Aucune question pour cette combinaison.\n"
                "Verifie tes fichiers JSON.")
            return

        # Melange + deduplication finale par texte de question
        seen = set()
        unique = []
        for q in pool:
            if q["question"] not in seen:
                seen.add(q["question"])
                unique.append(q)

        random.shuffle(unique)
        self.questions       = unique
        self.current_q_index = 0
        self.score           = 0
        self.streak          = 0
        self.repondu         = False

        self.setup_ui_jeu()
        self.show_question()

    # ═══════════════════════════════════════════════════════════════════ #
    #  INTERFACE DE JEU                                                  #
    # ═══════════════════════════════════════════════════════════════════ #
    def setup_ui_jeu(self):
        self.nettoyer_ecran()

        # ── Barre du haut ────────────────────────────────────────────── #
        top = ctk.CTkFrame(self, fg_color="#111111", height=56, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)

        inner_top = ctk.CTkFrame(top, fg_color="transparent")
        inner_top.pack(fill="both", expand=True, padx=20)

        self._btn_retour(inner_top)   # ← BOUTON RETOUR

        self.lbl_score = ctk.CTkLabel(
            inner_top, text="Score : 0",
            font=("Arial", 20, "bold"), text_color=COLOR_ACCENT,
        )
        self.lbl_score.pack(side="left", padx=20)

        self.lbl_streak = ctk.CTkLabel(
            inner_top, text="🔥  0",
            font=("Arial", 18), text_color="#f39c12",
        )
        self.lbl_streak.pack(side="right", padx=10)

        self.lbl_progression = ctk.CTkLabel(
            inner_top, text="",
            font=("Arial", 13), text_color=COLOR_SUBTEXT,
        )
        self.lbl_progression.pack(side="right", padx=10)

        # ── Zone centrale ────────────────────────────────────────────── #
        self.canvas_timer = tk.Canvas(
            self, width=110, height=110,
            bg=COLOR_BG, highlightthickness=0,
        )
        self.canvas_timer.pack(pady=(14, 0))

        self.lbl_question = ctk.CTkLabel(
            self, text="",
            font=("Arial", 21), wraplength=860,
            justify="center", text_color=COLOR_TEXT,
        )
        self.lbl_question.pack(pady=(14, 8), padx=60)

        # ── Grille 2×2 des boutons ───────────────────────────────────── #
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=60, pady=10)
        grid.columnconfigure((0, 1), weight=1)
        grid.rowconfigure((0, 1), weight=1)

        labels = ["A", "B", "C", "D"]
        self.btns = []
        for i in range(4):
            r, c = divmod(i, 2)
            btn = ctk.CTkButton(
                grid,
                text="",
                command=lambda x=i: self.check_answer(x),
                font=("Arial", 15),
                height=70,
                fg_color=COLOR_DEFAULT,
                hover_color=COLOR_HOVER,
                text_color=COLOR_TEXT,
                anchor="w",
                corner_radius=10,
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=8, pady=6)
            self.btns.append(btn)

    # ═══════════════════════════════════════════════════════════════════ #
    #  TIMER CIRCULAIRE                                                  #
    # ═══════════════════════════════════════════════════════════════════ #
    def _dessiner_timer(self):
        c = self.canvas_timer
        c.delete("all")
        ratio = max(self.seconds_left / TEMPS_PAR_QUESTION, 0)
        extent = 359.9 * ratio   # evite bug arc plein a 360
        color  = (COLOR_ACCENT if ratio > 0.5
                  else ("#f39c12" if ratio > 0.25
                  else COLOR_WRONG))
        c.create_oval(8, 8, 102, 102, outline="#2a2a2a", width=9)
        if extent > 0:
            c.create_arc(8, 8, 102, 102, start=90, extent=extent,
                         style="arc", outline=color, width=9)
        c.create_text(55, 55,
                      text=str(math.ceil(self.seconds_left)),
                      fill="white", font=("Arial", 24, "bold"))

    def update_timer(self):
        if self.seconds_left > 0:
            self.seconds_left = round(self.seconds_left - 0.1, 1)
            self._dessiner_timer()
            self.timer_id = self.after(100, self.update_timer)
        else:
            self.timer_id = None
            if not self.repondu:
                self.check_answer(-1)

    # ═══════════════════════════════════════════════════════════════════ #
    #  AFFICHAGE D'UNE QUESTION                                          #
    # ═══════════════════════════════════════════════════════════════════ #
    def show_question(self):
        if self.current_q_index >= len(self.questions):
            self.fin()
            return

        self.repondu = False

        # Reset boutons
        for btn in self.btns:
            btn.configure(
                fg_color=COLOR_DEFAULT,
                hover_color=COLOR_HOVER,
                state="normal",
                text="",
            )

        q    = self.questions[self.current_q_index]
        opts = q["options"]

        total = len(self.questions)
        self.lbl_progression.configure(
            text=f"Question {self.current_q_index + 1} / {total}"
        )
        self.lbl_question.configure(text=q["question"])

        prefixes = ["A  —  ", "B  —  ", "C  —  ", "D  —  "]
        for i in range(4):
            if i < len(opts):
                self.btns[i].configure(
                    text=prefixes[i] + opts[i],
                    state="normal",
                )
            else:
                self.btns[i].configure(text="", state="disabled")

        self.seconds_left = TEMPS_PAR_QUESTION
        self._annuler_timer()
        self.update_timer()

    # ═══════════════════════════════════════════════════════════════════ #
    #  VERIFICATION DE LA REPONSE                                        #
    # ═══════════════════════════════════════════════════════════════════ #
    def check_answer(self, idx):
        if self.repondu:    # evite double déclenchement timer + clic
            return
        self.repondu = True
        self._annuler_timer()

        q       = self.questions[self.current_q_index]
        correct = q["answer"]

        # Desactiver tous les boutons
        for btn in self.btns:
            btn.configure(state="disabled", hover_color=COLOR_DEFAULT)

        if idx == -1:
            # Temps ecoule
            self.streak = 0
        else:
            # Extraire le texte brut (sans prefix "A — ")
            raw_text = self.btns[idx].cget("text")
            chosen   = raw_text.split("  —  ", 1)[-1] if "  —  " in raw_text else raw_text

            if chosen == correct:
                self.score  += 100
                self.streak += 1
                self.btns[idx].configure(fg_color=COLOR_ACCENT)
            else:
                self.streak = 0
                self.btns[idx].configure(fg_color=COLOR_WRONG)

        # Toujours montrer la bonne reponse en vert
        for btn in self.btns:
            raw = btn.cget("text")
            val = raw.split("  —  ", 1)[-1] if "  —  " in raw else raw
            if val == correct:
                btn.configure(fg_color=COLOR_ACCENT)

        self.lbl_score.configure(text=f"Score : {self.score}")
        self.lbl_streak.configure(text=f"🔥  {self.streak}")

        self.current_q_index += 1
        self.after(1500, self.show_question)

    # ═══════════════════════════════════════════════════════════════════ #
    #  ECRAN DE FIN                                                      #
    # ═══════════════════════════════════════════════════════════════════ #
    def fin(self):
        self.nettoyer_ecran()

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(expand=True, fill="both")

        card = ctk.CTkFrame(main, fg_color="#111111", corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        total_q = len(self.questions)
        bonnes  = self.score // 100
        pct     = int(bonnes / total_q * 100) if total_q else 0

        emoji = "🏆" if pct >= 80 else ("👍" if pct >= 50 else "💪")

        ctk.CTkLabel(card, text=emoji, font=("Arial", 70)).pack(pady=(30, 0))

        ctk.CTkLabel(
            card, text="Fin de partie !",
            font=("Arial", 34, "bold"), text_color=COLOR_ACCENT,
        ).pack(pady=(8, 20))

        # Stats
        stats = ctk.CTkFrame(card, fg_color="#1a1a1a", corner_radius=12)
        stats.pack(padx=40, pady=10)

        rows = [
            ("Score",            f"{self.score} pts"),
            ("Bonnes reponses",  f"{bonnes} / {total_q}  ({pct}%)"),
            ("Meilleure serie",  f"{self.streak} 🔥"),
        ]
        for label, val in rows:
            row = ctk.CTkFrame(stats, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=6)
            ctk.CTkLabel(row, text=label, font=("Arial", 15),
                         text_color=COLOR_SUBTEXT).pack(side="left")
            ctk.CTkLabel(row, text=val, font=("Arial", 15, "bold"),
                         text_color=COLOR_TEXT).pack(side="right")

        # Boutons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=28)

        ctk.CTkButton(
            btn_row, text="🔄  Rejouer",
            command=self.demarrer_jeu,
            fg_color=COLOR_ACCENT, hover_color="#27ae60",
            text_color="#000000", font=("Arial", 15, "bold"),
            width=160, height=46, corner_radius=10,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="🏠  Accueil",
            command=self.afficher_accueil,
            fg_color="transparent", hover_color="#1a1a1a",
            border_width=1, border_color="#444444",
            text_color=COLOR_TEXT, font=("Arial", 15),
            width=160, height=46, corner_radius=10,
        ).pack(side="left", padx=8)


if __name__ == "__main__":
    app = VianneyQuiz()
    app.mainloop()