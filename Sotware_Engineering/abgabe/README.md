# TODO-Anwendung – Software Engineering Projekt

## 1. Projektübersicht
Diese Anwendung ist eine plattformübergreifende TODO-Lösung, die nach den Best Practices des Software Engineerings entwickelt wurde. Sie integriert Requirements Engineering nach dem SMART-Prinzip, eine klare MVC-Architektur und bewährte Design Patterns.

## 2. Anforderungsanalyse – Block 2
Alle Anforderungen sind entlang des **SMART-Prinzips** (Specific, Measurable, Accepted, Realistic, Timely)

### 2.1 Funktionale Anforderungen
Funktionale Anforderungen beschreiben **was** das System leisten muss. 00-04 entsprechen den Anforderungen aus den Folien.

| ID     | Beschreibung                                                                 | Priorität |
|--------|------------------------------------------------------------------------------|-----------|
| FR-00  | Das System speichert Aufgaben persistent (z. B. lokal/DB).             | MUSS      |
| FR-01  | Eine neue Aufgabe mit Titel lässt sich innerhalb von maximal 5 Sekunden anlegen. | MUSS      |
| FR-02  | Der Nutzer kann Aufgaben dauerhaft löschen.                                 | MUSS      |
| FR-03  | Aufgaben lassen sich nachträglich bearbeiten (Titel, Beschreibung, Kategorie). | MUSS      |
| FR-04  | Aufgaben können als erledigt markiert werden.                                | MUSS      |
| FR-05  | Filterfunktionen erlauben die Anzeige nach Kategorien.                       | SOLL      |
| FR-06  | Aufgaben lassen sich nach dem Fälligkeitsdatum sortieren (auf-/absteigend). | SOLL      |
| FR-07  | Eine Suchfunktion findet Aufgaben anhand des Titels.                         | SOLL      |
| FR-08  | Vor dem endgültigen Löschen erscheint eine Bestätigungsabfrage.              | KANN      |
| FR-09  | Erledigte Aufgaben lassen sich gesammelt entfernen.                          | KANN      |
| FR-10  | Aufgaben lassen sich als „wichtig“ oder „priorisiert“ markieren.            | KANN      |
| FR-11  | Es können nur Aufgaben mit bevorstehendem Fälligkeitsdatum angezeigt werden (heute/diese Woche). | KANN      |
| FR-12  | Es können Kategorien farbig markiert werden  | KANN      |


## 3. Streamlit-Benutzeroberfläche – Block 3
→ Link zu Figma (noch in Arbeit)

## 4. Architektur
### 4.1 MVC-Architektur
### Wieso MVC?
Die Model-View-Controller-(MVC)-Architektur eignet sich besonders gut für eine TODO-Anwendung, da sie eine strikte Trennung der Verantwortlichkeiten durch die Aufteilung in drei klar definierte Schichten erzwingt: das Model (Daten und Geschäftslogik), die View (Benutzerschnittstelle) und den Controller (Steuerung und Koordination des Anwendungsablaufs). Diese Struktur überführt funktionale Anforderungen in eine klare Mikroarchitektur, reduziert die kognitive Komplexität und erleichtert es, das System zu verstehen, zu warten und weiterzuentwickeln. Durch die explizite Zuordnung von Zuständigkeiten – etwa die Verwaltung persistenter Aufgabendaten im Model oder die Verarbeitung von Benutzeraktionen wie dem Hinzufügen oder Löschen von Einträgen im Controller – wird der Code konsistenter und besser nachvollziehbar.

MVC unterstützt die Erweiterbarkeit des Systems, da wiederkehrende technische Probleme nach einheitlichen Mustern gelöst werden. Dies erleichtert die Integration neuer Funktionalitäten und fördert die langfristige Wartbarkeit. Die Fachliteratur hebt zudem hervor, dass der Einsatz etablierter Architekturpatterns wie MVC zur Softwarequalität beiträgt, indem er eine frühe Ausrichtung an Qualitätsmerkmalen und Stakeholder-Anforderungen begünstigt. Schließlich ermöglicht die Entkopplung von View und Model, die Benutzeroberfläche zu verändern, ohne die zugrunde liegende Datenhaltung oder Geschäftslogik anpassen zu müssen – ein zentrales Merkmal professioneller Softwareentwicklung.

### Implementierung von MVC
#### Model (model.py)
**Verantwortlichkeiten:**
- Domänenobjekte wie `Task` und `Category`
- Persistierung über `TaskRepository` (JSON-basierte Ablage)
- Validierungslogik (z. B. Pflichtfelder, Anzahl Kategorien)
- JSON-Serialisierung/-Deserialisierung
- Geschäftsregeln wie `is_urgent()`

**Implementierte Klassen:**
- `Task`: Repräsentiert eine Aufgabe mit Validierung
- `Category`: Beinhaltet Kategorien, maximal fünf pro Nutzer
- `TaskRepository`: Data Access Layer für die persistente Speicherung (FR-00)

#### View (view.py)
**Verantwortlichkeiten:**
- UI-Rendering mit Streamlit-Komponenten
- Formulare zur Anlage und Bearbeitung von Aufgaben
- Darstellung als Task-Liste und Statistikbereich
- Responsive Layouts und CSS-Styling
- Integration der Nielsen-Heuristiken in die Benutzeroberfläche

**Implementierte Klassen:**
- `TaskView`: Formulare und Listenansicht für Tasks
- `CategoryView`: Verwaltung und Anzeige von Kategorien (FR-05)
- `SidebarView`: Filteroptionen und Statistiken (FR-06, FR-07)
- `ArchiveView`: Ansicht archivierter erledigter Aufgaben (FR-09)
- `LayoutView`: Responsive Layout-Komponenten und globales CSS

#### Controller (controller.py)
**Verantwortlichkeiten:**
- Vermittlung zwischen Model und View
- CRUD-Operationen für Tasks (FR-00 bis FR-04)
- Event Handling und Steuerung des Datenflusses
- Geschäftslogik für Filter, Sortierung und Statistiken
- Session-State-Management

**Implementierte Klassen:**
- `TaskController`: Create, Read, Update, Delete, Toggle-Erledigt-Status
- `CategoryController`: Verwaltung der Kategorien
- `ApplicationController`: Fassade für alle Controller und Initialisierung der Anwendung

#### Main Application (app.py)
**Verantwortlichkeiten:**
- Einstiegspunkt der Anwendung
- Initialisierung des Session States
- Verknüpfung von Controller und View
- Streamlit-spezifische Konfigurationen
- Event-Callbacks und Rerun-Logik

### 4.2 Design Patterns
Folgende Entwurfsmuster sind umgesetzt:
- **Repository Pattern**: `TaskRepository` kapselt Datenzugriff und Persistierung
- **Facade Pattern**: `ApplicationController` bietet eine zentrale Schnittstelle zu Task- und Category-Controllern
- **Domain Model Pattern**: `Task` und `Category` modellieren Geschäftsobjekte mit Validierung
- **MVC Pattern**: Klare Trennung von Model, View und Controller

## 5. Usability-Nachverfolgbarkeit (Nielsen)
Jede Nielsen-Heuristik ist explizit den UI-Komponenten zugeordnet, um die Gebrauchstauglichkeit nachweisbar zu machen.

| Heuristik | Konkrete Umsetzung im Code |
|---|---|
| **Sichtbarkeit des Systemstatus** | Das System nutzt moderne Toast-Notifications (`st.toast`) für unaufdringliches, aber klares Feedback ("Änderungen gespeichert!") nach jeder Speicheraktion. |
| **Übereinstimmung System/Realität** | `TaskView` verwendet natürliche Sprache für Fälligkeitsdaten („heute“, „morgen“, „in 3 Tagen“) statt technischer Datumsformate. |
| **Benutzerkontrolle & Freiheit** | Nutzer können versehentlich gelöschte Aufgaben über die `ArchiveView` („Wiederherstellen“-Button) zurückholen; Bearbeitungsdialoge haben einen expliziten „Abbrechen“-Button. |
| **Konsistenz & Standards** | Identisches Verhalten bei kritischen Aktionen: Sowohl Aufgaben (`TaskView`) als auch Kategorien (`CategoryView`) nutzen exakt denselben Zwei-Schritt-Löschprozess (🗑 -> ✖), um kognitive Last zu minimieren. |
| **Fehlervermeidung** | Zwei-Stufen-Bestätigung verhindert das versehentliche Löschen von Daten. Der Bestätigungs-Button ändert sich dynamisch, erfordert also eine bewusste Bestätigung. |
| **Wiedererkennung statt Erinnerung** | Eingabefelder nutzen `placeholder`-Texte (z. B. „Was möchten Sie erledigen?“), um das erwartete Format anzuzeigen, ohne dass der Nutzer eine Hilfe lesen muss. |
| **Flexibilität & Effizienz** | Die `SidebarView` ermöglicht Power-Usern das schnelle Filtern nach Kategorien und Status, während Dringlichkeit durch Farbcodierung (roter Rand) sofort scannbar ist. |
| **Ästhetik & Minimalismus** | `label_visibility="collapsed"` wird in Formularen genutzt, um visuelles Rauschen zu reduzieren; `st.expander` versteckt selten genutzte Funktionen wie das Kategorie-Management. |
| **Hilfe bei Fehlern** | Wenn eine leere Kategorie angelegt wird, gibt `CategoryView` eine spezifische Fehlermeldung via `st.error` aus („Bitte Namen eingeben“), statt nichts zu tun. |
| **Hilfe & Dokumentation** | Eine Kurzanleitung mit Symbol-Erklärung ist direkt in der App über `LayoutView.render_help` als aufklappbare Info-Box verfügbar. |

