"""
Unit Tests für TODO-App
Verwendet pytest mit AAA-Muster (Arrange-Act-Assert)
Ziel: >80% Code Coverage
"""

import pytest
import json
from pathlib import Path
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch, mock_open
from model import Task, Category, TaskRepository
from controller import TaskController, CategoryController, ApplicationController


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_data_file(tmp_path):
    """Erstellt temporäre Datei für Tests"""
    return tmp_path / "test_todo_data.json"


@pytest.fixture
def empty_repository(temp_data_file):
    """Erstellt leeres Repository"""
    return TaskRepository(temp_data_file)


@pytest.fixture
def repository_with_tasks(temp_data_file):
    """Erstellt Repository mit Beispiel-Tasks"""
    repo = TaskRepository(temp_data_file)
    repo.add_task(Task(0, "Task 1", category="Arbeit"))
    repo.add_task(Task(0, "Task 2", category="Privat"))
    repo.add_task(Task(0, "Task 3", completed=True))
    return repo


@pytest.fixture
def task_controller(empty_repository):
    """Erstellt TaskController mit leerem Repository"""
    return TaskController(empty_repository)


@pytest.fixture
def category_controller(empty_repository):
    """Erstellt CategoryController mit leerem Repository"""
    return CategoryController(empty_repository)


# ============================================================================
# TESTS FÜR TASK-KLASSE (Domänenobjekt)
# ============================================================================

class TestTask:
    """Tests für Task-Domänenobjekt"""
    
    def test_task_creation_with_valid_data(self):
        """Test: Task mit gültigen Daten erstellen"""
        # Arrange
        task_id = 1
        title = "Test Task"
        
        # Act
        task = Task(id=task_id, title=title)
        
        # Assert
        assert task.id == task_id
        assert task.title == title
        assert task.completed is False
        assert task.category == "Keine"
        assert task.due_date is None
    
    def test_task_creation_with_all_parameters(self):
        """Test: Task mit allen Parametern erstellen"""
        # Arrange
        task_data = {
            "id": 5,
            "title": "Complete Task",
            "completed": True,
            "category": "Arbeit",
            "due_date": "2025-12-31"
        }
        
        # Act
        task = Task(**task_data)
        
        # Assert
        assert task.id == 5
        assert task.title == "Complete Task"
        assert task.completed is True
        assert task.category == "Arbeit"
        assert task.due_date == "2025-12-31"
    
    def test_task_validate_returns_true_for_valid_title(self):
        """Test: Validierung gibt True für gültigen Titel zurück"""
        # Arrange
        task = Task(id=1, title="Valid Title")
        
        # Act
        result = task.validate()
        
        # Assert
        assert result is True
    
    def test_task_validate_returns_false_for_empty_title(self):
        """Test: Validierung gibt False für leeren Titel zurück"""
        # Arrange
        task = Task(id=1, title="")
        
        # Act
        result = task.validate()
        
        # Assert
        assert result is False
    
    def test_task_validate_returns_false_for_whitespace_title(self):
        """Test: Validierung gibt False für Whitespace-Titel zurück"""
        # Arrange
        task = Task(id=1, title="   ")
        
        # Act
        result = task.validate()
        
        # Assert
        assert result is False
    
    def test_task_is_urgent_returns_true_for_today(self):
        """Test: is_urgent gibt True für heute fällige Task zurück"""
        # Arrange
        today = date.today().isoformat()
        task = Task(id=1, title="Urgent", due_date=today)
        
        # Act
        result = task.is_urgent()
        
        # Assert
        assert result is True
    
    def test_task_is_urgent_returns_true_for_tomorrow(self):
        """Test: is_urgent gibt True für morgen fällige Task zurück"""
        # Arrange
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        task = Task(id=1, title="Urgent", due_date=tomorrow)
        
        # Act
        result = task.is_urgent()
        
        # Assert
        assert result is True
    
    def test_task_is_urgent_returns_false_for_future_date(self):
        """Test: is_urgent gibt False für zukünftiges Datum zurück"""
        # Arrange
        future = (date.today() + timedelta(days=5)).isoformat()
        task = Task(id=1, title="Not Urgent", due_date=future)
        
        # Act
        result = task.is_urgent()
        
        # Assert
        assert result is False
    
    def test_task_is_urgent_returns_false_for_no_due_date(self):
        """Test: is_urgent gibt False für Task ohne Fälligkeitsdatum zurück"""
        # Arrange
        task = Task(id=1, title="No Date")
        
        # Act
        result = task.is_urgent()
        
        # Assert
        assert result is False
    
    def test_task_to_dict_serializes_correctly(self):
        """Test: to_dict serialisiert Task korrekt"""
        # Arrange
        task = Task(id=10, title="Test", completed=True, 
                   category="Arbeit", due_date="2025-12-25")
        
        # Act
        result = task.to_dict()
        
        # Assert
        assert result == {
            "id": 10,
            "title": "Test",
            "completed": True,
            "category": "Arbeit",
            "due_date": "2025-12-25"
        }
    
    def test_task_from_dict_deserializes_correctly(self):
        """Test: from_dict deserialisiert Task korrekt"""
        # Arrange
        data = {
            "id": 15,
            "title": "Deserialized",
            "completed": False,
            "category": "Privat",
            "due_date": "2026-01-01"
        }
        
        # Act
        task = Task.from_dict(data)
        
        # Assert
        assert task.id == 15
        assert task.title == "Deserialized"
        assert task.completed is False
        assert task.category == "Privat"
        assert task.due_date == "2026-01-01"
    
    def test_task_from_dict_with_missing_optional_fields(self):
        """Test: from_dict mit fehlenden optionalen Feldern"""
        # Arrange
        data = {"id": 20, "title": "Minimal"}
        
        # Act
        task = Task.from_dict(data)
        
        # Assert
        assert task.id == 20
        assert task.title == "Minimal"
        assert task.completed is False
        assert task.category == "Keine"
        assert task.due_date is None


# ============================================================================
# TESTS FÜR CATEGORY-KLASSE
# ============================================================================

class TestCategory:
    """Tests für Category-Domänenobjekt"""
    
    def test_category_creation_with_valid_name(self):
        """Test: Kategorie mit gültigem Namen erstellen"""
        # Arrange
        name = "Arbeit"
        
        # Act
        category = Category(name)
        
        # Assert
        assert category.name == name
    
    def test_category_validate_returns_true_for_valid_name(self):
        """Test: Validierung gibt True für gültigen Namen zurück"""
        # Arrange
        category = Category("Valid Name")
        
        # Act
        result = category.validate()
        
        # Assert
        assert result is True
    
    def test_category_validate_returns_false_for_empty_name(self):
        """Test: Validierung gibt False für leeren Namen zurück"""
        # Arrange
        category = Category("")
        
        # Act
        result = category.validate()
        
        # Assert
        assert result is False
    
    def test_category_validate_returns_false_for_whitespace_name(self):
        """Test: Validierung gibt False für Whitespace-Namen zurück"""
        # Arrange
        category = Category("   ")
        
        # Act
        result = category.validate()
        
        # Assert
        assert result is False
    
    def test_category_max_categories_constant(self):
        """Test: MAX_CATEGORIES Konstante ist korrekt gesetzt"""
        # Arrange & Act
        max_categories = Category.MAX_CATEGORIES
        
        # Assert
        assert max_categories == 8


# ============================================================================
# TESTS FÜR TASKREPOSITORY (Datenzugriff)
# ============================================================================

class TestTaskRepository:
    """Tests für TaskRepository"""
    
    def test_repository_initialization_creates_default_data(self, temp_data_file):
        """Test: Repository-Initialisierung erstellt Standard-Daten"""
        # Arrange & Act
        repo = TaskRepository(temp_data_file)
        
        # Assert
        assert repo.data["tasks"] == []
        assert repo.data["archived_tasks"] == []
        # Kategorien sind jetzt Objekte mit name und color
        category_names = [c["name"] for c in repo.data["categories"]]
        assert "Arbeit" in category_names
        assert "Privat" in category_names
        assert repo.data["next_id"] == 1
    
    def test_repository_saves_data_to_file(self, temp_data_file):
        """Test: Repository speichert Daten in Datei"""
        # Arrange
        repo = TaskRepository(temp_data_file)
        repo.add_task(Task(0, "Test Task"))
        
        # Act
        repo.save()
        
        # Assert
        assert temp_data_file.exists()
        with open(temp_data_file, "r") as f:
            data = json.load(f)
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"
    
    def test_repository_loads_existing_data(self, temp_data_file):
        """Test: Repository lädt existierende Daten"""
        # Arrange - Daten mit neuer Kategorie-Struktur
        test_data = {
            "tasks": [{"id": 1, "title": "Existing", "completed": False, 
                      "category": "Keine", "due_date": None}],
            "archived_tasks": [],
            "categories": [{"name": "Test", "color": "#4e73df"}],
            "next_id": 2
        }
        with open(temp_data_file, "w") as f:
            json.dump(test_data, f)
        
        # Act
        repo = TaskRepository(temp_data_file)
        
        # Assert
        assert len(repo.data["tasks"]) == 1
        assert repo.data["tasks"][0]["title"] == "Existing"
        assert repo.data["categories"][0]["name"] == "Test"
        assert repo.data["next_id"] == 2
    
    def test_add_task_with_valid_task(self, empty_repository):
        """Test: Hinzufügen einer gültigen Task (FR-00)"""
        # Arrange
        task = Task(0, "New Task")
        
        # Act
        result = empty_repository.add_task(task)
        
        # Assert
        assert result is True
        assert len(empty_repository.data["tasks"]) == 1
        assert empty_repository.data["tasks"][0]["title"] == "New Task"
        assert empty_repository.data["tasks"][0]["id"] == 1
    
    def test_add_task_with_invalid_task(self, empty_repository):
        """Test: Hinzufügen einer ungültigen Task schlägt fehl"""
        # Arrange
        task = Task(0, "")  # Leerer Titel
        
        # Act
        result = empty_repository.add_task(task)
        
        # Assert
        assert result is False
        assert len(empty_repository.data["tasks"]) == 0
    
    def test_add_task_increments_id(self, empty_repository):
        """Test: Hinzufügen von Tasks inkrementiert ID"""
        # Arrange
        task1 = Task(0, "Task 1")
        task2 = Task(0, "Task 2")
        
        # Act
        empty_repository.add_task(task1)
        empty_repository.add_task(task2)
        
        # Assert - Neue Tasks werden oben eingefügt (insert(0))
        assert empty_repository.data["tasks"][0]["id"] == 2  # Neueste zuerst
        assert empty_repository.data["tasks"][1]["id"] == 1
        assert empty_repository.data["next_id"] == 3
    
    def test_get_all_tasks_returns_all_active_tasks(self, repository_with_tasks):
        """Test: get_all_tasks gibt alle aktiven Tasks zurück"""
        # Arrange & Act
        tasks = repository_with_tasks.get_all_tasks()
        
        # Assert
        assert len(tasks) == 3
        assert all(isinstance(t, Task) for t in tasks)
    
    def test_get_task_by_id_returns_correct_task(self, repository_with_tasks):
        """Test: get_task_by_id gibt korrekte Task zurück"""
        # Arrange
        task_id = 1
        
        # Act
        task = repository_with_tasks.get_task_by_id(task_id)
        
        # Assert
        assert task is not None
        assert task.id == task_id
        assert task.title == "Task 1"
    
    def test_get_task_by_id_returns_none_for_nonexistent_id(self, repository_with_tasks):
        """Test: get_task_by_id gibt None für nicht existierende ID zurück"""
        # Arrange
        nonexistent_id = 999
        
        # Act
        task = repository_with_tasks.get_task_by_id(nonexistent_id)
        
        # Assert
        assert task is None
    
    def test_update_task_with_valid_data(self, repository_with_tasks):
        """Test: Aktualisieren einer Task mit gültigen Daten (FR-03)"""
        # Arrange
        updated_task = Task(id=1, title="Updated Title", category="Neu")
        
        # Act
        result = repository_with_tasks.update_task(updated_task)
        
        # Assert
        assert result is True
        task = repository_with_tasks.get_task_by_id(1)
        assert task.title == "Updated Title"
        assert task.category == "Neu"
    
    def test_update_task_with_invalid_data(self, repository_with_tasks):
        """Test: Aktualisieren mit ungültigen Daten schlägt fehl"""
        # Arrange
        invalid_task = Task(id=1, title="")  # Leerer Titel
        
        # Act
        result = repository_with_tasks.update_task(invalid_task)
        
        # Assert
        assert result is False
        # Original bleibt unverändert
        task = repository_with_tasks.get_task_by_id(1)
        assert task.title == "Task 1"
    
    def test_update_nonexistent_task(self, repository_with_tasks):
        """Test: Aktualisieren nicht existierender Task"""
        # Arrange
        nonexistent_task = Task(id=999, title="Nonexistent")
        
        # Act
        result = repository_with_tasks.update_task(nonexistent_task)
        
        # Assert
        assert result is False
    
    def test_delete_task_removes_task(self, repository_with_tasks):
        """Test: Löschen einer Task entfernt sie (FR-02)"""
        # Arrange
        task_id = 1
        initial_count = len(repository_with_tasks.get_all_tasks())
        
        # Act
        result = repository_with_tasks.delete_task(task_id)
        
        # Assert
        assert result is True
        assert len(repository_with_tasks.get_all_tasks()) == initial_count - 1
        assert repository_with_tasks.get_task_by_id(task_id) is None
    
    def test_delete_nonexistent_task(self, repository_with_tasks):
        """Test: Löschen nicht existierender Task"""
        # Arrange
        nonexistent_id = 999
        
        # Act
        result = repository_with_tasks.delete_task(nonexistent_id)
        
        # Assert
        assert result is False
    
    def test_toggle_task_completion_marks_incomplete_as_complete(self, repository_with_tasks):
        """Test: Toggle markiert offene Task als erledigt (FR-04)"""
        # Arrange
        task_id = 1
        task = repository_with_tasks.get_task_by_id(task_id)
        assert task.completed is False
        
        # Act
        result = repository_with_tasks.toggle_task_completion(task_id)
        
        # Assert
        assert result is True
        # Task sollte ins Archiv verschoben werden
        archived = repository_with_tasks.get_archived_tasks()
        assert any(t.id == task_id for t in archived)
        # Task sollte aus aktiven Tasks entfernt sein
        assert repository_with_tasks.get_task_by_id(task_id) is None
    
    def test_toggle_task_completion_archives_completed_task(self, empty_repository):
        """Test: Erledigte Task wird archiviert"""
        # Arrange
        empty_repository.add_task(Task(0, "To Complete"))
        task_id = 1
        
        # Act
        empty_repository.toggle_task_completion(task_id)
        
        # Assert
        archived = empty_repository.get_archived_tasks()
        assert len(archived) == 1
        assert archived[0].id == task_id
        assert archived[0].completed is True
    
    def test_restore_task_from_archive(self, empty_repository):
        """Test: Wiederherstellen archivierter Task"""
        # Arrange
        empty_repository.add_task(Task(0, "To Archive"))
        task_id = 1
        empty_repository.toggle_task_completion(task_id)  # Archivieren
        
        # Act
        result = empty_repository.restore_task(task_id)
        
        # Assert
        assert result is True
        # Task ist wieder in aktiven Tasks
        task = empty_repository.get_task_by_id(task_id)
        assert task is not None
        assert task.completed is False
        # Task ist nicht mehr im Archiv
        archived = empty_repository.get_archived_tasks()
        assert len(archived) == 0
    
    def test_restore_nonexistent_archived_task(self, empty_repository):
        """Test: Wiederherstellen nicht existierender archivierter Task"""
        # Arrange
        nonexistent_id = 999
        
        # Act
        result = empty_repository.restore_task(nonexistent_id)
        
        # Assert
        assert result is False
    
    def test_get_categories_returns_all_categories(self, empty_repository):
        """Test: get_categories gibt alle Kategorien zurück"""
        # Arrange & Act
        categories = empty_repository.get_categories()
        
        # Assert - Kategorien sind jetzt Objekte mit name und color
        assert isinstance(categories, list)
        category_names = [c["name"] for c in categories]
        assert "Arbeit" in category_names
        assert "Privat" in category_names
    
    def test_add_category_with_valid_name(self, empty_repository):
        """Test: Hinzufügen gültiger Kategorie (FR-06)"""
        # Arrange
        category = Category("Sport", "#ff0000")
        
        # Act
        result = empty_repository.add_category(category)
        
        # Assert
        assert result is True
        category_names = [c["name"] for c in empty_repository.get_categories()]
        assert "Sport" in category_names
    
    def test_add_category_with_invalid_name(self, empty_repository):
        """Test: Hinzufügen ungültiger Kategorie"""
        # Arrange
        category = Category("")  # Leerer Name
        
        # Act
        result = empty_repository.add_category(category)
        
        # Assert
        assert result is False
    
    def test_add_duplicate_category(self, empty_repository):
        """Test: Hinzufügen doppelter Kategorie"""
        # Arrange
        category = Category("Arbeit")  # Existiert bereits
        
        # Act
        result = empty_repository.add_category(category)
        
        # Assert
        assert result is False
    
    def test_add_category_exceeds_maximum(self, empty_repository):
        """Test: Hinzufügen über Maximum schlägt fehl"""
        # Arrange - Repository hat bereits 2 Kategorien, Maximum ist 8
        empty_repository.add_category(Category("Cat3"))
        empty_repository.add_category(Category("Cat4"))
        empty_repository.add_category(Category("Cat5"))
        empty_repository.add_category(Category("Cat6"))
        empty_repository.add_category(Category("Cat7"))
        empty_repository.add_category(Category("Cat8"))
        # Jetzt sind 8 Kategorien vorhanden (Maximum)
        
        # Act
        result = empty_repository.add_category(Category("Cat9"))
        
        # Assert
        assert result is False
        assert len(empty_repository.get_categories()) == 8
    
    def test_delete_category_removes_category(self, empty_repository):
        """Test: Löschen einer Kategorie"""
        # Arrange
        category_name = "Arbeit"
        
        # Act
        result = empty_repository.delete_category(category_name)
        
        # Assert
        assert result is True
        category_names = [c["name"] for c in empty_repository.get_categories()]
        assert category_name not in category_names
    
    def test_delete_category_updates_tasks(self, empty_repository):
        """Test: Löschen einer Kategorie setzt Tasks auf 'Keine'"""
        # Arrange
        empty_repository.add_task(Task(0, "Task 1", category="Arbeit"))
        empty_repository.add_task(Task(0, "Task 2", category="Privat"))
        
        # Act
        empty_repository.delete_category("Arbeit")
        
        # Assert
        tasks = empty_repository.get_all_tasks()
        task1 = next(t for t in tasks if t.title == "Task 1")
        assert task1.category == "Keine"
    
    def test_delete_nonexistent_category(self, empty_repository):
        """Test: Löschen nicht existierender Kategorie gibt True zurück (keine Fehler)"""
        # Arrange
        nonexistent = "Nonexistent"
        initial_count = len(empty_repository.get_categories())
        
        # Act
        result = empty_repository.delete_category(nonexistent)
        
        # Assert - delete_category gibt immer True zurück (keine Ausnahme)
        assert result is True
        assert len(empty_repository.get_categories()) == initial_count
    
    def test_filter_tasks_by_status_open(self, repository_with_tasks):
        """Test: Filtern nach Status 'Offen' (FR-07)"""
        # Arrange & Act
        filtered = repository_with_tasks.filter_tasks(status="Offen")
        
        # Assert
        assert len(filtered) == 2
        assert all(not t.completed for t in filtered)
    
    def test_filter_tasks_by_status_completed(self, repository_with_tasks):
        """Test: Filtern nach Status 'Erledigt' (FR-07)"""
        # Arrange & Act
        filtered = repository_with_tasks.filter_tasks(status="Erledigt")
        
        # Assert
        assert len(filtered) == 1
        assert all(t.completed for t in filtered)
    
    def test_filter_tasks_by_category(self, repository_with_tasks):
        """Test: Filtern nach Kategorie (FR-07)"""
        # Arrange & Act
        filtered = repository_with_tasks.filter_tasks(category="Arbeit")
        
        # Assert
        assert len(filtered) == 1
        assert all(t.category == "Arbeit" for t in filtered)
    
    def test_filter_tasks_by_status_and_category(self, repository_with_tasks):
        """Test: Filtern nach Status und Kategorie"""
        # Arrange & Act
        filtered = repository_with_tasks.filter_tasks(status="Offen", category="Arbeit")
        
        # Assert
        assert len(filtered) == 1
        assert filtered[0].category == "Arbeit"
        assert not filtered[0].completed
    
    def test_filter_tasks_with_no_filters_returns_all(self, repository_with_tasks):
        """Test: Keine Filter gibt alle Tasks zurück"""
        # Arrange & Act
        filtered = repository_with_tasks.filter_tasks()
        
        # Assert
        assert len(filtered) == 3
    
    def test_get_urgent_tasks_returns_only_urgent(self, empty_repository):
        """Test: get_urgent_tasks gibt nur dringliche Tasks zurück"""
        # Arrange
        today = date.today().isoformat()
        future = (date.today() + timedelta(days=5)).isoformat()
        empty_repository.add_task(Task(0, "Urgent", due_date=today))
        empty_repository.add_task(Task(0, "Not Urgent", due_date=future))
        empty_repository.add_task(Task(0, "No Date"))
        
        # Act
        urgent = empty_repository.get_urgent_tasks()
        
        # Assert
        assert len(urgent) == 1
        assert urgent[0].title == "Urgent"


# ============================================================================
# TESTS FÜR TASKCONTROLLER (Geschäftslogik)
# ============================================================================

class TestTaskController:
    """Tests für TaskController"""
    
    def test_create_task_with_valid_data(self, task_controller):
        """Test: Erstellen einer Task mit gültigen Daten"""
        # Arrange
        title = "New Task"
        category = "Arbeit"
        due_date = date.today()
        
        # Act
        result = task_controller.create_task(title, category, due_date)
        
        # Assert
        assert result is True
        tasks = task_controller.get_all_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "New Task"
        assert tasks[0].category == "Arbeit"
    
    def test_create_task_with_empty_title(self, task_controller):
        """Test: Erstellen mit leerem Titel schlägt fehl"""
        # Arrange
        title = ""
        
        # Act
        result = task_controller.create_task(title)
        
        # Assert
        assert result is False
        assert len(task_controller.get_all_tasks()) == 0
    
    def test_create_task_strips_whitespace(self, task_controller):
        """Test: Erstellen strippt Whitespace vom Titel"""
        # Arrange
        title = "  Task with spaces  "
        
        # Act
        result = task_controller.create_task(title)
        
        # Assert
        assert result is True
        tasks = task_controller.get_all_tasks()
        assert tasks[0].title == "Task with spaces"
    
    def test_create_task_without_optional_parameters(self, task_controller):
        """Test: Erstellen ohne optionale Parameter"""
        # Arrange
        title = "Minimal Task"
        
        # Act
        result = task_controller.create_task(title)
        
        # Assert
        assert result is True
        tasks = task_controller.get_all_tasks()
        assert tasks[0].category == "Keine"
        assert tasks[0].due_date is None
    
    def test_get_all_tasks_returns_all_tasks(self, task_controller):
        """Test: get_all_tasks gibt alle Tasks zurück"""
        # Arrange
        task_controller.create_task("Task 1")
        task_controller.create_task("Task 2")
        task_controller.create_task("Task 3")
        
        # Act
        tasks = task_controller.get_all_tasks()
        
        # Assert
        assert len(tasks) == 3
    
    def test_get_filtered_tasks_with_status_filter(self, task_controller):
        """Test: Gefilterte Tasks nach Status"""
        # Arrange
        task_controller.create_task("Open Task")
        task_controller.create_task("Another Open")
        task_controller.repository.toggle_task_completion(1)  # Erste erledigen
        
        # Act
        open_tasks = task_controller.get_filtered_tasks(status="Offen")
        
        # Assert
        assert len(open_tasks) == 1
        assert open_tasks[0].title == "Another Open"
    
    def test_get_filtered_tasks_with_category_filter(self, task_controller):
        """Test: Gefilterte Tasks nach Kategorie"""
        # Arrange
        task_controller.create_task("Work Task", category="Arbeit")
        task_controller.create_task("Personal Task", category="Privat")
        
        # Act
        work_tasks = task_controller.get_filtered_tasks(category="Arbeit")
        
        # Assert
        assert len(work_tasks) == 1
        assert work_tasks[0].category == "Arbeit"
    
    def test_get_task_returns_specific_task(self, task_controller):
        """Test: get_task gibt spezifische Task zurück"""
        # Arrange
        task_controller.create_task("Specific Task")
        task_id = 1
        
        # Act
        task = task_controller.get_task(task_id)
        
        # Assert
        assert task is not None
        assert task.id == task_id
    
    def test_get_archived_tasks_returns_archived_only(self, task_controller):
        """Test: get_archived_tasks gibt nur archivierte zurück"""
        # Arrange
        task_controller.create_task("Task 1")
        task_controller.create_task("Task 2")
        task_controller.toggle_task_completion(1)  # Archivieren
        
        # Act
        archived = task_controller.get_archived_tasks()
        
        # Assert
        assert len(archived) == 1
        assert archived[0].completed is True
    
    def test_get_urgent_tasks_returns_urgent_only(self, task_controller):
        """Test: get_urgent_tasks gibt nur dringliche zurück"""
        # Arrange
        today = date.today()
        future = date.today() + timedelta(days=5)
        task_controller.create_task("Urgent", due_date=today)
        task_controller.create_task("Not Urgent", due_date=future)
        
        # Act
        urgent = task_controller.get_urgent_tasks()
        
        # Assert
        assert len(urgent) == 1
        assert urgent[0].title == "Urgent"
    
    def test_update_task_with_valid_data(self, task_controller):
        """Test: Aktualisieren mit gültigen Daten"""
        # Arrange
        task_controller.create_task("Original")
        task_id = 1
        
        # Act
        result = task_controller.update_task(
            task_id, "Updated", "Arbeit", date.today()
        )
        
        # Assert
        assert result is True
        task = task_controller.get_task(task_id)
        assert task.title == "Updated"
        assert task.category == "Arbeit"
    
    def test_update_task_with_empty_title(self, task_controller):
        """Test: Aktualisieren mit leerem Titel schlägt fehl"""
        # Arrange
        task_controller.create_task("Original")
        task_id = 1
        
        # Act
        result = task_controller.update_task(task_id, "", "Arbeit")
        
        # Assert
        assert result is False
        # Original bleibt unverändert
        task = task_controller.get_task(task_id)
        assert task.title == "Original"
    
    def test_toggle_task_completion_changes_status(self, task_controller):
        """Test: Toggle ändert Erledigungsstatus"""
        # Arrange
        task_controller.create_task("Task")
        task_id = 1
        
        # Act
        result = task_controller.toggle_task_completion(task_id)
        
        # Assert
        assert result is True
        # Task sollte archiviert sein
        archived = task_controller.get_archived_tasks()
        assert len(archived) == 1
    
    def test_restore_task_moves_from_archive_to_active(self, task_controller):
        """Test: Wiederherstellen verschiebt von Archiv zu aktiv"""
        # Arrange
        task_controller.create_task("Task")
        task_id = 1
        task_controller.toggle_task_completion(task_id)  # Archivieren
        
        # Act
        result = task_controller.restore_task(task_id)
        
        # Assert
        assert result is True
        task = task_controller.get_task(task_id)
        assert task is not None
        assert task.completed is False
        archived = task_controller.get_archived_tasks()
        assert len(archived) == 0
    
    def test_delete_task_removes_task(self, task_controller):
        """Test: Löschen entfernt Task"""
        # Arrange
        task_controller.create_task("To Delete")
        task_id = 1
        
        # Act
        result = task_controller.delete_task(task_id)
        
        # Assert
        assert result is True
        assert len(task_controller.get_all_tasks()) == 0
    
    def test_get_statistics_calculates_correctly(self, task_controller):
        """Test: Statistiken werden korrekt berechnet"""
        # Arrange
        task_controller.create_task("Open 1")
        task_controller.create_task("Open 2")
        task_controller.create_task("Done")
        task_controller.toggle_task_completion(3)  # Eine erledigen
        
        # Act
        stats = task_controller.get_statistics()
        
        # Assert
        assert stats["total"] == 2  # Nur aktive
        assert stats["open"] == 2
        assert stats["done"] == 0
        assert stats["archived"] == 1


# ============================================================================
# TESTS FÜR CATEGORYCONTROLLER
# ============================================================================

class TestCategoryController:
    """Tests für CategoryController"""
    
    def test_get_all_categories_returns_default_categories(self, category_controller):
        """Test: get_all_categories gibt Standard-Kategorien zurück"""
        # Arrange & Act
        categories = category_controller.get_all_categories()
        
        # Assert
        assert "Arbeit" in categories
        assert "Privat" in categories
    
    def test_create_category_adds_new_category(self, category_controller):
        """Test: Erstellen fügt neue Kategorie hinzu"""
        # Arrange
        name = "Sport"
        
        # Act
        result = category_controller.create_category(name)
        
        # Assert
        assert result is True
        assert "Sport" in category_controller.get_all_categories()
    
    def test_create_category_strips_whitespace(self, category_controller):
        """Test: Erstellen strippt Whitespace"""
        # Arrange
        name = "  Freizeit  "
        
        # Act
        result = category_controller.create_category(name)
        
        # Assert
        assert result is True
        assert "Freizeit" in category_controller.get_all_categories()
    
    def test_create_category_with_empty_name(self, category_controller):
        """Test: Erstellen mit leerem Namen schlägt fehl"""
        # Arrange
        name = ""
        
        # Act
        result = category_controller.create_category(name)
        
        # Assert
        assert result is False
    
    def test_delete_category_removes_category(self, category_controller):
        """Test: Löschen entfernt Kategorie"""
        # Arrange
        name = "Arbeit"
        
        # Act
        result = category_controller.delete_category(name)
        
        # Assert
        assert result is True
        assert name not in category_controller.get_all_categories()
    
    def test_can_add_category_returns_true_when_below_max(self, category_controller):
        """Test: can_add_category gibt True zurück wenn unter Maximum"""
        # Arrange - Standardmäßig 2 Kategorien
        
        # Act
        result = category_controller.can_add_category()
        
        # Assert
        assert result is True
    
    def test_can_add_category_returns_false_when_at_max(self, category_controller):
        """Test: can_add_category gibt False zurück wenn bei Maximum"""
        # Arrange - Auf 8 Kategorien auffüllen (Maximum)
        category_controller.create_category("Cat3")
        category_controller.create_category("Cat4")
        category_controller.create_category("Cat5")
        category_controller.create_category("Cat6")
        category_controller.create_category("Cat7")
        category_controller.create_category("Cat8")
        
        # Act
        result = category_controller.can_add_category()
        
        # Assert
        assert result is False


# ============================================================================
# TESTS FÜR APPLICATIONCONTROLLER
# ============================================================================

class TestApplicationController:
    """Tests für ApplicationController"""
    
    def test_initialization_creates_controllers(self):
        """Test: Initialisierung erstellt Controller"""
        # Arrange & Act
        app_controller = ApplicationController()
        
        # Assert
        assert app_controller.repository is not None
        assert app_controller.task_controller is not None
        assert app_controller.category_controller is not None
    
    def test_get_task_controller_returns_task_controller(self):
        """Test: get_task_controller gibt TaskController zurück"""
        # Arrange
        app_controller = ApplicationController()
        
        # Act
        task_controller = app_controller.get_task_controller()
        
        # Assert
        assert isinstance(task_controller, TaskController)
    
    def test_get_category_controller_returns_category_controller(self):
        """Test: get_category_controller gibt CategoryController zurück"""
        # Arrange
        app_controller = ApplicationController()
        
        # Act
        category_controller = app_controller.get_category_controller()
        
        # Assert
        assert isinstance(category_controller, CategoryController)


# ============================================================================
# EDGE CASES & FEHLERBEHANDLUNG
# ============================================================================

class TestEdgeCases:
    """Tests für Randbedingungen und Fehlerfälle"""
    
    def test_task_with_very_long_title(self, task_controller):
        """Test: Task mit sehr langem Titel"""
        # Arrange
        long_title = "A" * 500
        
        # Act
        result = task_controller.create_task(long_title)
        
        # Assert
        assert result is True
        task = task_controller.get_all_tasks()[0]
        assert len(task.title) == 500
    
    def test_task_with_special_characters_in_title(self, task_controller):
        """Test: Task mit Sonderzeichen im Titel"""
        # Arrange
        special_title = "Task with <>&\"' special chars"
        
        # Act
        result = task_controller.create_task(special_title)
        
        # Assert
        assert result is True
        task = task_controller.get_all_tasks()[0]
        assert task.title == special_title
    
    def test_multiple_tasks_with_same_title(self, task_controller):
        """Test: Mehrere Tasks mit gleichem Titel sind erlaubt"""
        # Arrange
        title = "Duplicate Title"
        
        # Act
        result1 = task_controller.create_task(title)
        result2 = task_controller.create_task(title)
        
        # Assert
        assert result1 is True
        assert result2 is True
        tasks = task_controller.get_all_tasks()
        assert len(tasks) == 2
        assert tasks[0].id != tasks[1].id
    
    def test_task_with_past_due_date(self, task_controller):
        """Test: Task mit vergangenem Fälligkeitsdatum"""
        # Arrange
        past_date = date.today() - timedelta(days=5)
        
        # Act
        result = task_controller.create_task("Past Due", due_date=past_date)
        
        # Assert
        assert result is True
        task = task_controller.get_all_tasks()[0]
        assert task.due_date is not None
    
    def test_repository_handles_corrupted_json(self, temp_data_file):
        """Test: Repository behandelt korrupte JSON-Datei"""
        # Arrange
        with open(temp_data_file, "w") as f:
            f.write("{ invalid json }")
        
        # Act
        repo = TaskRepository(temp_data_file)
        
        # Assert - Sollte Default-Daten verwenden
        assert repo.data["tasks"] == []
        category_names = [c["name"] for c in repo.data["categories"]]
        assert "Arbeit" in category_names
    
    def test_category_name_with_special_characters(self, category_controller):
        """Test: Kategorie mit Sonderzeichen"""
        # Arrange
        special_name = "Categóry-123 & Test"
        
        # Act
        result = category_controller.create_category(special_name)
        
        # Assert
        assert result is True
        assert special_name in category_controller.get_all_categories()
    
    def test_concurrent_task_creation_maintains_unique_ids(self, empty_repository):
        """Test: Gleichzeitige Task-Erstellung erhält eindeutige IDs"""
        # Arrange
        task1 = Task(0, "Task 1")
        task2 = Task(0, "Task 2")
        task3 = Task(0, "Task 3")
        
        # Act
        empty_repository.add_task(task1)
        empty_repository.add_task(task2)
        empty_repository.add_task(task3)
        
        # Assert
        tasks = empty_repository.get_all_tasks()
        ids = [t.id for t in tasks]
        assert len(ids) == len(set(ids))  # Alle IDs sind eindeutig
        # Neue Tasks werden oben eingefügt, daher ist Reihenfolge umgekehrt
        assert sorted(ids) == [1, 2, 3]
    
    def test_invalid_due_date_format_in_stored_data(self, temp_data_file):
        """Test: Ungültiges Datumsformat in gespeicherten Daten"""
        # Arrange
        invalid_data = {
            "tasks": [{
                "id": 1,
                "title": "Task",
                "completed": False,
                "category": "Keine",
                "due_date": "invalid-date"
            }],
            "archived_tasks": [],
            "categories": ["Arbeit"],
            "next_id": 2
        }
        with open(temp_data_file, "w") as f:
            json.dump(invalid_data, f)
        
        # Act
        repo = TaskRepository(temp_data_file)
        task = repo.get_task_by_id(1)
        
        # Assert
        assert task is not None
        assert task.is_urgent() is False  # Sollte False zurückgeben, nicht abstürzen
