# Test Dokumentation - TODO-App

## Übersicht

Vollständige Test Suite für die TODO-App mit pytest Framework.

## Test-Statistiken

- **Gesamt Tests**: 93 (83 Unit + 5 Integration + 5 System)
- **Status**: ✅ Alle Tests bestanden
- **Code Coverage**: 98%
  - `model.py`: 97% (141 von 145 Zeilen)
  - `controller.py`: 100% (52 von 52 Zeilen)

## Test-Struktur

```
tests/
├── __init__.py
├── README.md
├── test_unit.py         (83 Tests - Unit Tests)
├── test_integration.py  (5 Tests - Integrationstests)
└── test_system.py       (5 Tests - Systemtests)
```

## Test-Struktur

Die Tests folgen konsequent dem **AAA-Muster** (Arrange-Act-Assert):

```python
def test_example(self):
    """Test: Beschreibung was getestet wird"""
    # Arrange - Test-Daten vorbereiten
    data = ...
    
    # Act - Zu testende Aktion ausführen
    result = function(data)
    
    # Assert - Erwartetes Ergebnis überprüfen
    assert result == expected
```

## Test-Kategorien

### Unit Tests (83 Tests) - test_unit.py

#### 1. Task-Klasse Tests (12 Tests)
- ✅ Erstellung mit gültigen/ungültigen Daten
- ✅ Validierung (leere Titel, Whitespace)
- ✅ Dringlichkeitsprüfung (heute, morgen, zukünftig)
- ✅ Serialisierung/Deserialisierung (to_dict/from_dict)

#### 2. Category-Klasse Tests (5 Tests)
- ✅ Erstellung und Validierung
- ✅ Konstanten-Überprüfung (MAX_CATEGORIES)

#### 3. TaskRepository Tests (30 Tests)
- ✅ **CRUD-Operationen:**
  - Hinzufügen neuer Tasks (FR-00)
  - Lesen von Tasks (FR-05)
  - Aktualisieren von Tasks (FR-03)
  - Löschen von Tasks (FR-02)
  
- ✅ **Status-Management:**
  - Toggle Completion (FR-04)
  - Archivierung
  - Wiederherstellung
  
- ✅ **Kategorie-Management:**
  - Hinzufügen (FR-06)
  - Löschen mit Task-Update
  - Maximum-Limit (5 Kategorien)
  
- ✅ **Filter-Funktionen:**
  - Nach Status (Offen/Erledigt) (FR-07)
  - Nach Kategorie (FR-07)
  - Kombinierte Filter
  - Dringliche Tasks

- ✅ **Persistierung:**
  - Laden/Speichern von JSON
  - Default-Daten
  - Fehlerbehandlung (korrupte Dateien)

#### 4. TaskController Tests (17 Tests)
- ✅ CRUD mit Validierung
- ✅ Whitespace-Handling
- ✅ Statistik-Berechnung
- ✅ Filter-Delegation
- ✅ Archiv-Operationen

#### 5. CategoryController Tests (7 Tests)
- ✅ CRUD-Operationen
- ✅ Validierung und Normalisierung
- ✅ Kapazitätsprüfung

#### 6. ApplicationController Tests (3 Tests)
- ✅ Initialisierung
- ✅ Controller-Zugriff

#### 7. Edge Cases & Fehlerbehandlung (9 Tests)
- ✅ Sehr lange Titel (500+ Zeichen)
- ✅ Sonderzeichen (<>&"')
- ✅ Doppelte Titel
- ✅ Vergangene Fälligkeitsdaten
- ✅ Korrupte JSON-Dateien
- ✅ Ungültige Datumsformate
- ✅ Eindeutige ID-Vergabe

### Integrationstests (5 Tests) - test_integration.py

#### 1. Task-Erstellung Integration
**Test**: `test_create_multiple_tasks_maintains_repository_consistency`

Testet das Zusammenspiel zwischen TaskController, CategoryController und Repository:
- ✅ Mehrere Tasks (5) über Controller erstellen
- ✅ Repository-Konsistenz prüfen (IDs, Titel, Kategorien)
- ✅ Filter funktionieren korrekt
- ✅ Dringliche Tasks werden identifiziert
- ✅ Persistierung auf Disk funktioniert
- ✅ Daten können neu geladen werden
- ✅ Statistiken sind korrekt

#### 2. Task-Aktualisierung Integration
**Test**: `test_update_task_status_persists_correctly_in_repository`

Testet Status-Änderungen und deren Persistierung:
- ✅ Task erstellen
- ✅ Status auf erledigt ändern (toggle completion)
- ✅ Task wird ins Archiv verschoben
- ✅ Änderung persistiert im Repository
- ✅ Task kann wiederhergestellt werden
- ✅ Task-Details aktualisieren (Titel, Kategorie, Datum)
- ✅ Alle Updates werden persistent gespeichert

#### 3. Fehlerbehandlung Integration
**Test**: `test_empty_task_creation_raises_controlled_error`

Testet kontrollierte Fehlerbehandlung:
- ✅ Leere Task erstellen → Controller gibt False zurück
- ✅ Whitespace-Task → wird abgelehnt
- ✅ Repository bleibt konsistent
- ✅ Keine ungültigen Tasks werden gespeichert
- ✅ next_id wird nicht durch Fehlversuche erhöht
- ✅ Gültige Tasks funktionieren nach Fehlversuchen

#### 4. Task-Löschung Integration
**Test**: `test_delete_task_removes_from_repository_completely`

Testet Löschen aus aktivem Repository und Archiv:
- ✅ Mehrere Tasks erstellen
- ✅ Einzelne Task löschen
- ✅ Task verschwindet aus Repository
- ✅ Andere Tasks bleiben unberührt
- ✅ Löschung persistiert
- ✅ Nicht-existierende Tasks geben False zurück
- ✅ Archivierte Tasks können gelöscht werden

#### 5. Kompletter Workflow Integration
**Test**: `test_complete_task_lifecycle`

Testet den vollständigen Task-Lebenszyklus:
- ✅ Kategorien erstellen
- ✅ Tasks erstellen
- ✅ Tasks bearbeiten
- ✅ Tasks als erledigt markieren (archivieren)
- ✅ Tasks wiederherstellen
- ✅ Tasks löschen
- ✅ Repository-Konsistenz durchgehend gewährleistet

### Systemtests (5 Tests) - test_system.py

Systemtests testen das **komplette System End-to-End** durch alle Schichten (View → Controller → Repository).

#### 1. Aufgabe anlegen (Systemtest)
**Test**: `test_create_task_through_complete_system`

Testet den kompletten Datenfluss beim Anlegen:
- ✅ User Input → Controller → Repository
- ✅ Persistierung auf Disk
- ✅ System-Neustart simulieren
- ✅ Daten korrekt gespeichert und abrufbar
- ✅ Mehrfach-Erstellung funktioniert
- ✅ Filter funktionieren nach Erstellung
- ✅ Statistiken korrekt aktualisiert

#### 2. Als erledigt markieren (Systemtest)
**Test**: `test_mark_task_completed_through_complete_system`

Testet Status-Änderung durch alle Schichten:
- ✅ Task erstellen und erledigen
- ✅ Archivierung funktioniert systemweit
- ✅ Status persistent gespeichert
- ✅ Wiederherstellung funktioniert
- ✅ Statistiken aktualisiert
- ✅ System konsistent nach Neustart

#### 3. Aufgabe löschen (Systemtest)
**Test**: `test_delete_task_through_complete_system`

Testet Löschung durch komplettes System:
- ✅ Tasks erstellen und löschen
- ✅ Aus aktivem Repository entfernen
- ✅ Aus Archiv löschen
- ✅ Andere Tasks unberührt
- ✅ Persistierung korrekt
- ✅ System konsistent nach Löschungen

#### 4. Fehlerbehandlung (Systemtest)
**Test**: `test_error_cases_through_complete_system`

Testet Fehlerbehandlung auf allen Ebenen:
- ✅ Leere/Whitespace Tasks abgelehnt
- ✅ Nicht-existierende Ressourcen
- ✅ Kategorie-Limits
- ✅ Doppelte Kategorien
- ✅ System bleibt konsistent
- ✅ Kontrollierte False-Rückgabe (keine Exceptions)

#### 5. Kompletter End-to-End Workflow (Systemtest)
**Test**: `test_complete_user_workflow_through_system`

Simuliert realistischen Benutzer-Workflow:
- ✅ Kategorien verwalten
- ✅ Tasks erstellen
- ✅ Tasks bearbeiten
- ✅ Tasks filtern
- ✅ Tasks als erledigt markieren
- ✅ Archiv verwalten
- ✅ Tasks löschen
- ✅ System-Neustart → Daten persistent
- ✅ Alle Funktionen nach Neustart verfügbar

## Test-Unabhängigkeit

Alle Tests sind vollständig unabhängig durch:
- **Fixtures**: Temporäre Dateien und frische Repository-Instanzen pro Test
- **Isolation**: Kein shared state zwischen Tests
- **Cleanup**: Automatisches Aufräumen durch pytest tmp_path

### Unit vs Integration vs System Tests

**Unit Tests** (`test_unit.py`):
- Testen einzelne Komponenten isoliert
- Nutzen Mocks für externe Abhängigkeiten
- Schnell und fokussiert
- 83 Tests, < 0.2s Laufzeit

**Integrationstests** (`test_integration.py`):
- Testen Zusammenspiel mehrerer Komponenten
- Controller + Repository Interaktion
- Persistierung und Daten-Konsistenz
- 5 Tests, < 0.05s Laufzeit

**Systemtests** (`test_system.py`):
- Testen komplettes System End-to-End
- View + Controller + Repository
- Simulieren echte Benutzer-Workflows
- Ohne Browser (kontrolliert)
- 5 Tests, < 0.4s Laufzeit

## Ausführung

### Alle Tests ausführen
```bash
pytest tests/ -v
```

### Nur Unit Tests
```bash
pytest tests/test_unit.py -v
```

### Nur Integrationstests
```bash
pytest tests/test_integration.py -v
```

### Mit Coverage-Report
```bash
pytest tests/ --cov=model --cov=controller --cov-report=term-missing
```

### HTML Coverage-Report
```bash
pytest tests/ --cov=model --cov=controller --cov-report=html
# Report verfügbar unter: htmlcov/index.html
```

### Spezifische Test-Klasse ausführen
```bash
pytest tests/test_unit.py::TestTaskRepository -v
pytest tests/test_integration.py::TestTaskCreationIntegration -v
```

### Einzelnen Test ausführen
```bash
pytest tests/test_unit.py::TestTask::test_task_creation_with_valid_data -v
```

## Funktionale Anforderungen (FR) Coverage

| FR-ID | Anforderung | Tests | Status |
|-------|-------------|-------|--------|
| FR-00 | Neue Task hinzufügen | 5 Tests | ✅ |
| FR-01 | Persistierung | 3 Tests | ✅ |
| FR-02 | Task löschen | 3 Tests | ✅ |
| FR-03 | Task bearbeiten | 5 Tests | ✅ |
| FR-04 | Als erledigt markieren | 4 Tests | ✅ |
| FR-05 | Alle Tasks anzeigen | 3 Tests | ✅ |
| FR-06 | Kategorien verwalten | 9 Tests | ✅ |
| FR-07 | Filtern nach Status/Kategorie | 7 Tests | ✅ |
| FR-08 | Fälligkeitsdatum | 6 Tests | ✅ |

## Nicht getestete Zeilen

Die 4 nicht getesteten Zeilen in `model.py` sind ausschließlich in **except-Blöcken** für Fehlerbehandlung bei ungültigen Datumsformaten, die nur bei manueller Datenkorruption auftreten können.

## Test-Philosophie

1. **Klar und Lesbar**: Jeder Test hat aussagekräftigen Namen und Docstring
2. **Fokussiert**: Ein Test prüft genau eine Funktionalität
3. **Schnell**: Alle 83 Tests laufen in < 0.5 Sekunden
4. **Robust**: Tests prüfen auch Fehlerfälle und Randbedingungen
5. **Wartbar**: Fixtures vermeiden Code-Duplikation

## Fixtures

```python
@pytest.fixture
def empty_repository(temp_data_file)
    """Leeres Repository für Tests"""

@pytest.fixture
def repository_with_tasks(temp_data_file)
    """Repository mit 3 Beispiel-Tasks"""

@pytest.fixture
def task_controller(empty_repository)
    """TaskController mit leerem Repository"""

@pytest.fixture
def category_controller(empty_repository)
    """CategoryController mit leerem Repository"""
```

## Continuous Integration Ready

Die Tests sind CI/CD-ready:
- Keine externen Abhängigkeiten (außer pytest)
- Deterministische Ergebnisse
- Keine Netzwerk-/Datenbank-Zugriffe
- Schnelle Ausführung

## Ergebnis

✅ **Ziel erreicht**: >80% Code Coverage (98%)
✅ **Alle Tests bestanden**: 93/93 (83 Unit + 5 Integration + 5 System)
✅ **AAA-Muster**: Konsequent angewendet
✅ **Unabhängig**: Jeder Test läuft isoliert
✅ **Vollständig**: Alle CRUD-Operationen, Validierungen, Filter und Edge Cases getestet
✅ **Integration**: Controller-Repository Zusammenspiel getestet
✅ **Systemtests**: End-to-End Workflows durch alle Schichten
✅ **Fehlerbehandlung**: Ungültige Eingaben kontrolliert abgefangen
