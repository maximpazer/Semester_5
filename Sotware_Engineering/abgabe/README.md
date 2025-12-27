# TODO Application – Software Engineering Project

## 1. Project Overview
This project implements a cross-platform TODO application developed according to
Software Engineering best practices, including Requirements Engineering (SMART),
MVC architecture, and established design patterns.

The goal is to design, implement, and document a maintainable system that fulfills
both functional and non-functional requirements.


## 2. Requirements Engineering --> Block 2

All requirements are formulated according to the **SMART principle**
(Specific, Measurable, Accepted, Realistic, Timely) and are uniquely identifiable
to ensure full traceability throughout the project lifecycle.

### 2.1 Functional Requirements 

Functional requirements describe **what** the system must do.
At least five MUST requirements are fully implemented.

| ID     | Description                                                                 | Priority |
|--------|------------------------------------------------------------------------------|----------|
| FR-00  | The system must allow users to create new TODO items with at least a title. | MUSS     |
| FR-01  | The system must store tasks persistently so data is not lost on restart.     | MUSS     |
| FR-02  | The system must allow the user to delete existing TODO items.                | MUSS     |
| FR-03  | The system must allow the user to edit the content of existing TODO items.   | MUSS     |
| FR-04  | The system must enable marking tasks as completed or open.                   | MUSS     |
| FR-05  | The system must display all TODO items in a clear list format.               | MUSS     |
| FR-06  | The user should be able to create and manage up to five categories.          | SOLL     |
| FR-07  | The system should allow filtering tasks by status.                           | SOLL     |
| FR-08  | Tasks can include a due date selected via a calendar picker (< 3 clicks).    | KANN     |


### 2.2 Non-Functional Requirements

Non-functional requirements describe **how well** the system performs,
based on ISO/IEC 25010 quality characteristics.

| ID      | Category       | Description                                                             | Priority |
|---------|---------------|-------------------------------------------------------------------------|----------|
| NFR-01  | Performance   | A new task can be created in under 5 seconds.                          | MUSS     |
| NFR-02  | Usability     | The UI adheres to Nielsen’s 10 Usability Heuristics.                    | MUSS     |
| NFR-03  | Performance   | The system reacts to user input within 200–300 ms.                     | MUSS     |
| NFR-04  | Security      | Passwords (if used) are stored using a secure hashing algorithm.       | SOLL     |
| NFR-05  | Compatibility | The application supports cross-platform execution.                    | MUSS     |
| NFR-06  | Reliability   | The application ensures 99.5% monthly availability.                   | SOLL     |



## 3. Streamlit UI --> Block 3
--> hier Link einfügen zu Figma (noch zu erstellen)
Streamlit Plugin:
https://www.figma.com/community/plugin/1167469184805790690/figma-to-streamlit
▪
Streamlit Design System:
https://www.figma.com/community/file/1166786573904778097
1.
Öffnen Sie das Streamlit-Designsystem, machen Sie sich damit vertraut.
2.
Öffnen Sie eine neue Seite. Erstellen Sie ein einfaches Todo-App-Design mit Streamlit-Assets (gehen Sie zu „Assets“ und suchen Sie nach Assets, die mit „st.“ beginnen
## 3. Architecture & Quality Constraints

### 3.1 MVC Architecture

Die TODO-App implementiert strikt das Model-View-Controller (MVC) Architekturmuster:

**Warum MVC für diese Anwendung geeignet ist:**
MVC trennt Datenlogik, Präsentation und Steuerung voneinander, was die Wartbarkeit und Testbarkeit erheblich verbessert. Die klare Trennung ermöglicht es, UI-Änderungen vorzunehmen ohne die Geschäftslogik zu beeinflussen. Für eine TODO-App mit CRUD-Operationen ist MVC ideal, da Tasks (Model) unabhängig von ihrer Darstellung (View) verwaltet werden können. Die Controller-Schicht koordiniert Nutzerinteraktionen effizient und macht die Anwendung erweiterbar. Streamlit's reaktives Rendering passt gut zum MVC-Pattern, da Views automatisch bei Datenänderungen aktualisiert werden. Die Architektur unterstützt auch zukünftige Features wie Cloud-Synchronisation durch einfachen Austausch der Persistierung-Logik im Model.

#### Model (model.py)
**Verantwortlichkeiten:**
- Zentrale Domänenobjekte (`Task`, `Category`)
- Datenzugriff und Persistierung (`TaskRepository`)
- Validierungslogik für Tasks und Kategorien
- JSON-Serialisierung/Deserialisierung
- Geschäftsregeln (z.B. is_urgent())

**Implementierte Klassen:**
- `Task`: Domänenobjekt für Aufgaben mit Validierung
- `Category`: Domänenobjekt für Kategorien (max. 5)
- `TaskRepository`: Data Access Layer für JSON-Persistierung (FR-01)

#### View (view.py)
**Verantwortlichkeiten:**
- UI-Rendering mit Streamlit-Komponenten
- Formulare für Task-Eingabe und -Bearbeitung
- Listen-Darstellung von Tasks (FR-05)
- Responsive Design und CSS-Styling
- Nielsen Usability Heuristics in UI-Elementen

**Implementierte Klassen:**
- `TaskView`: Darstellung von Task-Formularen und Listen
- `CategoryView`: Kategorie-Verwaltungs-UI (FR-06)
- `SidebarView`: Filter- und Statistik-Anzeige (FR-07)
- `ArchiveView`: Archiv-Darstellung
- `LayoutView`: Responsive CSS und Layout-Komponenten

#### Controller (controller.py)
**Verantwortlichkeiten:**
- Koordination zwischen Model und View
- CRUD-Operationen für Tasks (FR-00, FR-02, FR-03, FR-04)
- Event-Handling und Datenfluss-Steuerung
- Geschäftslogik für Filterung und Statistiken
- Session-State-Management

**Implementierte Klassen:**
- `TaskController`: Steuerung aller Task-Operationen (Create, Read, Update, Delete, Toggle)
- `CategoryController`: Verwaltung von Kategorien
- `ApplicationController`: Haupt-Controller als Fassade für die Anwendung

#### Main Application (app.py)
**Verantwortlichkeiten:**
- Einstiegspunkt der Anwendung
- Session State Initialisierung
- Verbindung von Controller und View
- Streamlit-spezifische Konfiguration
- Event-Callbacks und Rerun-Logik

### 3.2 Design Patterns

Die folgenden Design Patterns sind implementiert:

- **Repository Pattern**: `TaskRepository` kapselt Datenzugriff und Persistierung
- **Facade Pattern**: `ApplicationController` bietet vereinfachten Zugang zu Task- und Category-Controllern
- **Domain Model Pattern**: `Task` und `Category` repräsentieren Geschäftsobjekte mit Validierung
- **MVC Pattern**: Strikte Trennung von Model, View und Controller


## 4. Usability Traceability (Nielsen)

Each usability heuristic is explicitly mapped to UI elements.

| Heuristic | Implementation Example |
|----------|------------------------
