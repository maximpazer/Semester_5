"""
Unit Test nach AAA 
python -m pytest tests/test_unit.py -v --tb=short && python -m pytest tests/test_unit.py --cov=model --cov=controller --cov-report=term-missing && wc -l tests/test_unit.py
"""

import pytest
from datetime import date
from model import Task, Category, TaskRepository
from controller import TaskController




@pytest.fixture
def repo(tmp_path):
    return TaskRepository(tmp_path / "test.json")


@pytest.fixture
def ctrl(repo):
    return TaskController(repo)

# Kernfunktionen
class TestKernfunktionen:

    def test_hinzufuegen(self, ctrl):
        """1. Hinzufügen eines TODO-Items"""

        # Arrange
        title = "Einkaufen"

        # Act
        result = ctrl.create_task(title)
        tasks = ctrl.get_all_tasks()

        # Assert
        assert result is True
        assert len(tasks) == 1
        assert tasks[0].title == title

    def test_entfernen(self, ctrl):
        """2. Entfernen eines Items"""

        # Arrange
        ctrl.create_task("Löschen")

        # Act
        result = ctrl.delete_task(1)
        tasks = ctrl.get_all_tasks()

        # Assert
        assert result is True
        assert len(tasks) == 0

    def test_erledigt_markieren(self, ctrl):
        """3a. Markieren als erledigt"""

        # Arrange
        ctrl.create_task("Aufgabe")

        # Act
        result = ctrl.toggle_task_completion(1)
        archived = ctrl.get_archived_tasks()

        # Assert
        assert result is True
        assert archived[0].completed is True

    def test_nicht_erledigt_markieren(self, ctrl):
        """3b. Markieren als nicht erledigt"""

        # Arrange
        ctrl.create_task("Aufgabe")
        ctrl.toggle_task_completion(1)

        # Act
        result = ctrl.restore_task(1)
        task = ctrl.get_task(1)

        # Assert
        assert result is True
        assert task.completed is False

    def test_bearbeiten(self, ctrl):
        """4. Bearbeiten eines Items"""

        # Arrange
        ctrl.create_task("Alt")

        # Act
        result = ctrl.update_task(1, "Neu", "Arbeit")
        task = ctrl.get_task(1)

        # Assert
        assert result is True
        assert task.title == "Neu"
        assert task.category == "Arbeit"


# Fehlerfälle
class TestFehlerfaelle:

    def test_leerer_titel(self, ctrl):
        """Leere oder ungültige Titel dürfen nicht erstellt werden"""

        # Arrange
        invalid_titles = ["", "   "]

        # Act & Assert
        for title in invalid_titles:
            result = ctrl.create_task(title)
            assert result is False

    def test_nicht_vorhanden(self, ctrl):
        """Löschen einer nicht existierenden Task"""

        # Arrange
        non_existing_id = 999

        # Act
        result = ctrl.delete_task(non_existing_id)

        # Assert
        assert result is False

    def test_doppelte_titel(self, ctrl):
        """Doppelte Titel sind erlaubt"""

        # Arrange
        ctrl.create_task("X")

        # Act
        ctrl.create_task("X")
        tasks = ctrl.get_all_tasks()

        # Assert
        assert len(tasks) == 2


# Coverage Tests

class TestCoverage:

    def test_task_basics(self):
        """Grundfunktionen von Task"""

        # Arrange
        today = date.today().isoformat()
        task = Task(1, "Test", completed=True, category="A", due_date=today)

        # Act
        is_valid = task.validate()
        is_urgent = task.is_urgent()
        data = task.to_dict()
        restored = Task.from_dict(data)

        # Assert
        assert is_valid is True
        assert is_urgent is True
        assert restored.title == "Test"
        assert Task(1, "").validate() is False

    def test_category(self):
        """Validierung von Kategorien"""

        # Arrange
        valid = Category("Valid")
        invalid = Category("")

        # Act & Assert
        assert valid.validate() is True
        assert invalid.validate() is False

    def test_repository_ops(self, repo):
        """Repository CRUD-Operationen"""

        # Arrange
        task_a = Task(0, "A", category="Arbeit")
        task_b = Task(0, "B", category="Privat")

        # Act
        repo.add_task(task_a)
        repo.add_task(task_b)

        found = repo.get_task_by_id(1)
        not_found = repo.get_task_by_id(999)

        arbeit_tasks = repo.filter_tasks(category="Arbeit")
        offene_tasks = repo.filter_tasks(status="Offen")

        repo.update_task(Task(1, "Updated"))
        updated_task = repo.get_task_by_id(1)

        # Assert
        assert found is not None
        assert not_found is None
        assert len(arbeit_tasks) == 1
        assert len(offene_tasks) == 2
        assert updated_task.title == "Updated"

    def test_kategorie_ops(self, repo):
        """Hinzufügen und Entfernen von Kategorien"""

        # Arrange
        category = Category("Sport")

        # Act
        repo.add_category(category)
        names = [c["name"] for c in repo.get_categories()]
        repo.delete_category("Sport")

        # Assert
        assert "Sport" in names

    def test_dringende_tasks(self, repo):
        """Dringende Tasks erkennen"""

        # Arrange
        urgent_task = Task(0, "Dringend", due_date=date.today().isoformat())

        # Act
        repo.add_task(urgent_task)
        urgent_tasks = repo.get_urgent_tasks()

        # Assert
        assert len(urgent_tasks) == 1

    def test_persistenz(self, tmp_path):
        """Speichern und Laden aus Datei"""

        # Arrange
        file_path = tmp_path / "d.json"
        repo1 = TaskRepository(file_path)

        # Act
        repo1.add_task(Task(0, "P"))
        repo1.save()

        repo2 = TaskRepository(file_path)
        tasks = repo2.get_all_tasks()

        # Assert
        assert len(tasks) == 1
