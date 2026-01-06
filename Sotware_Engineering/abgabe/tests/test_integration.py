"""
Integrationstests für TODO-App
Testet das Zusammenspiel zwischen Controller und Repository
"""

import pytest
import sys
from pathlib import Path
from datetime import date, timedelta

# Parent directory zum Pfad hinzufügen für Imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from model import Task, Category, TaskRepository
from controller import TaskController, CategoryController, ApplicationController


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_data_file(tmp_path):
    """Erstellt temporäre Datei für Integrationstests"""
    return tmp_path / "integration_test_data.json"


@pytest.fixture
def app_controller(temp_data_file):
    """Erstellt ApplicationController mit temporärem Repository"""
    # Repository mit temporärer Datei initialisieren
    repo = TaskRepository(temp_data_file)
    
    # ApplicationController manuell erstellen mit unserem Repository
    controller = ApplicationController()
    controller.repository = repo
    controller.task_controller = TaskController(repo)
    controller.category_controller = CategoryController(repo)
    
    return controller


# ============================================================================
# INTEGRATIONSTESTS
# ============================================================================

class TestTaskCreationIntegration:
    """Integrationstest: Mehrere Aufgaben erstellen und Repository-Konsistenz prüfen"""
    
    def test_create_multiple_tasks_maintains_repository_consistency(self, app_controller):
        """
        Integration Test: Mehrere Aufgaben erstellen
        
        Testet das Zusammenspiel zwischen TaskController und Repository:
        - Erstellen mehrerer Tasks über Controller
        - Sicherstellen dass Repository konsistent bleibt
        - IDs korrekt inkrementiert werden
        - Alle Tasks persistent gespeichert werden
        - Filter korrekt funktionieren
        """
        # Arrange
        task_controller = app_controller.get_task_controller()
        category_controller = app_controller.get_category_controller()
        
        # Neue Kategorie erstellen
        category_controller.create_category("Projekt")
        
        tasks_to_create = [
            {"title": "Task 1", "category": "Arbeit", "due_date": date.today()},
            {"title": "Task 2", "category": "Privat", "due_date": date.today() + timedelta(days=1)},
            {"title": "Task 3", "category": "Projekt", "due_date": None},
            {"title": "Task 4", "category": "Keine", "due_date": date.today() + timedelta(days=5)},
            {"title": "Task 5", "category": "Arbeit", "due_date": None},
        ]
        
        # Act - Mehrere Tasks über Controller erstellen
        created_ids = []
        for task_data in tasks_to_create:
            result = task_controller.create_task(
                task_data["title"],
                task_data["category"],
                task_data["due_date"]
            )
            assert result is True, f"Task '{task_data['title']}' konnte nicht erstellt werden"
        
        # Assert - Repository-Konsistenz prüfen
        
        # 1. Alle Tasks im Repository vorhanden
        all_tasks = task_controller.get_all_tasks()
        assert len(all_tasks) == 5, "Repository sollte 5 Tasks enthalten"
        
        # 2. IDs sind eindeutig und aufsteigend
        task_ids = [task.id for task in all_tasks]
        assert task_ids == [1, 2, 3, 4, 5], "IDs sollten sequentiell sein"
        assert len(set(task_ids)) == 5, "Alle IDs sollten eindeutig sein"
        
        # 3. Titel korrekt gespeichert
        task_titles = [task.title for task in all_tasks]
        expected_titles = [t["title"] for t in tasks_to_create]
        assert task_titles == expected_titles, "Titel sollten korrekt gespeichert sein"
        
        # 4. Kategorien korrekt zugeordnet
        for i, task in enumerate(all_tasks):
            assert task.category == tasks_to_create[i]["category"], \
                f"Kategorie von Task {i+1} sollte '{tasks_to_create[i]['category']}' sein"
        
        # 5. Filter funktionieren korrekt
        arbeit_tasks = task_controller.get_filtered_tasks(category="Arbeit")
        assert len(arbeit_tasks) == 2, "Filter 'Arbeit' sollte 2 Tasks finden"
        
        # 6. Dringliche Tasks werden korrekt identifiziert
        urgent_tasks = task_controller.get_urgent_tasks()
        assert len(urgent_tasks) == 2, "2 Tasks sollten dringlich sein (heute + morgen)"
        
        # 7. Persistierung funktioniert (Repository speichert auf Disk)
        repository = task_controller.repository
        assert repository.data_file.exists(), "Datei sollte existieren"
        
        # 8. Daten können neu geladen werden
        new_repo = TaskRepository(repository.data_file)
        reloaded_tasks = new_repo.get_all_tasks()
        assert len(reloaded_tasks) == 5, "Nach Reload sollten 5 Tasks vorhanden sein"
        
        # 9. Statistiken sind korrekt
        stats = task_controller.get_statistics()
        assert stats["total"] == 5, "Gesamt sollte 5 sein"
        assert stats["open"] == 5, "Alle sollten offen sein"
        assert stats["done"] == 0, "Keine sollte erledigt sein"
        assert stats["archived"] == 0, "Keine sollte archiviert sein"
        
        print("✅ Repository-Konsistenz bestätigt: 5 Tasks erfolgreich erstellt und persistent gespeichert")


class TestTaskUpdateIntegration:
    """Integrationstest: Task aktualisieren und Repository-Konsistenz prüfen"""
    
    def test_update_task_status_persists_correctly_in_repository(self, app_controller):
        """
        Integration Test: Task-Status aktualisieren
        
        Testet das Zusammenspiel zwischen Controller und Repository:
        - Task erstellen
        - Status auf erledigt ändern (toggle completion)
        - Prüfen dass Änderung im Repository persistiert wird
        - Prüfen dass Task ins Archiv verschoben wird
        - Prüfen dass Task wiederhergestellt werden kann
        """
        # Arrange
        task_controller = app_controller.get_task_controller()
        
        # Task erstellen
        task_controller.create_task(
            title="Task zum Status ändern",
            category="Arbeit",
            due_date=date.today()
        )
        
        # Task-ID ermitteln
        all_tasks = task_controller.get_all_tasks()
        assert len(all_tasks) == 1, "Eine Task sollte erstellt worden sein"
        task_id = all_tasks[0].id
        initial_task = all_tasks[0]
        
        # Assert - Initiale Prüfungen
        assert initial_task.completed is False, "Task sollte initial nicht erledigt sein"
        assert initial_task.title == "Task zum Status ändern"
        assert initial_task.category == "Arbeit"
        
        # Act 1 - Status auf "erledigt" ändern
        result = task_controller.toggle_task_completion(task_id)
        assert result is True, "Toggle sollte erfolgreich sein"
        
        # Assert 1 - Task ist ins Archiv verschoben
        active_tasks = task_controller.get_all_tasks()
        assert len(active_tasks) == 0, "Keine aktiven Tasks nach Erledigung"
        
        archived_tasks = task_controller.get_archived_tasks()
        assert len(archived_tasks) == 1, "Eine archivierte Task"
        archived_task = archived_tasks[0]
        assert archived_task.id == task_id, "Richtige Task archiviert"
        assert archived_task.completed is True, "Task ist als erledigt markiert"
        assert archived_task.title == "Task zum Status ändern", "Titel unverändert"
        assert archived_task.category == "Arbeit", "Kategorie unverändert"
        
        # Assert 2 - Persistierung prüfen (Repository neu laden)
        repository = task_controller.repository
        new_repo = TaskRepository(repository.data_file)
        reloaded_archived = new_repo.get_archived_tasks()
        assert len(reloaded_archived) == 1, "Archivierung persistiert"
        assert reloaded_archived[0].completed is True, "Status persistiert"
        
        # Act 2 - Task wiederherstellen
        result = task_controller.restore_task(task_id)
        assert result is True, "Restore sollte erfolgreich sein"
        
        # Assert 3 - Task wieder aktiv
        active_tasks_after_restore = task_controller.get_all_tasks()
        assert len(active_tasks_after_restore) == 1, "Task wieder aktiv"
        restored_task = active_tasks_after_restore[0]
        assert restored_task.id == task_id, "Richtige Task wiederhergestellt"
        assert restored_task.completed is False, "Status zurückgesetzt"
        
        archived_after_restore = task_controller.get_archived_tasks()
        assert len(archived_after_restore) == 0, "Archiv leer nach Restore"
        
        # Assert 4 - Wiederherstellung persistiert
        final_repo = TaskRepository(repository.data_file)
        final_active = final_repo.get_all_tasks()
        assert len(final_active) == 1, "Wiederherstellung persistiert"
        assert final_active[0].completed is False, "Status-Reset persistiert"
        
        # Act 3 - Task-Details aktualisieren (nicht nur Status)
        update_result = task_controller.update_task(
            task_id=task_id,
            title="Geänderter Titel",
            category="Privat",
            due_date=date.today() + timedelta(days=3)
        )
        assert update_result is True, "Update sollte erfolgreich sein"
        
        # Assert 5 - Änderungen im Repository
        updated_task = task_controller.get_task(task_id)
        assert updated_task.title == "Geänderter Titel", "Titel geändert"
        assert updated_task.category == "Privat", "Kategorie geändert"
        assert updated_task.due_date is not None, "Datum gesetzt"
        
        # Assert 6 - Detail-Updates persistiert
        detail_repo = TaskRepository(repository.data_file)
        detail_task = detail_repo.get_task_by_id(task_id)
        assert detail_task.title == "Geänderter Titel", "Titel-Update persistiert"
        assert detail_task.category == "Privat", "Kategorie-Update persistiert"
        
        print("✅ Task-Status-Updates funktionieren korrekt und werden persistent gespeichert")


class TestInvalidTaskCreationIntegration:
    """Integrationstest: Fehlerbehandlung bei ungültigen Tasks"""
    
    def test_empty_task_creation_raises_controlled_error(self, app_controller):
        """
        Integration Test: Leere Aufgabe erstellen
        
        Testet Fehlerbehandlung im Zusammenspiel Controller-Repository:
        - Versuch eine Task mit leerem Titel zu erstellen
        - Controller sollte False zurückgeben (kein Exception)
        - Repository sollte konsistent bleiben
        - Keine Task sollte gespeichert werden
        """
        # Arrange
        task_controller = app_controller.get_task_controller()
        
        # Initiale Task-Anzahl prüfen
        initial_tasks = task_controller.get_all_tasks()
        initial_count = len(initial_tasks)
        assert initial_count == 0, "Repository sollte leer starten"
        
        # Act 1 - Versuch leere Task zu erstellen
        result_empty = task_controller.create_task(title="", category="Arbeit")
        
        # Assert 1 - Kontrollierter Fehler (False, kein Exception)
        assert result_empty is False, "Leerer Titel sollte abgelehnt werden"
        
        # Assert 2 - Repository unverändert
        tasks_after_empty = task_controller.get_all_tasks()
        assert len(tasks_after_empty) == initial_count, "Keine neue Task im Repository"
        
        # Act 2 - Versuch Task mit nur Whitespace zu erstellen
        result_whitespace = task_controller.create_task(title="   ", category="Privat")
        
        # Assert 3 - Auch Whitespace wird abgelehnt
        assert result_whitespace is False, "Whitespace-Titel sollte abgelehnt werden"
        
        tasks_after_whitespace = task_controller.get_all_tasks()
        assert len(tasks_after_whitespace) == initial_count, "Immer noch keine neue Task"
        
        # Act 3 - Gültige Task erstellen als Vergleich
        result_valid = task_controller.create_task(title="Gültige Task", category="Arbeit")
        
        # Assert 4 - Gültige Task wird akzeptiert
        assert result_valid is True, "Gültige Task sollte erstellt werden"
        
        tasks_after_valid = task_controller.get_all_tasks()
        assert len(tasks_after_valid) == initial_count + 1, "Eine Task im Repository"
        
        # Assert 5 - Repository-Integrität nach Fehlversuchen
        valid_task = tasks_after_valid[0]
        assert valid_task.id == 1, "ID sollte 1 sein (keine IDs durch Fehlversuche verschwendet)"
        assert valid_task.title == "Gültige Task", "Titel korrekt"
        
        # Act 4 - Weiterer Fehlversuch nach erfolgreicher Erstellung
        result_empty_after = task_controller.create_task(title="", category="Test")
        
        # Assert 6 - Fehlerbehandlung funktioniert weiterhin
        assert result_empty_after is False, "Leerer Titel wird weiterhin abgelehnt"
        
        final_tasks = task_controller.get_all_tasks()
        assert len(final_tasks) == 1, "Immer noch nur eine Task"
        
        # Assert 7 - Persistierung korrekt (nur gültige Task gespeichert)
        repository = task_controller.repository
        new_repo = TaskRepository(repository.data_file)
        persisted_tasks = new_repo.get_all_tasks()
        assert len(persisted_tasks) == 1, "Nur gültige Task persistiert"
        assert persisted_tasks[0].title == "Gültige Task", "Richtige Task persistiert"
        
        # Assert 8 - next_id korrekt (nicht durch Fehlversuche erhöht)
        assert new_repo.data["next_id"] == 2, "next_id sollte 2 sein (nicht durch Fehler erhöht)"
        
        print("✅ Fehlerbehandlung funktioniert korrekt: Ungültige Tasks werden kontrolliert abgelehnt")


class TestTaskDeletionIntegration:
    """Integrationstest: Task löschen und Repository-Konsistenz prüfen"""
    
    def test_delete_task_removes_from_repository_completely(self, app_controller):
        """
        Integration Test: Task löschen
        
        Testet das Zusammenspiel beim Löschen:
        - Mehrere Tasks erstellen
        - Einzelne Task löschen
        - Prüfen dass Task aus Repository verschwindet
        - Prüfen dass andere Tasks unberührt bleiben
        - Prüfen dass Löschung persistiert wird
        """
        # Arrange
        task_controller = app_controller.get_task_controller()
        
        # Mehrere Tasks erstellen
        task_controller.create_task("Task 1", "Arbeit", date.today())
        task_controller.create_task("Task 2", "Privat", None)
        task_controller.create_task("Task 3", "Arbeit", date.today() + timedelta(days=1))
        task_controller.create_task("Task 4", "Keine", None)
        
        initial_tasks = task_controller.get_all_tasks()
        assert len(initial_tasks) == 4, "4 Tasks sollten erstellt sein"
        
        # Task 2 (ID=2) zum Löschen auswählen
        task_to_delete = next(t for t in initial_tasks if t.title == "Task 2")
        task_id_to_delete = task_to_delete.id
        assert task_id_to_delete == 2, "Task 2 sollte ID 2 haben"
        
        # Act - Task löschen
        delete_result = task_controller.delete_task(task_id_to_delete)
        
        # Assert 1 - Löschung erfolgreich
        assert delete_result is True, "Löschung sollte erfolgreich sein"
        
        # Assert 2 - Task aus aktivem Repository entfernt
        remaining_tasks = task_controller.get_all_tasks()
        assert len(remaining_tasks) == 3, "3 Tasks sollten übrig bleiben"
        
        remaining_ids = [t.id for t in remaining_tasks]
        assert task_id_to_delete not in remaining_ids, "Gelöschte Task sollte nicht mehr existieren"
        
        remaining_titles = [t.title for t in remaining_tasks]
        assert "Task 2" not in remaining_titles, "Task 2 sollte nicht mehr vorhanden sein"
        assert "Task 1" in remaining_titles, "Task 1 sollte noch vorhanden sein"
        assert "Task 3" in remaining_titles, "Task 3 sollte noch vorhanden sein"
        assert "Task 4" in remaining_titles, "Task 4 sollte noch vorhanden sein"
        
        # Assert 3 - Task kann nicht mehr abgerufen werden
        deleted_task = task_controller.get_task(task_id_to_delete)
        assert deleted_task is None, "Gelöschte Task sollte None zurückgeben"
        
        # Assert 4 - Andere Tasks unverändert
        task1 = task_controller.get_task(1)
        assert task1 is not None, "Task 1 sollte existieren"
        assert task1.title == "Task 1", "Task 1 unverändert"
        assert task1.category == "Arbeit", "Task 1 Kategorie unverändert"
        
        task3 = task_controller.get_task(3)
        assert task3 is not None, "Task 3 sollte existieren"
        assert task3.title == "Task 3", "Task 3 unverändert"
        
        # Assert 5 - Löschung persistiert
        repository = task_controller.repository
        new_repo = TaskRepository(repository.data_file)
        persisted_tasks = new_repo.get_all_tasks()
        assert len(persisted_tasks) == 3, "3 Tasks nach Reload"
        
        persisted_ids = [t.id for t in persisted_tasks]
        assert task_id_to_delete not in persisted_ids, "Gelöschte Task nicht in Datei"
        
        # Assert 6 - Statistiken aktualisiert
        stats = task_controller.get_statistics()
        assert stats["total"] == 3, "Statistik: 3 Tasks gesamt"
        
        # Act 2 - Weitere Task löschen
        delete_result2 = task_controller.delete_task(1)
        assert delete_result2 is True, "Zweite Löschung erfolgreich"
        
        # Assert 7 - Nur noch 2 Tasks übrig
        final_tasks = task_controller.get_all_tasks()
        assert len(final_tasks) == 2, "2 Tasks übrig"
        assert all(t.id in [3, 4] for t in final_tasks), "Nur Task 3 und 4 übrig"
        
        # Act 3 - Versuch nicht-existierende Task zu löschen
        delete_nonexistent = task_controller.delete_task(999)
        
        # Assert 8 - Löschen nicht-existierender Task gibt False zurück
        assert delete_nonexistent is False, "Nicht-existierende Task kann nicht gelöscht werden"
        
        # Assert 9 - Repository unverändert nach Fehlversuch
        tasks_after_failed = task_controller.get_all_tasks()
        assert len(tasks_after_failed) == 2, "Immer noch 2 Tasks nach Fehlversuch"
        
        # Act 4 - Erledigte Task löschen (aus Archiv)
        task_controller.toggle_task_completion(3)  # Task 3 erledigen (archivieren)
        archived = task_controller.get_archived_tasks()
        assert len(archived) == 1, "Eine Task archiviert"
        
        delete_archived = task_controller.delete_task(3)
        assert delete_archived is True, "Archivierte Task kann gelöscht werden"
        
        # Assert 10 - Task vollständig entfernt (nicht in aktiv oder archiv)
        final_active = task_controller.get_all_tasks()
        final_archived = task_controller.get_archived_tasks()
        assert len(final_active) == 1, "Nur 1 aktive Task übrig"
        assert len(final_archived) == 0, "Keine archivierte Task mehr"
        assert final_active[0].id == 4, "Nur Task 4 übrig"
        
        print("✅ Task-Löschung funktioniert korrekt und wird persistent gespeichert")


# ============================================================================
# ZUSÄTZLICHER INTEGRATIONSTEST: GESAMTWORKFLOW
# ============================================================================

class TestCompleteWorkflowIntegration:
    """Integrationstest: Kompletter Workflow von Erstellung bis Löschung"""
    
    def test_complete_task_lifecycle(self, app_controller):
        """
        Integration Test: Kompletter Task-Lebenszyklus
        
        Testet den vollständigen Workflow:
        1. Kategorien erstellen
        2. Tasks erstellen
        3. Tasks bearbeiten
        4. Tasks als erledigt markieren (archivieren)
        5. Tasks wiederherstellen
        6. Tasks löschen
        7. Repository-Konsistenz durchgehend prüfen
        """
        # Arrange
        task_controller = app_controller.get_task_controller()
        category_controller = app_controller.get_category_controller()
        
        # Phase 1: Kategorien vorbereiten
        category_controller.create_category("Projekt A")
        categories = category_controller.get_all_categories()
        assert "Projekt A" in categories
        
        # Phase 2: Tasks erstellen
        task_controller.create_task("Design Review", "Projekt A", date.today())
        task_controller.create_task("Code Review", "Arbeit", date.today() + timedelta(days=1))
        task_controller.create_task("Meeting", "Projekt A", None)
        
        assert len(task_controller.get_all_tasks()) == 3
        
        # Phase 3: Task bearbeiten
        task_controller.update_task(1, "Design Review v2", "Projekt A", date.today())
        updated = task_controller.get_task(1)
        assert updated.title == "Design Review v2"
        
        # Phase 4: Task erledigen
        task_controller.toggle_task_completion(2)
        assert len(task_controller.get_all_tasks()) == 2
        assert len(task_controller.get_archived_tasks()) == 1
        
        # Phase 5: Wiederherstellen
        task_controller.restore_task(2)
        assert len(task_controller.get_all_tasks()) == 3
        assert len(task_controller.get_archived_tasks()) == 0
        
        # Phase 6: Löschen
        task_controller.delete_task(3)
        assert len(task_controller.get_all_tasks()) == 2
        
        # Phase 7: Persistierung prüfen
        repository = task_controller.repository
        new_repo = TaskRepository(repository.data_file)
        assert len(new_repo.get_all_tasks()) == 2
        
        print("✅ Kompletter Task-Lebenszyklus erfolgreich getestet")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
