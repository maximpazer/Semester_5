"""
Systemtests für TODO-App
Testet das komplette System End-to-End (ohne Mocks)
Use-Case-orientiert | Framework: pytest

python -m pytest tests/test_system.py -v && wc -l tests/test_system.py
"""
import pytest
from pathlib import Path
from model import TaskRepository
from controller import ApplicationController, TaskController, CategoryController


@pytest.fixture
def system(tmp_path):
    """
    Komplettes System aufbauen (wie in Produktion)
    Repository → Controller → bereit für Use Cases
    """
    file = tmp_path / "todo_data.json"
    repo = TaskRepository(file)
    
    app = ApplicationController()
    app.repository = repo
    app.task_controller = TaskController(repo)
    app.category_controller = CategoryController(repo)
    
    return {
        "file": file,
        "repo": repo,
        "tasks": app.task_controller,
        "categories": app.category_controller
    }


class TestSystem:
    """4 Systemtests gemäß Aufgabenstellung (End-to-End Use Cases)"""
    
    def test_aufgabe_anlegen_speichern_abrufen(self, system):
        """
        Use Case 1: Aufgabe anlegen → Speicherung und Abruf
        
        Szenario: Benutzer erstellt Task, schließt App, öffnet erneut
        """
        tasks = system["tasks"]
        file = system["file"]
        
        # Benutzer erstellt Aufgabe
        tasks.create_task("Einkaufen gehen", "Privat")
        
        # System speichert (wie beim Schließen der App)
        system["repo"].save()
        
        # Benutzer öffnet App erneut (neues Repository)
        repo2 = TaskRepository(file)
        loaded = repo2.get_all_tasks()
        
        # Aufgabe ist vorhanden
        assert len(loaded) == 1
        assert loaded[0].title == "Einkaufen gehen"
        assert loaded[0].category == "Privat"
    
    def test_aufgabe_erledigt_markieren(self, system):
        """
        Use Case 2: Aufgabe als erledigt markieren → Status korrekt im System
        
        Szenario: Benutzer erledigt eine Aufgabe
        """
        tasks = system["tasks"]
        repo = system["repo"]
        
        # Benutzer erstellt und erledigt Aufgabe
        tasks.create_task("Meeting vorbereiten")
        tasks.toggle_task_completion(1)
        
        # System zeigt: aktive Liste leer, Archiv enthält erledigte Task
        assert len(tasks.get_all_tasks()) == 0
        archived = tasks.get_archived_tasks()
        assert len(archived) == 1
        assert archived[0].completed is True
    
    def test_aufgabe_loeschen_system_konsistent(self, system):
        """
        Use Case 3: Aufgabe löschen → System bleibt konsistent
        
        Szenario: Benutzer löscht eine von mehreren Aufgaben
        """
        tasks = system["tasks"]
        file = system["file"]
        
        # Benutzer erstellt mehrere Aufgaben
        tasks.create_task("Aufgabe A")
        tasks.create_task("Aufgabe B")
        tasks.create_task("Aufgabe C")
        
        # Benutzer löscht mittlere Aufgabe
        tasks.delete_task(2)
        
        # System ist konsistent
        remaining = tasks.get_all_tasks()
        assert len(remaining) == 2
        titles = [t.title for t in remaining]
        assert "Aufgabe B" not in titles
        
        # Persistenz prüfen
        system["repo"].save()
        repo2 = TaskRepository(file)
        assert len(repo2.get_all_tasks()) == 2
    
    def test_fehlerfall_kontrollierte_meldung(self, system):
        """
        Use Case 4: Fehlerfall → kontrollierte Fehlermeldung
        
        Szenario: Benutzer versucht ungültige Aktionen
        """
        tasks = system["tasks"]
        repo = system["repo"]
        
        # Versuch: Leere Aufgabe erstellen
        result1 = tasks.create_task("")
        assert result1 is False
        
        # Versuch: Nicht existierende Task löschen
        result2 = tasks.delete_task(999)
        assert result2 is False
        
        # Versuch: Nicht existierende Task bearbeiten
        result3 = tasks.update_task(999, "Test", "Keine")
        assert result3 is False
        
        # System bleibt stabil (keine Exceptions, keine korrupten Daten)
        assert len(repo.get_all_tasks()) == 0
