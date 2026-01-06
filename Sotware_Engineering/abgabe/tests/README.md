# Tests für TODO-App

Vollständige Test Suite mit 93 Tests (83 Unit + 5 Integration + 5 System)

## Schnellstart

```bash
# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage
pytest tests/ --cov=model --cov=controller --cov-report=term-missing

# HTML Coverage Report
pytest tests/ --cov=model --cov=controller --cov-report=html
```

## Dateien

- **test_unit.py** (83 Tests)
  - Task, Category, Repository Tests
  - Controller Tests
  - Edge Cases & Fehlerbehandlung

- **test_integration.py** (5 Tests)
  - Mehrere Tasks erstellen → Repository-Konsistenz
  - Task-Status aktualisieren → Persistierung
  - Leere Task → Fehlerbehandlung
  - Task löschen → Entfernung aus Repository
  - Kompletter Workflow

- **test_system.py** (5 Tests)
  - Aufgabe anlegen → Speicherung & Abruf
  - Als erledigt markieren → Status korrekt
  - Aufgabe löschen → System konsistent
  - Fehlerfälle → Kontrollierte Fehlermeldung
  - End-to-End Workflow

## Ergebnisse

- ✅ **93/93 Tests bestanden**
- ✅ **98% Code Coverage**
- ✅ **< 0.4s Laufzeit**

Siehe [TEST_DOKUMENTATION.md](../TEST_DOKUMENTATION.md) für Details.
