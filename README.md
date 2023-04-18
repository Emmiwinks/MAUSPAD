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

| **Kennwert**      	| **Berechnung**                	| **Soll** 	| **Grenzwert** 	| **Kommentar**                 	|
|-------------------	|-------------------------------	|----------	|---------------	|-------------------------------	|
| EV/MC             	| Enterprise Value / Market Cap 	| <        	| 2             	|                               	|
| Netto-Debt        	| Total Debt / Total Cash       	| <        	| 2             	| Verschuldungsgrad             	|
| EV/EBIT           	| Enterprise Value / EBIT       	| <        	| 20            	|                               	|
| PEG-Ratio         	|                               	| <        	| 1             	| Price-Earnings-Growth Ratio, nicht möglich, weil growth info fehlt   	|
| Net profit Margin 	|                               	| >        	| 10%           	|                               	|
| Piotroski score   	|                               	| >        	| 8             	| P-Score jetzt auch bei Simfin 	|
| Return on Equity  	|                               	| >        	| 15%           	|                               	|

## Phase III - Backtesting
Ziel: Ausführunge von Buy- und Sell- Orders anhand festgelegter Strategien basierend auf historischen Kursdaten und Berechnung des Gewinns.
- es zählen nur Umsätze bis zur letzten Sell-Order

ToDo:
- Emmiwinks: Implementierung
- Lazer: Bestimmung eines geeigneten Scores + Triggerpunkte für Buy/Sell (Hysterese beachten!), am besten relativ zu letztem Quartal etc...

## Phase IV - Fine tuning (verschoben)
Ziel: Strategie verfeinern durch 
- Festlegen des potentiellen Portfolio (Asset Pool)
- Verbesserung des MAUSPAD™-Scores
- Entscheidung darüber, ob MAUSPAD™-Score-Schwellwerte festgelegt oder optimiert werden sollen
- Überlegungen, welche Strategie(n) als Benchmark gelten sollen (z.B. Buy-and-Hold des ganzen Portfolios)

## Phase IV Fine tuning (neu)
Ziel: Validierung der KPIs <br>
ToDos:
- Emmiwinks: Tabelle mit allen benötigten Daten und KPIs erstellen (done - siehe "simfin_data/kpi-summary.csv")
- Lazer: Ansehen und Validieren der KPIs, Vergleich verschiedener Unternehmen, ggf. Ergänzen der Tabelle mit gewünschten Unternehmen mithilfe des mauspad_score.py main code


#### Anleitung Prototyp (derzeit nicht relevant)
```
git clone https://github.com/Emmiwinks/MAUSPAD.git
cd MAUSPAD
pip install -r requirements.txt 
python -m app
```
http://127.0.0.1:8050/ im Browser öffnen
