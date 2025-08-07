
# 📰 Wortwolken deutscher Nachrichtenseiten

🔗 **Live-Demo:** [https://newsinsight-wg3q.onrender.com/](https://nachrichten-wortwolken.onrender.com)  
> *Täglich aktualisierte Wortwolken aus den Startseiten großer deutscher Zeitungen.*

---

## ✨ Motivation

In einer Zeit, in der Medienlandschaften zunehmend fragmentiert sind, bietet dieses Projekt einen schnellen, visuellen Einblick in die **unterschiedlichen Schwerpunkte und Narrative** deutscher Nachrichtenseiten.

Durch den direkten Vergleich von Wortwolken wird deutlich, **wie verschieden gesellschaftliche und politische Themen gewichtet und dargestellt** werden – beispielsweise zwischen BILD, ZEIT, FAZ und Spiegel.

Ziel ist es, die **Mediensensibilität zu fördern** und Nutzer:innen zu ermutigen, verschiedene Informationsquellen kritisch zu reflektieren.

---

## ⚙️ Funktionsweise

### 1. Webseiten-Scraping
Täglich wird die Startseite folgender Nachrichtenseiten automatisch ausgelesen:

- [Spiegel](https://www.spiegel.de/)
- [Bild](https://www.bild.de/)
- [ZEIT Online](https://www.zeit.de)
- [FAZ](https://www.faz.net/aktuell/)

Dazu wird `newspaper3k` verwendet, um Artikeltexte zu extrahieren. Paywall-Artikel und irrelevante Navigationslinks werden dabei gefiltert.

### 2. Wortbereinigung

Die größte Herausforderung liegt darin, **irrelevante oder generische Wörter** wie „der“, „lesen“, „Startseite“ oder „mehr“ zuverlässig auszuschließen.

Dafür werden mehrere Methoden kombiniert:

- NLTK- und spaCy-Stoppwortlisten für die deutsche Sprache
- Dynamische Filter auf Basis von Wortfrequenzen und Dokumenthäufigkeit
- Manuell gepflegte Listen in `stopwords.txt` und `excluded_words.json`

> 🛠️ An den Stopwörtern und Filtern wird **kontinuierlich weitergearbeitet**, um die Aussagekraft der Wortwolken weiter zu verbessern.

### 3. Generierung der Wortwolken

Mit der `wordcloud`-Bibliothek wird für jede Quelle ein PNG-Bild erstellt. Diese werden nach Datum abgelegt und über die Web-App abrufbar gemacht.

### 4. Automatisierung

Ein GitHub Actions Workflow führt die Scraper täglich automatisch aus. Alle Wortwolken landen in `static/images`.

---

## 🌐 Web-App

Die Anwendung basiert auf **Flask** und wird über [Render.com](https://render.com) kostenlos gehostet.

- **Startseite**: Aktuelle Wortwolken des Tages
- **Archivseite**: Aufruf vergangener Tage über `/wordclouds/<yyyy-mm-dd>`

---

## 📁 Projektstruktur

```
project/
├── app.py                    # Flask-App zur Anzeige der Wortwolken
├── scraper.py                # Scraper und Wortwolken-Generator
├── stopwords.txt             # Manuell gepflegte Stopwords
├── excluded_words.json       # Quelle-spezifische Ausnahmen
├── excluded_links.json       # Unerwünschte Links beim Crawling
├── templates/
│   ├── index.html            # Aktuelle Tagesansicht
│   └── wordclouds.html       # Archivansicht
├── static/images/            # Wortwolken (PNG-Dateien)
├── requirements.txt          # Python-Abhängigkeiten
└── README.md
```

---

## 🚀 Lokal ausführen

### 1. Setup

```bash
git clone https://github.com/dein-nutzername/dein-repo.git
cd dein-repo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Sprachmodelle herunterladen

```bash
python -m nltk.downloader stopwords
python -m spacy download de_core_news_sm
```

### 3. Wortwolken generieren

```bash
python scraper.py
```

### 4. Webserver starten

```bash
python app.py
```

---

## 🧠 Herausforderungen & Weiterentwicklung

- **Stoppwörter** sind je nach Quelle und Tag unterschiedlich wirksam – hier ist **fortlaufende Feinjustierung** notwendig
- Themen wie „heute“, „Update“ oder „mehr lesen“ tauchen regelmäßig auf, sind aber semantisch bedeutungslos
- Ziel ist es, künftig ein noch präziseres **Themen-Clustering** umzusetzen (z. B. über Named Entity Recognition)
- Optional: Integration interaktiver Wortwolken oder Zeitverläufe

---

## 📜 Lizenz

MIT – freie Nutzung und Weiterverwendung ausdrücklich erlaubt und erwünscht!

---

## 📬 Kontakt

Bei Fragen, Feedback oder Kollaborationswünschen: **[Mario_Diekmann@yahoo.de]**

---

> Projekt von [Mario Diekmann] – Erstellt mit Python, Flask, newspaper3k, wordcloud, NLTK und spaCy.
