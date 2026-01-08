"""
Integrationstests für TODO-App
Testet das Zusammenspiel: Controller ↔ Repository ↔ Dateisystem
pytest -q tests/test_integration.py
"""
import pytest
from model import Task, TaskRepository
from controller import TaskController


@pytest.fixture
def setup(tmp_path):
    """Controller + Repository mit echter Datei"""
    repo = TaskRepository(tmp_path / "data.json")
    return {"repo": repo, "ctrl": TaskController(repo)}


class TestIntegration:
    """3 Integrationstests gemäß Aufgabenstellung"""
    
    def test_mehrere_aufgaben_repository_konsistent(self, setup):
        """
        Test 1: Mehrere Aufgaben erstellen → Repository-Schicht bleibt konsistent
        """
        ctrl, repo = setup["ctrl"], setup["repo"]
        
        # Act: Mehrere Tasks erstellen
        ctrl.create_task("Aufgabe 1")
        ctrl.create_task("Aufgabe 2")
        ctrl.create_task("Aufgabe 3")
        
        # Assert: Repository konsistent
        tasks = repo.get_all_tasks()
        assert len(tasks) == 3
        ids = [t.id for t in tasks]
        assert len(ids) == len(set(ids))  # IDs eindeutig
    
    def test_status_aendern_repository_aktualisiert(self, setup):
        """
        Test 2: Status ändern → Status korrekt im Repository aktualisiert
        """
        ctrl, repo = setup["ctrl"], setup["repo"]
        
        # Arrange
        ctrl.create_task("Aufgabe")
        task_id = repo.get_all_tasks()[0].id
        
        # Act: Status auf "erledigt" ändern
        ctrl.toggle_task_completion(task_id)
        
        # Assert: Im Archiv mit completed=True
        archived = repo.get_archived_tasks()
        assert len(archived) == 1
        assert archived[0].completed is True
    
    def test_leere_aufgabe_kontrollierter_fehler(self, setup):
        """
        Test 3: Leere Aufgabe → Repository wirft kontrollierten Fehler
        """
        ctrl, repo = setup["ctrl"], setup["repo"]
        
        # Act: Leere Aufgabe erstellen
        result = ctrl.create_task("")
        
        # Assert: Abgelehnt, Repository unverändert
        assert result is False
        assert len(repo.get_all_tasks()) == 0
