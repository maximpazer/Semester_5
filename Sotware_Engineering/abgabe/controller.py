# CONTROLLER - Steuerungslogik der TODO-App
# Verantwortlichkeiten:
# - Koordination zwischen Model und View
# - Geschäftslogik für CRUD-Operationen
# - Event-Handling und Datenfluss-Steuerung

from datetime import date
from typing import List, Optional, Dict
from model import Task, Category, TaskRepository


class TaskController:
    """Controller für Task-Operationen"""
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository
    
    def create_task(self, title: str, category: str = "Keine", 
                   due_date: Optional[date] = None) -> bool:
        """Erstellt eine neue Task"""
        task = Task(
            id=0,  # Wird vom Repository gesetzt
            title=title.strip(),
            category=category,
            due_date=due_date.isoformat() if due_date else None
        )
        return self.repository.add_task(task)


    def get_all_tasks(self) -> List[Task]:
        """Gibt alle Tasks zurück"""
        return self.repository.get_all_tasks()
    
    def get_filtered_tasks(self, status: Optional[str] = None,
                          category: Optional[str] = None) -> List[Task]:
        """Gibt gefilterte Tasks zurück (FR-05)"""
        return self.repository.filter_tasks(status, category)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Gibt einzelne Task zurück"""
        return self.repository.get_task_by_id(task_id)
    
    def get_archived_tasks(self) -> List[Task]:
        """Gibt archivierte Tasks zurück"""
        return self.repository.get_archived_tasks()
    
    def get_urgent_tasks(self) -> List[Task]:
        """Gibt dringliche Tasks zurück"""
        return self.repository.get_urgent_tasks()
    
    def update_task(self, task_id: int, title: str, category: str,
                   due_date: Optional[date] = None) -> bool:
        """Aktualisiert eine Task (FR-03)"""
        task = Task(
            id=task_id,
            title=title.strip(),
            category=category,
            due_date=due_date.isoformat() if due_date else None
        )
        return self.repository.update_task(task)
    
    def toggle_task_completion(self, task_id: int) -> bool:
        """Markiert Task als erledigt/offen (FR-04)"""
        return self.repository.toggle_task_completion(task_id)
    
    def restore_task(self, task_id: int) -> bool:
        """Stellt archivierte Task wieder her"""
        return self.repository.restore_task(task_id)
        
    def delete_task(self, task_id: int) -> bool:
        """Löscht eine Task (FR-02)"""
        return self.repository.delete_task(task_id)
    

class CategoryController:
    """Controller für Kategorie-Operationen"""
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository
    
    def get_all_categories(self) -> List[str]:
        """Gibt die Namen der Kategorien zurück"""
        return [c["name"] for c in self.repository.get_categories()]
    
    def get_categories_with_colors(self) -> List[Dict]:
        """Gibt Kategorien mit ihren Farben zurück"""
        return self.repository.get_categories()
    
    def get_category_color(self, name: str) -> str:
        """Gibt die Farbe für einen Kategorienamen zurück"""
        return self.repository.get_category_color(name)
    
    def create_category(self, name: str, color: str = "#e8e8e8") -> bool:
        """Erstellt neue Kategorie mit Farbe (FR-12)"""
        category = Category(name.strip(), color)
        return self.repository.add_category(category)
    
    def delete_category(self, name: str) -> bool:
        """Löscht Kategorie"""
        return self.repository.delete_category(name)
    
    def can_add_category(self) -> bool:
        """Prüft ob weitere Kategorie hinzugefügt werden kann"""
        return len(self.get_all_categories()) < Category.MAX_CATEGORIES


class ApplicationController:
    """Haupt-Controller der Anwendung"""
    
    def __init__(self):
        self.repository = TaskRepository()
        self.task_controller = TaskController(self.repository)
        self.category_controller = CategoryController(self.repository)
    
    def get_task_controller(self) -> TaskController:
        """Gibt Task-Controller zurück"""
        return self.task_controller
    
    def get_category_controller(self) -> CategoryController:
        """Gibt Category-Controller zurück"""
        return self.category_controller
