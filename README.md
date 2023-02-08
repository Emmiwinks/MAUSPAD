# MAUSPAD 🐭
Coconut Panda presents
**Market Analysis Ultimate Stocks Python Awesome Database**

## Ziel
Unternehmen automatisiert anhand fundamentaler Daten analysieren und bewerten und auf Grundlage dessen eine Kaufentscheidung treffen. 

## Phase I
### Datenaquise
Unternehmenskennzahlen über API oder Webscraper sammeln
idealerweise regelmäßig (z.B. monatlich) aktualisiert
Kennzahlen kommen aus seperater Tabelle (mit Quelle, [hier klicken](https://docs.google.com/spreadsheets/d/1Gey_Ki_RBlKmYTK_6NeiPbnTqjyGkbalJ7TLtR6sqYw/edit?usp=sharing))

## Phase II
### Vizualation
Ziel: graphische Darstellung des historischen Kursverlaufs + des Mauspad_scores (oder F-Score, wenn verfügbar) </br>
Variablen: UpdateRate, startTime, AssetPool, buy/sell-Trigger

ToDo: 
- Emmiwinks: F-Score errechnen zu jedem beliebligen Zeitpunkt zu irgendeiner Aktie + Vizualation
- Lazer: Recherche eigener Score aus yfinance Daten + geeignete Triggerpunkte

## Phase III
### Backtesting
Ziel: Ausführunge von Buy- und Sell- Orders anhand festgelegter Strategien basierend auf historischen Kursdaten und Berechnung des Gewinns.
- es zählen nur Umsätze bis zur letzten Sell-Order

ToDo:
- Emmiwinks: Implementierung
- Lazer: Bestimmung eines geeigneten Scores + Triggerpunkte für Buy/Sell (Hysterese beachten!), am besten relativ zu letztem Quartal etc...

#### Anleitung Prototyp
```
git clone https://github.com/Emmiwinks/MAUSPAD.git
cd MAUSPAD
pip install -r requirements.txt 
python -m app
```
http://127.0.0.1:8050/ im Browser öffnen
