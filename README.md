# 🎭 Vianney Quiz

Quiz interactif multi-catégories avec interface graphique moderne.
Catégories : Informatique · Manga · Musique · Physique · Science · Sport
Niveaux : Facile · Moyen · Difficile · Tout

---

## 📁 Structure du projet

```
Quizz/
├── quiz.py
├── informatique.json
├── manga.json
├── musique.json
├── physique.json
├── science.json
└── sport.json
```

---

## ⚙️ Installation (lancer depuis Python)

### 1. Prérequis

- **Python 3.9 ou supérieur** → https://www.python.org/downloads/
  - ⚠️ Lors de l'installation, cocher "Add Python to PATH"

### 2. Installer la dépendance

Ouvre un terminal (cmd ou PowerShell) dans le dossier du projet :

```bash
pip install customtkinter
```

### 3. Lancer le quiz

```bash
python quiz.py
```

---

## 🖥️ Créer un fichier .EXE (Windows)

Tu peux transformer le quiz en application autonome .exe
que tu peux partager sans avoir besoin de Python.

### Étape 1 — Installer PyInstaller

```bash
pip install pyinstaller
```

### Étape 2 — Générer l'exe

Dans le dossier du projet, lance :

```bash
pyinstaller --onefile --windowed --name "VianeyQuiz" quiz.py
```

| Option            | Rôle                                        |
|-------------------|---------------------------------------------|
| --onefile         | Tout dans un seul fichier .exe              |
| --windowed        | Pas de fenêtre console noire au démarrage   |
| --name "VianeyQuiz" | Nom du fichier généré                     |

### Étape 3 — Récupérer l'exe

L'exécutable se trouve dans :

```
Quizz/
└── dist/
    └── VianeyQuiz.exe   ✅ ton application
```

### Étape 4 — Copier les JSON à côté de l'exe

⚠️ IMPORTANT : les fichiers JSON doivent être dans le même dossier que le .exe :

```
n'importe où/
├── VianeyQuiz.exe
├── informatique.json
├── manga.json
├── musique.json
├── physique.json
├── science.json
└── sport.json
```

Tu peux distribuer ce dossier à n'importe qui — aucune installation nécessaire.

---

## 🎮 Règles du jeu

| Élément              | Détail                              |
|----------------------|-------------------------------------|
| ⏱️ Temps/question    | 20 secondes                         |
| ✅ Bonne réponse     | +100 points                         |
| ❌ Mauvaise/temps    | 0 pts, série réinitialisée          |
| 🔥 Streak            | Bonnes réponses consécutives        |
| ← Retour             | Disponible à tout moment            |

---

## 📦 Dépendances

```
customtkinter
pyinstaller   (uniquement pour créer l'exe)
```

---

## 🛠️ Format des fichiers JSON

```json
{
  "Facile": [
    {
      "question": "Texte de la question ?",
      "options": { "A": "Choix 1", "B": "Choix 2", "C": "Choix 3", "D": "Choix 4" },
      "answer": "Choix 1"
    }
  ],
  "Moyen": [],
  "Difficile": []
}
```

> ⚠️ La valeur de "answer" doit être identique à l'une des valeurs de "options".
