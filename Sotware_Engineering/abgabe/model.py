"""
MODEL - Datenschicht der TODO-App
Verantwortlichkeiten:
- Domänenobjekte (Task, Category)
- Datenzugriff und Persistierung
- Validierungslogik
"""

import json
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict


class Task:
    """Domänenobjekt für eine Aufgabe (FR-00)"""
    
    def __init__(self, id: int, title: str, completed: bool = False, 
                 category: str = "Keine", due_date: Optional[str] = None):
        self.id = id
        self.title = title
        self.completed = completed
        self.category = category
        self.due_date = due_date
    
    def validate(self) -> bool:
        """Validiert die Task-Daten"""
        return bool(self.title and self.title.strip())
    
    def is_urgent(self) -> bool:
        """Prüft ob Aufgabe dringlich ist (heute oder morgen fällig)"""
        if not self.due_date:
            return False
        try:
            due = datetime.fromisoformat(self.due_date).date()
            today = date.today()
            tomorrow = today + timedelta(days=1)
            return due == today or due == tomorrow
        except:
            return False
    
    def to_dict(self) -> Dict:
        """Serialisiert Task für JSON-Speicherung"""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "category": self.category,
            "due_date": self.due_date
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        """Erstellt Task aus Dictionary"""
        return Task(
            id=data["id"],
            title=data["title"],
            completed=data.get("completed", False),
            category=data.get("category", "Keine"),
            due_date=data.get("due_date")
        )


class Category:
    """Domänenobjekt für Kategorien (FR-06)"""
    
    MAX_CATEGORIES = 8
    
    def __init__(self, name: str, color: str = "#e8e8e8"):
        self.name = name
        self.color = color
    
    def validate(self) -> bool:
        """Validiert Kategorie-Daten"""
        return bool(self.name and self.name.strip())


class TaskRepository:
    """Datenzugriff und Persistierung (FR-01)"""
    
    def __init__(self, data_file: Path = Path("todo_data.json")):
        self.data_file = data_file
        self.data = self._load_data()
        self._migrate_categories()
    
    def _load_data(self) -> Dict:
        """Lädt Daten aus JSON-Datei"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return self._get_default_data()
        return self._get_default_data()
    
    def _migrate_categories(self) -> None:
        """Migriert alte String-Kategorien zu Objekten falls nötig"""
        if not self.data.get("categories"):
            self.data["categories"] = self._get_default_data()["categories"]
            self.save()
            return

        new_categories = []
        changed = False
        default_colors = ["#4e73df", "#1cc88a", "#36b9cc", "#f6c23e", "#e74a3b", "#858796"]
        
        for i, cat in enumerate(self.data["categories"]):
            if isinstance(cat, str):
                color = default_colors[i % len(default_colors)]
                new_categories.append({"name": cat, "color": color})
                changed = True
            else:
                new_categories.append(cat)
        
        if changed:
            self.data["categories"] = new_categories
            self.save()
    
    def _get_default_data(self) -> Dict:
        """Gibt Standard-Datenstruktur zurück"""
        return {
            "tasks": [],
            "archived_tasks": [],
            "categories": [
                {"name": "Arbeit", "color": "#4e73df"},
                {"name": "Privat", "color": "#1cc88a"}
            ],
            "next_id": 1
        }
    
    def save(self) -> None:
        """Speichert Daten in JSON-Datei"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_all_tasks(self) -> List[Task]:
        """Gibt alle aktiven Tasks zurück"""
        return [Task.from_dict(t) for t in self.data["tasks"]]
    
    def get_archived_tasks(self) -> List[Task]:
        """Gibt alle archivierten Tasks zurück"""
        if "archived_tasks" not in self.data:
            self.data["archived_tasks"] = []
        return [Task.from_dict(t) for t in self.data["archived_tasks"]]
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Findet Task nach ID"""
        for task_data in self.data["tasks"]:
            if task_data["id"] == task_id:
                return Task.from_dict(task_data)
        return None
    
    def add_task(self, task: Task) -> bool:
        """Fügt neue Task hinzu"""
        if not task.validate():
            return False
        task.id = self.data["next_id"]
        self.data["tasks"].insert(0, task.to_dict())  # Neue oben einfügen
        self.data["next_id"] += 1
        self.save()
        return True
    
    def update_task(self, task: Task) -> bool:
        """Aktualisiert existierende Task (FR-03)"""
        if not task.validate():
            return False
        for i, t in enumerate(self.data["tasks"]):
            if t["id"] == task.id:
                self.data["tasks"][i] = task.to_dict()
                self.save()
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Löscht Task (FR-02) - aus aktiven Tasks oder Archiv"""
        # Aus aktiven Tasks löschen
        original_len = len(self.data["tasks"])
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        
        # Aus Archiv löschen falls nicht in aktiven gefunden
        if len(self.data["tasks"]) == original_len:
            if "archived_tasks" in self.data:
                original_archived_len = len(self.data["archived_tasks"])
                self.data["archived_tasks"] = [t for t in self.data["archived_tasks"] if t["id"] != task_id]
                if len(self.data["archived_tasks"]) < original_archived_len:
                    self.save()
                    return True
            return False
        
        self.save()
        return True
    
    def toggle_task_completion(self, task_id: int) -> bool:
        """Markiert Task als erledigt/offen (FR-04)"""
        for i, task_data in enumerate(self.data["tasks"]):
            if task_data["id"] == task_id:
                task_data["completed"] = not task_data["completed"]
                # Bei Erledigung ins Archiv verschieben
                if task_data["completed"]:
                    if "archived_tasks" not in self.data:
                        self.data["archived_tasks"] = []
                    self.data["archived_tasks"].insert(0, task_data)
                    self.data["tasks"].pop(i)
                self.save()
                return True
        return False
    
    def restore_task(self, task_id: int) -> bool:
        """Stellt archivierte Task wieder her"""
        if "archived_tasks" not in self.data:
            return False
        for i, task_data in enumerate(self.data["archived_tasks"]):
            if task_data["id"] == task_id:
                task_data["completed"] = False
                self.data["tasks"].insert(0, task_data)
                self.data["archived_tasks"].pop(i)
                self.save()
                return True
        return False
    
    def get_categories(self) -> List[Dict]:
        """Gibt alle Kategorien als Dicts zurück"""
        return self.data.get("categories", [])
    
    def get_category_color(self, name: str) -> str:
        """Gibt die Farbe einer Kategorie zurück"""
        for cat in self.data.get("categories", []):
            if cat["name"] == name:
                return cat["color"]
        return "#e8e8e8"
    
    def add_category(self, category: Category) -> bool:
        """Fügt neue Kategorie hinzu (FR-06)"""
        if not category.validate():
            return False
        if any(c["name"] == category.name for c in self.data["categories"]):
            return False
        if len(self.data["categories"]) >= Category.MAX_CATEGORIES:
            return False
        self.data["categories"].append({"name": category.name, "color": category.color})
        self.save()
        return True
    
    def delete_category(self, category_name: str) -> bool:
        """Löscht Kategorie"""
        self.data["categories"] = [c for c in self.data["categories"] if c["name"] != category_name]
        # Tasks auf "Keine" setzen
        for task in self.data["tasks"]:
            if task["category"] == category_name:
                task["category"] = "Keine"
        for task in self.data.get("archived_tasks", []):
            if task["category"] == category_name:
                task["category"] = "Keine"
        self.save()
        return True
    
    def filter_tasks(self, status: Optional[str] = None, 
                    category: Optional[str] = None) -> List[Task]:
        """Filtert Tasks nach Status und Kategorie (FR-07)"""
        tasks = self.get_all_tasks()
        
        # Nach Status filtern
        if status == "Offen":
            tasks = [t for t in tasks if not t.completed]
        elif status == "Erledigt":
            tasks = [t for t in tasks if t.completed]
        
        # Nach Kategorie filtern
        if category and category != "Alle":
            tasks = [t for t in tasks if t.category == category]
        
        return tasks
    
    def get_urgent_tasks(self) -> List[Task]:
        """Gibt alle dringlichen Tasks zurück"""
        return [t for t in self.get_all_tasks() if t.is_urgent()]

