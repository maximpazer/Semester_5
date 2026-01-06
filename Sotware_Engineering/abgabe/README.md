# TODO-Anwendung – Software Engineering Projekt

## 1. Projektübersicht
Diese Anwendung ist eine plattformübergreifende TODO-Lösung, die nach den Best Practices des Software Engineerings entwickelt wurde. Sie integriert Requirements Engineering nach dem SMART-Prinzip, eine klare MVC-Architektur und bewährte Design Patterns.

Das Ziel ist ein wartbares System, das funktionale und nicht-funktionale Anforderungen gleichermaßen erfüllt und umfassend dokumentiert ist.

## 2. Anforderungsanalyse – Block 2
Alle Anforderungen sind entlang des **SMART-Prinzips** (Specific, Measurable, Accepted, Realistic, Timely) formuliert und eindeutig gekennzeichnet, um eine lückenlose Nachverfolgbarkeit im Projektverlauf zu gewährleisten.

### 2.1 Funktionale Anforderungen
Funktionale Anforderungen beschreiben **was** das System leisten muss. Mindestens fünf MUSS-Anforderungen wurden vollständig implementiert.

| ID     | Beschreibung                                                                 | Priorität |
|--------|------------------------------------------------------------------------------|-----------|
| FR-00  | Das System speichert Aufgaben persistent (z. B. lokal als JSON).             | MUSS      |
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

### 2.2 Nicht-funktionale Anforderungen
Nicht-funktionale Anforderungen beschreiben **wie gut** das System seine Aufgaben erfüllt und orientieren sich an den ISO/IEC 25010 Qualitätsmerkmalen.

| ID      | Kategorie     | Beschreibung                                                                 | Priorität |
|---------|---------------|-------------------------------------------------------------------------------|-----------|
| NFR-01  | Performance   | Das Anlegen einer neuen Aufgabe dauert unter 5 Sekunden.                      | MUSS      |
| NFR-02  | Usability     | Die Benutzeroberfläche folgt den zehn Usability-Heuristiken von Nielsen.     | MUSS      |
| NFR-03  | Performance   | Reaktionen auf Nutzereingaben erfolgen innerhalb von 200–300 ms.             | MUSS      |
| NFR-04  | Sicherheit    | Passwörter (falls verwendet) werden mit einem sicheren Hash abgelegt.        | SOLL      |
| NFR-05  | Kompatibilität| Die Anwendung unterstützt plattformübergreifende Ausführung.                 | MUSS      |
| NFR-06  | Zuverlässigkeit| Die Anwendung garantiert 99,5 % monatliche Verfügbarkeit.                   | SOLL      |

## 3. Streamlit-Benutzeroberfläche – Block 3
→ Link zu Figma (noch in Arbeit)

Streamlit Plugin:
https://www.figma.com/community/plugin/1167469184805790690/figma-to-streamlit

Streamlit Design System:
https://www.figma.com/community/file/1166786573904778097

1. Öffnen Sie das Streamlit-Designsystem und machen Sie sich mit den Komponenten vertraut.
2. Erstellen Sie eine neue Seite und gestalten Sie ein einfaches Todo-App-Layout mithilfe der Streamlit-Assets (Assets-Bibliothek nach „st.“ filtern).

## 4. Architektur & Qualitätsrestriktionen
### 4.1 MVC-Architektur
Die TODO-App setzt strikt auf das Model-View-Controller-Muster, das Datenlogik, Darstellung und Steuerung trennt. Diese Trennung erhöht Wartbarkeit und Testbarkeit, erlaubt UI-Anpassungen ohne Geschäftslogikänderungen und macht die Anwendung für zukünftige Features (z. B. Cloud-Synchronisation) flexibel.

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

| Heuristik                                    | Konkrete Umsetzung                                                                                   |
|----------------------------------------------|------------------------------------------------------------------------------------------------------|
| Sichtbarkeit des Systemstatus                | `LayoutView` zeigt Fortschrittsanzeigen und Statusmeldungen beim Speichern bzw. Löschen an.          |
| Übereinstimmung zwischen System und realer Welt | Labels, Kategorien und Terminangaben orientieren sich an vertrauter Todo-Terminologie.      |
| Benutzerkontrolle und Freiheit               | `TaskView` erlaubt Abbrechen und erneutes Laden der Formulare, `SidebarView` setzt Filter zurück.    |
| Konsistenz und Standards                      | Einheitliche Buttons, Icons und Streamlit-Stile in allen Views sorgen für durchgängiges Verhalten.  |
| Fehlervermeidung                             | Validierung verhindert leere Titel, vor dem Löschen erscheint eine Bestätigung (FR-08).              |
| Erkennung statt Erinnerung                   | Editierbare Listen und Filter erleichtern das Wiederfinden von Tasks ohne Gedächtnisleistung.        |
| Flexibilität und Effizienz                   | Tastatur-Fokussierung, Shortcuts für Filter und Schnellaktionen erhöhen die Arbeitseffizienz.        |
| Ästhetik und minimalistisches Design          | `LayoutView` und CSS sorgen für eine reduzierte, aufgeräumte Darstellung ohne unnötige Elemente.     |
| Hilfe bei Fehlern                            | Hilfetexte, Fehlermeldungen und Validierungsfeedback geben klare Hinweise auf korrekte Eingaben.     |
| Hilfe und Dokumentation                      | README, View-Tooltips und das Design-System-Referenzmaterial unterstützen bei der Nutzung.          |

