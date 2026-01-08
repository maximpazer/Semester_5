"""
Unit Tests für TODO-App | pytest | AAA-Muster | Ziel: >=80% Coverage

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
        assert ctrl.create_task("Einkaufen") is True
        assert len(ctrl.get_all_tasks()) == 1
    
    def test_entfernen(self, ctrl):
        """2. Entfernen eines Items"""
        ctrl.create_task("Löschen")
        assert ctrl.delete_task(1) is True
        assert len(ctrl.get_all_tasks()) == 0
    
    def test_erledigt_markieren(self, ctrl):
        """3a. Markieren als erledigt"""
        ctrl.create_task("Aufgabe")
        assert ctrl.toggle_task_completion(1) is True
        assert ctrl.get_archived_tasks()[0].completed is True
    
    def test_nicht_erledigt_markieren(self, ctrl):
        """3b. Markieren als nicht erledigt"""
        ctrl.create_task("Aufgabe")
        ctrl.toggle_task_completion(1)
        assert ctrl.restore_task(1) is True
        assert ctrl.get_task(1).completed is False
    
    def test_bearbeiten(self, ctrl):
        """4. Bearbeiten eines Items"""
        ctrl.create_task("Alt")
        assert ctrl.update_task(1, "Neu", "Arbeit") is True
        assert ctrl.get_task(1).title == "Neu"


# zusätzliche Fehlerfälle

class TestFehlerfaelle:
    
    def test_leerer_titel(self, ctrl):
        assert ctrl.create_task("") is False
        assert ctrl.create_task("   ") is False
    
    def test_nicht_vorhanden(self, ctrl):
        assert ctrl.delete_task(999) is False
    
    def test_doppelte_titel(self, ctrl):
        ctrl.create_task("X")
        ctrl.create_task("X")
        assert len(ctrl.get_all_tasks()) == 2


# Coverage Test

class TestCoverage:
    
    def test_task_basics(self):
        t = Task(1, "Test", completed=True, category="A", due_date=date.today().isoformat())
        assert t.validate() is True
        assert Task(1, "").validate() is False
        assert t.is_urgent() is True
        d = t.to_dict()
        assert Task.from_dict(d).title == "Test"
    
    def test_category(self):
        assert Category("Valid").validate() is True
        assert Category("").validate() is False
    
    def test_repository_ops(self, repo):
        repo.add_task(Task(0, "A", category="Arbeit"))
        repo.add_task(Task(0, "B", category="Privat"))
        assert repo.get_task_by_id(1) is not None
        assert repo.get_task_by_id(999) is None
        assert len(repo.filter_tasks(category="Arbeit")) == 1
        assert len(repo.filter_tasks(status="Offen")) == 2
        repo.update_task(Task(1, "Updated"))
        assert repo.get_task_by_id(1).title == "Updated"
    
    def test_kategorie_ops(self, repo):
        repo.add_category(Category("Sport"))
        names = [c["name"] for c in repo.get_categories()]
        assert "Sport" in names
        repo.delete_category("Sport")
    
    def test_dringende_tasks(self, repo):
        repo.add_task(Task(0, "Dringend", due_date=date.today().isoformat()))
        assert len(repo.get_urgent_tasks()) == 1
    
    def test_persistenz(self, tmp_path):
        f = tmp_path / "d.json"
        r1 = TaskRepository(f)
        r1.add_task(Task(0, "P"))
        r1.save()
        r2 = TaskRepository(f)
        assert len(r2.get_all_tasks()) == 1
