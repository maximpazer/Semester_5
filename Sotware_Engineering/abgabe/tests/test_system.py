"""
Systemtests für TODO-App
Testet das komplette System: View + Controller + Repository
Simuliert echte Benutzer-Workflows ohne Browser
"""

import pytest
import sys
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock, patch
from io import StringIO

# Parent directory zum Pfad hinzufügen für Imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from model import Task, TaskRepository
from controller import ApplicationController, TaskController, CategoryController
from view import TaskView, CategoryView, SidebarView, ArchiveView, LayoutView


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_data_file(tmp_path):
    """Erstellt temporäre Datei für Systemtests"""
    return tmp_path / "system_test_data.json"


@pytest.fixture
def system_setup(temp_data_file):
    """
    Erstellt komplettes System mit allen Schichten
    Repository → Controller → Ready für View-Interaktion
    """
    # Repository mit temporärer Datei
    repository = TaskRepository(temp_data_file)
    
    # Controller initialisieren
    app_controller = ApplicationController()
    app_controller.repository = repository
    app_controller.task_controller = TaskController(repository)
    app_controller.category_controller = CategoryController(repository)
    
    return {
        'repository': repository,
        'app_controller': app_controller,
        'task_controller': app_controller.get_task_controller(),
        'category_controller': app_controller.get_category_controller(),
        'data_file': temp_data_file
    }


@pytest.fixture
def mock_streamlit():
    """Mockt Streamlit Session State für View-Tests"""
    mock_st = MagicMock()
    
    # Session State simulieren
    mock_st.session_state = {}
    
    # Streamlit UI-Komponenten mocken
    mock_st.title = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.write = MagicMock()
    mock_st.error = MagicMock()
    mock_st.success = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.info = MagicMock()
    mock_st.divider = MagicMock()
    mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
    mock_st.container = MagicMock(return_value=MagicMock())
    mock_st.expander = MagicMock()
    mock_st.form = MagicMock()
    mock_st.sidebar = MagicMock()
    
    return mock_st


# ============================================================================
# SYSTEMTEST 1: AUFGABE ANLEGEN
# ============================================================================

class TestCreateTaskSystemFlow:
    """Systemtest: Kompletter Workflow zum Anlegen einer Aufgabe"""
    
    def test_create_task_through_complete_system(self, system_setup):
        """
        Systemtest: Aufgabe anlegen → Speicherung und Abruf
        
        Testet den kompletten Datenfluss:
        User Input → Controller → Repository → Persistierung → Reload → Ausgabe
        """
        # Arrange
        task_controller = system_setup['task_controller']
        category_controller = system_setup['category_controller']
        repository = system_setup['repository']
        data_file = system_setup['data_file']
        
        # Initiale System-Prüfung
        assert len(task_controller.get_all_tasks()) == 0, "System sollte leer starten"
        assert data_file.exists() is False, "Datei sollte noch nicht existieren"
        
        # Act 1 - Benutzer erstellt neue Aufgabe über UI
        # (Simuliert: Benutzer füllt Formular aus und klickt "Hinzufügen")
        user_input = {
            'title': 'System Test Task',
            'category': 'Arbeit',
            'due_date': date.today() + timedelta(days=2)
        }
        
        # Controller verarbeitet Input
        create_result = task_controller.create_task(
            user_input['title'],
            user_input['category'],
            user_input['due_date']
        )
        
        # Assert 1 - Erstellung erfolgreich
        assert create_result is True, "Task-Erstellung sollte erfolgreich sein"
        
        # Assert 2 - Task im System vorhanden (In-Memory)
        all_tasks = task_controller.get_all_tasks()
        assert len(all_tasks) == 1, "Eine Task sollte im System sein"
        
        created_task = all_tasks[0]
        assert created_task.title == user_input['title'], "Titel sollte übereinstimmen"
        assert created_task.category == user_input['category'], "Kategorie sollte übereinstimmen"
        assert created_task.due_date is not None, "Datum sollte gesetzt sein"
        assert created_task.completed is False, "Task sollte nicht erledigt sein"
        assert created_task.id == 1, "Erste Task sollte ID 1 haben"
        
        # Assert 3 - Persistierung erfolgt (Datei existiert)
        assert data_file.exists(), "Datei sollte nach Speicherung existieren"
        
        # Assert 4 - System-Neustart simulieren (Repository neu laden)
        new_repository = TaskRepository(data_file)
        reloaded_tasks = new_repository.get_all_tasks()
        
        assert len(reloaded_tasks) == 1, "Task sollte nach Reload vorhanden sein"
        reloaded_task = reloaded_tasks[0]
        
        # Assert 5 - Alle Daten korrekt persistent gespeichert
        assert reloaded_task.title == user_input['title'], "Titel persistent"
        assert reloaded_task.category == user_input['category'], "Kategorie persistent"
        assert reloaded_task.id == 1, "ID persistent"
        assert reloaded_task.completed is False, "Status persistent"
        
        # Assert 6 - Statistiken korrekt
        new_controller = TaskController(new_repository)
        stats = new_controller.get_statistics()
        assert stats['total'] == 1, "Statistik: 1 Task"
        assert stats['open'] == 1, "Statistik: 1 offen"
        assert stats['done'] == 0, "Statistik: 0 erledigt"
        
        # Act 2 - Weitere Tasks erstellen (Mehrfach-Erstellung)
        task_controller.create_task("Task 2", "Privat", None)
        task_controller.create_task("Task 3", "Arbeit", date.today())
        
        # Assert 7 - Mehrere Tasks im System
        final_tasks = task_controller.get_all_tasks()
        assert len(final_tasks) == 3, "3 Tasks im System"
        
        # Assert 8 - Filter funktionieren nach Erstellung
        arbeit_tasks = task_controller.get_filtered_tasks(category="Arbeit")
        assert len(arbeit_tasks) == 2, "2 Tasks in Kategorie Arbeit"
        
        # Assert 9 - Dringliche Tasks werden erkannt
        urgent_tasks = task_controller.get_urgent_tasks()
        assert len(urgent_tasks) == 1, "1 dringliche Task (heute)"
        
        print("✅ Systemtest: Aufgabe anlegen → Speicherung und Abruf erfolgreich")


# ============================================================================
# SYSTEMTEST 2: AUFGABE ALS ERLEDIGT MARKIEREN
# ============================================================================

class TestMarkTaskCompletedSystemFlow:
    """Systemtest: Aufgabe als erledigt markieren"""
    
    def test_mark_task_completed_through_complete_system(self, system_setup):
        """
        Systemtest: Aufgabe als erledigt markieren → Status korrekt im System
        
        Testet den kompletten Workflow:
        Task erstellen → Als erledigt markieren → Archivierung → Status-Konsistenz
        """
        # Arrange
        task_controller = system_setup['task_controller']
        repository = system_setup['repository']
        data_file = system_setup['data_file']
        
        # System vorbereiten: 3 Tasks erstellen
        task_controller.create_task("Open Task 1", "Arbeit", date.today())
        task_controller.create_task("Open Task 2", "Privat", None)
        task_controller.create_task("Open Task 3", "Arbeit", date.today() + timedelta(days=1))
        
        initial_tasks = task_controller.get_all_tasks()
        assert len(initial_tasks) == 3, "3 Tasks initial"
        task_to_complete = initial_tasks[1]  # Task 2
        task_id = task_to_complete.id
        
        # Assert Pre-Condition
        assert task_to_complete.completed is False, "Task initial nicht erledigt"
        assert len(task_controller.get_archived_tasks()) == 0, "Archiv initial leer"
        
        # Act 1 - Benutzer markiert Task als erledigt (klickt Checkbox)
        toggle_result = task_controller.toggle_task_completion(task_id)
        
        # Assert 1 - Toggle erfolgreich
        assert toggle_result is True, "Toggle sollte erfolgreich sein"
        
        # Assert 2 - Task aus aktiven Tasks entfernt
        active_tasks_after = task_controller.get_all_tasks()
        assert len(active_tasks_after) == 2, "Nur 2 aktive Tasks nach Erledigung"
        active_ids = [t.id for t in active_tasks_after]
        assert task_id not in active_ids, "Erledigte Task nicht in aktiven Tasks"
        
        # Assert 3 - Task ins Archiv verschoben
        archived_tasks = task_controller.get_archived_tasks()
        assert len(archived_tasks) == 1, "1 Task im Archiv"
        archived_task = archived_tasks[0]
        assert archived_task.id == task_id, "Richtige Task archiviert"
        assert archived_task.completed is True, "Status auf erledigt gesetzt"
        assert archived_task.title == "Open Task 2", "Titel unverändert"
        
        # Assert 4 - Statistiken aktualisiert
        stats = task_controller.get_statistics()
        assert stats['total'] == 2, "2 aktive Tasks in Statistik"
        assert stats['open'] == 2, "2 offene Tasks"
        assert stats['done'] == 0, "0 erledigte in aktiven Tasks"
        assert stats['archived'] == 1, "1 archivierte Task"
        
        # Assert 5 - Persistierung korrekt
        assert data_file.exists(), "Datei sollte existieren"
        
        # System-Neustart simulieren
        new_repository = TaskRepository(data_file)
        new_controller = TaskController(new_repository)
        
        reloaded_active = new_controller.get_all_tasks()
        reloaded_archived = new_controller.get_archived_tasks()
        
        assert len(reloaded_active) == 2, "2 aktive nach Reload"
        assert len(reloaded_archived) == 1, "1 archivierte nach Reload"
        assert reloaded_archived[0].completed is True, "Status persistent"
        
        # Act 2 - Weitere Task erledigen
        remaining_task_id = active_tasks_after[0].id
        task_controller.toggle_task_completion(remaining_task_id)
        
        # Assert 6 - Zweite Archivierung funktioniert
        assert len(task_controller.get_all_tasks()) == 1, "Nur 1 aktive Task übrig"
        assert len(task_controller.get_archived_tasks()) == 2, "2 archivierte Tasks"
        
        # Act 3 - Task wiederherstellen (Benutzer klickt "Restore")
        restore_result = task_controller.restore_task(task_id)
        
        # Assert 7 - Wiederherstellung funktioniert
        assert restore_result is True, "Restore erfolgreich"
        assert len(task_controller.get_all_tasks()) == 2, "2 aktive nach Restore"
        assert len(task_controller.get_archived_tasks()) == 1, "1 archivierte nach Restore"
        
        restored_task = task_controller.get_task(task_id)
        assert restored_task is not None, "Task wieder abrufbar"
        assert restored_task.completed is False, "Status zurückgesetzt"
        
        print("✅ Systemtest: Aufgabe als erledigt markieren → Status korrekt")


# ============================================================================
# SYSTEMTEST 3: AUFGABE LÖSCHEN
# ============================================================================

class TestDeleteTaskSystemFlow:
    """Systemtest: Aufgabe löschen"""
    
    def test_delete_task_through_complete_system(self, system_setup):
        """
        Systemtest: Aufgabe löschen → System konsistent
        
        Testet den kompletten Workflow:
        Tasks erstellen → Task löschen → System-Konsistenz → Persistierung
        """
        # Arrange
        task_controller = system_setup['task_controller']
        repository = system_setup['repository']
        data_file = system_setup['data_file']
        
        # System vorbereiten: 4 Tasks erstellen
        task_controller.create_task("Task to keep 1", "Arbeit", None)
        task_controller.create_task("Task to delete", "Privat", date.today())
        task_controller.create_task("Task to keep 2", "Arbeit", None)
        task_controller.create_task("Task to archive then delete", "Keine", None)
        
        all_tasks = task_controller.get_all_tasks()
        assert len(all_tasks) == 4, "4 Tasks initial"
        
        task_to_delete = next(t for t in all_tasks if t.title == "Task to delete")
        delete_id = task_to_delete.id
        
        # Act 1 - Benutzer löscht Task (klickt Löschen-Button)
        delete_result = task_controller.delete_task(delete_id)
        
        # Assert 1 - Löschung erfolgreich
        assert delete_result is True, "Löschung sollte erfolgreich sein"
        
        # Assert 2 - Task aus System entfernt
        remaining_tasks = task_controller.get_all_tasks()
        assert len(remaining_tasks) == 3, "3 Tasks nach Löschung"
        
        remaining_ids = [t.id for t in remaining_tasks]
        assert delete_id not in remaining_ids, "Gelöschte Task nicht mehr vorhanden"
        
        remaining_titles = [t.title for t in remaining_tasks]
        assert "Task to delete" not in remaining_titles, "Gelöschter Titel nicht mehr vorhanden"
        assert "Task to keep 1" in remaining_titles, "Andere Tasks unberührt"
        assert "Task to keep 2" in remaining_titles, "Andere Tasks unberührt"
        
        # Assert 3 - Task kann nicht mehr abgerufen werden
        deleted_task = task_controller.get_task(delete_id)
        assert deleted_task is None, "Gelöschte Task gibt None zurück"
        
        # Assert 4 - Statistiken aktualisiert
        stats = task_controller.get_statistics()
        assert stats['total'] == 3, "Statistik: 3 Tasks"
        
        # Assert 5 - Persistierung korrekt
        new_repository = TaskRepository(data_file)
        new_controller = TaskController(new_repository)
        reloaded = new_controller.get_all_tasks()
        
        assert len(reloaded) == 3, "3 Tasks nach Reload"
        reloaded_ids = [t.id for t in reloaded]
        assert delete_id not in reloaded_ids, "Löschung persistent"
        
        # Act 2 - Task archivieren und dann löschen
        archive_task = next(t for t in remaining_tasks if t.title == "Task to archive then delete")
        archive_id = archive_task.id
        
        # Archivieren
        task_controller.toggle_task_completion(archive_id)
        assert len(task_controller.get_archived_tasks()) == 1, "Task archiviert"
        assert len(task_controller.get_all_tasks()) == 2, "Noch 2 aktive"
        
        # Aus Archiv löschen
        delete_archived_result = task_controller.delete_task(archive_id)
        
        # Assert 6 - Archivierte Task gelöscht
        assert delete_archived_result is True, "Löschen aus Archiv erfolgreich"
        assert len(task_controller.get_archived_tasks()) == 0, "Archiv leer"
        assert len(task_controller.get_all_tasks()) == 2, "Immer noch 2 aktive"
        
        # Assert 7 - Nicht-existierende Task löschen
        delete_nonexistent = task_controller.delete_task(999)
        assert delete_nonexistent is False, "Nicht-existierende Task nicht löschbar"
        
        # Assert 8 - System nach Löschversuchen konsistent
        final_tasks = task_controller.get_all_tasks()
        assert len(final_tasks) == 2, "System konsistent: 2 Tasks"
        assert all(t.title in ["Task to keep 1", "Task to keep 2"] for t in final_tasks), \
            "Nur beabsichtigte Tasks übrig"
        
        # Assert 9 - Filter funktionieren nach Löschungen
        arbeit_filter = task_controller.get_filtered_tasks(category="Arbeit")
        assert len(arbeit_filter) == 2, "Filter funktionieren noch"
        
        print("✅ Systemtest: Aufgabe löschen → System konsistent")


# ============================================================================
# SYSTEMTEST 4: FEHLERFÄLLE
# ============================================================================

class TestErrorHandlingSystemFlow:
    """Systemtest: Fehlerbehandlung im kompletten System"""
    
    def test_error_cases_through_complete_system(self, system_setup):
        """
        Systemtest: Fehlerfälle → Kontrollierte Fehlermeldung
        
        Testet Fehlerbehandlung auf allen Ebenen:
        - Ungültige Eingaben
        - Nicht-existierende Ressourcen
        - System bleibt konsistent
        """
        # Arrange
        task_controller = system_setup['task_controller']
        category_controller = system_setup['category_controller']
        repository = system_setup['repository']
        
        # Fehlerfall 1: Leere Task erstellen
        # ----------------------------------------
        # Act
        empty_result = task_controller.create_task("", "Arbeit", None)
        
        # Assert - Kontrollierter Fehler
        assert empty_result is False, "Leere Task abgelehnt"
        assert len(task_controller.get_all_tasks()) == 0, "Keine Task erstellt"
        
        # Fehlerfall 2: Task mit nur Whitespace
        # ----------------------------------------
        whitespace_result = task_controller.create_task("   ", "Privat", None)
        
        assert whitespace_result is False, "Whitespace-Task abgelehnt"
        assert len(task_controller.get_all_tasks()) == 0, "Immer noch keine Task"
        
        # Fehlerfall 3: Nicht-existierende Task bearbeiten
        # ----------------------------------------
        update_result = task_controller.update_task(999, "New Title", "Arbeit", None)
        
        assert update_result is False, "Update nicht-existierender Task abgelehnt"
        
        # Fehlerfall 4: Nicht-existierende Task als erledigt markieren
        # ----------------------------------------
        toggle_result = task_controller.toggle_task_completion(999)
        
        assert toggle_result is False, "Toggle nicht-existierender Task abgelehnt"
        
        # Fehlerfall 5: Nicht-existierende Task löschen
        # ----------------------------------------
        delete_result = task_controller.delete_task(999)
        
        assert delete_result is False, "Löschen nicht-existierender Task abgelehnt"
        
        # Fehlerfall 6: Nicht-existierende Task wiederherstellen
        # ----------------------------------------
        restore_result = task_controller.restore_task(999)
        
        assert restore_result is False, "Restore nicht-existierender Task abgelehnt"
        
        # System-Konsistenz nach Fehlern prüfen
        # ----------------------------------------
        assert len(task_controller.get_all_tasks()) == 0, "System leer nach Fehlern"
        assert repository.data["next_id"] == 1, "next_id nicht durch Fehler erhöht"
        
        # Gültige Task erstellen nach Fehlern
        # ----------------------------------------
        valid_result = task_controller.create_task("Valid Task", "Arbeit", None)
        
        assert valid_result is True, "Gültige Task funktioniert nach Fehlern"
        assert len(task_controller.get_all_tasks()) == 1, "Task erfolgreich erstellt"
        assert task_controller.get_all_tasks()[0].id == 1, "ID korrekt nach Fehlern"
        
        # Fehlerfall 7: Leere Kategorie erstellen
        # ----------------------------------------
        empty_cat_result = category_controller.create_category("")
        
        assert empty_cat_result is False, "Leere Kategorie abgelehnt"
        
        # Fehlerfall 8: Kategorie-Maximum überschreiten
        # ----------------------------------------
        # 6 Kategorien erstellen (2 existieren bereits: Arbeit, Privat), Maximum ist 8
        category_controller.create_category("Cat1")
        category_controller.create_category("Cat2")
        category_controller.create_category("Cat3")
        category_controller.create_category("Cat4")
        category_controller.create_category("Cat5")
        category_controller.create_category("Cat6")
        
        assert len(category_controller.get_all_categories()) == 8, "8 Kategorien (Maximum)"
        
        # Versuch 9. Kategorie
        exceed_result = category_controller.create_category("Cat9")
        
        assert exceed_result is False, "9. Kategorie abgelehnt"
        assert len(category_controller.get_all_categories()) == 8, "Immer noch 8"
        
        # Fehlerfall 9: Doppelte Kategorie erstellen
        # ----------------------------------------
        duplicate_result = category_controller.create_category("Arbeit")
        
        assert duplicate_result is False, "Doppelte Kategorie abgelehnt"
        
        # Fehlerfall 10: Nicht-existierende Kategorie löschen (gibt True zurück, da keine Exception)
        # ----------------------------------------
        delete_cat_result = category_controller.delete_category("NonExistent")
        
        assert delete_cat_result is True, "Löschen nicht-existierender Kategorie gibt True zurück (keine Exception)"
        
        # Fehlerfall 11: Task mit leerem Titel aktualisieren
        # ----------------------------------------
        task_id = task_controller.get_all_tasks()[0].id
        empty_update = task_controller.update_task(task_id, "", "Arbeit", None)
        
        assert empty_update is False, "Update mit leerem Titel abgelehnt"
        
        # Original-Task unverändert
        original = task_controller.get_task(task_id)
        assert original.title == "Valid Task", "Titel unverändert nach Fehlversuch"
        
        # Final: System konsistent nach allen Fehlern
        # ----------------------------------------
        final_tasks = task_controller.get_all_tasks()
        assert len(final_tasks) == 1, "System konsistent: 1 Task"
        assert final_tasks[0].title == "Valid Task", "Richtige Task vorhanden"
        
        final_cats = category_controller.get_all_categories()
        assert len(final_cats) == 8, "8 Kategorien final (Maximum)"
        
        # Statistiken korrekt nach Fehlern
        stats = task_controller.get_statistics()
        assert stats['total'] == 1, "Statistik korrekt"
        assert stats['open'] == 1, "1 offene Task"
        
        print("✅ Systemtest: Fehlerfälle → Kontrollierte Fehlermeldung erfolgreich")


# ============================================================================
# SYSTEMTEST 5: KOMPLETTER END-TO-END WORKFLOW
# ============================================================================

class TestCompleteEndToEndSystemFlow:
    """Systemtest: Kompletter Benutzer-Workflow"""
    
    def test_complete_user_workflow_through_system(self, system_setup):
        """
        Systemtest: Kompletter End-to-End Workflow
        
        Simuliert einen realistischen Benutzer-Workflow:
        1. System starten
        2. Kategorien verwalten
        3. Mehrere Tasks erstellen
        4. Tasks bearbeiten
        5. Tasks filtern
        6. Tasks als erledigt markieren
        7. Archiv verwalten
        8. Tasks löschen
        9. System neu starten und Daten prüfen
        """
        # Arrange
        task_controller = system_setup['task_controller']
        category_controller = system_setup['category_controller']
        data_file = system_setup['data_file']
        
        # Phase 1: Kategorien vorbereiten
        # ================================
        category_controller.create_category("Projekt X")
        category_controller.create_category("Haushalt")
        
        categories = category_controller.get_all_categories()
        assert len(categories) == 4, "4 Kategorien (2 default + 2 neue)"
        
        # Phase 2: Tasks erstellen
        # ========================
        tasks_data = [
            ("Design Review planen", "Projekt X", date.today()),
            ("Code Review durchführen", "Arbeit", date.today() + timedelta(days=1)),
            ("Einkaufen gehen", "Haushalt", None),
            ("Dokumentation schreiben", "Projekt X", date.today() + timedelta(days=3)),
            ("Team Meeting", "Arbeit", date.today()),
        ]
        
        for title, category, due_date in tasks_data:
            result = task_controller.create_task(title, category, due_date)
            assert result is True, f"Task '{title}' sollte erstellt werden"
        
        all_tasks = task_controller.get_all_tasks()
        assert len(all_tasks) == 5, "5 Tasks erstellt"
        
        # Phase 3: Tasks bearbeiten
        # =========================
        task_to_edit = next(t for t in all_tasks if t.title == "Einkaufen gehen")
        edit_result = task_controller.update_task(
            task_to_edit.id,
            "Wocheneinkauf erledigen",
            "Haushalt",
            date.today() + timedelta(days=5)  # Nicht dringliches Datum
        )
        assert edit_result is True, "Task bearbeitet"
        
        edited = task_controller.get_task(task_to_edit.id)
        assert edited.title == "Wocheneinkauf erledigen", "Titel geändert"
        
        # Phase 4: Tasks filtern
        # ======================
        projekt_tasks = task_controller.get_filtered_tasks(category="Projekt X")
        assert len(projekt_tasks) == 2, "2 Tasks in Projekt X"
        
        urgent = task_controller.get_urgent_tasks()
        assert len(urgent) == 3, "3 dringliche Tasks (heute + morgen)"
        
        # Phase 5: Tasks als erledigt markieren
        # ======================================
        completed_titles = ["Design Review planen", "Team Meeting"]
        for title in completed_titles:
            task = next(t for t in task_controller.get_all_tasks() if t.title == title)
            result = task_controller.toggle_task_completion(task.id)
            assert result is True, f"'{title}' als erledigt markiert"
        
        active = task_controller.get_all_tasks()
        archived = task_controller.get_archived_tasks()
        assert len(active) == 3, "3 aktive Tasks"
        assert len(archived) == 2, "2 archivierte Tasks"
        
        # Phase 6: Archiv verwalten
        # =========================
        # Eine Task wiederherstellen - die "Design Review planen" Task
        task_to_restore = next(t for t in archived if t.title == "Design Review planen")
        restore_result = task_controller.restore_task(task_to_restore.id)
        assert restore_result is True, "Task wiederhergestellt"
        
        assert len(task_controller.get_all_tasks()) == 4, "4 aktive nach Restore"
        assert len(task_controller.get_archived_tasks()) == 1, "1 im Archiv"
        
        # Phase 7: Tasks löschen
        # ======================
        task_to_delete = next(
            t for t in task_controller.get_all_tasks() 
            if t.title == "Wocheneinkauf erledigen"
        )
        delete_result = task_controller.delete_task(task_to_delete.id)
        assert delete_result is True, "Task gelöscht"
        
        assert len(task_controller.get_all_tasks()) == 3, "3 aktive nach Löschung"
        
        # Phase 8: System-Neustart simulieren
        # ====================================
        # Alle Daten sollten persistent sein
        new_repository = TaskRepository(data_file)
        new_task_controller = TaskController(new_repository)
        new_category_controller = CategoryController(new_repository)
        
        # Daten nach Neustart prüfen
        reloaded_tasks = new_task_controller.get_all_tasks()
        reloaded_archived = new_task_controller.get_archived_tasks()
        reloaded_categories = new_category_controller.get_all_categories()
        
        assert len(reloaded_tasks) == 3, "3 aktive Tasks nach Neustart"
        assert len(reloaded_archived) == 1, "1 archivierte Task nach Neustart"
        assert len(reloaded_categories) == 4, "4 Kategorien nach Neustart"
        
        # Phase 9: Statistiken final prüfen
        # ==================================
        final_stats = new_task_controller.get_statistics()
        assert final_stats['total'] == 3, "3 aktive Tasks"
        assert final_stats['archived'] == 1, "1 archivierte"
        
        # Filter funktionieren nach Neustart
        projekt_after_restart = new_task_controller.get_filtered_tasks(category="Projekt X")
        # Projekt X Tasks: "Design Review planen" (wiederhergestellt) + "Dokumentation schreiben"
        assert len(projekt_after_restart) == 2, "2 Projekt X Tasks nach Restart"
        
        print("✅ Systemtest: Kompletter End-to-End Workflow erfolgreich")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
