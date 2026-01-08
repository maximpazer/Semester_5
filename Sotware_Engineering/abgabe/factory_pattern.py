"""
Factory Pattern - ToDo-App Aufgabentypen

Das Factory Pattern wird verwendet:
- Wenn der genaue Objekttyp erst zur Laufzeit feststeht
- Wenn Nutzer eigene Erweiterungen einbauen sollen
- Wenn vorhandene Objekte wiederverwendet werden sollen

Vorteile:
- Client-Code kennt keine konkreten Klassen
- Einfache Erweiterbarkeit (neue Task-Typen hinzufügen)
- Zentrale Objekterzeugung
"""

from abc import ABC, abstractmethod


# ABSTRAKTE BASISKLASSE (Interface)

class Task(ABC):
    """
    Abstrakte Basisklasse für alle Aufgabentypen.
    Definiert das Interface, das alle konkreten Tasks implementieren müssen.
    """
    
    @abstractmethod
    def describe(self) -> str:
        """Beschreibt die Aufgabe - muss von Subklassen implementiert werden."""
        pass


# KONKRETE IMPLEMENTIERUNGEN

class TodoTask(Task):
    """Normale allgemeine Aufgabe"""
    
    def describe(self) -> str:
        return "Dies ist eine allgemeine ToDo-Aufgabe."


class ShoppingTask(Task):
    """Einkaufslisten-Aufgabe"""
    
    def describe(self) -> str:
        return "Dies ist eine Einkaufsliste-Aufgabe."


class WorkTask(Task):
    """Arbeitsaufgabe"""
    
    def describe(self) -> str:
        return "Dies ist eine Arbeitsaufgabe."


# FACTORY
class TaskFactory:
    """
    Factory-Klasse zur Erzeugung von Task-Objekten.
    
    Der Client muss nur den Typ als String angeben,
    die Factory kümmert sich um die konkrete Instanziierung.
    """
    
    # Mapping von Typ-String zu konkreter Klasse
    _task_types = {
        "todo": TodoTask,
        "shopping": ShoppingTask,
        "work": WorkTask
    }
    
    def create_task(self, task_type: str) -> Task:
        """
        Erzeugt eine Task basierend auf dem angegebenen Typ.
        
        Args:
            task_type: Art der Aufgabe ("todo", "shopping", "work")
            
        Returns:
            Task: Konkrete Task-Instanz
            
        Raises:
            ValueError: Wenn der Typ unbekannt ist
        """
        task_type = task_type.lower()
        
        if task_type not in self._task_types:
            raise ValueError(
                f"Unbekannter Task-Typ: '{task_type}'. "
                f"Verfügbar: {list(self._task_types.keys())}"
            )
        
        # Konkrete Klasse aus dem Mapping holen und instanziieren
        task_class = self._task_types[task_type]
        return task_class()
    
    @classmethod
    def register_task_type(cls, type_name: str, task_class: type) -> None:
        """
        Registriert einen neuen Task-Typ (Erweiterbarkeit).
        
        Args:
            type_name: Name des neuen Typs
            task_class: Klasse, die Task implementiert
        """
        if not issubclass(task_class, Task):
            raise TypeError(f"{task_class} muss von Task erben")
        cls._task_types[type_name.lower()] = task_class


# CLIENT-CODE (Beispiel)

if __name__ == "__main__":
    # Factory erstellen
    factory = TaskFactory()
    
    # Tasks über Factory erzeugen (Client kennt keine konkreten Klassen)
    task1 = factory.create_task("todo")
    task2 = factory.create_task("shopping")
    task3 = factory.create_task("work")
    
    # Beschreibungen ausgeben
    print(task1.describe())  # Dies ist eine allgemeine ToDo-Aufgabe.
    print(task2.describe())  # Dies ist eine Einkaufsliste-Aufgabe.
    print(task3.describe())  # Dies ist eine Arbeitsaufgabe.
    
    print("\n--- Erweiterbarkeit demonstrieren ---")
    
    # Neuen Task-Typ zur Laufzeit registrieren
    class UrgentTask(Task):
        def describe(self) -> str:
            return "Dies ist eine DRINGENDE Aufgabe!"
    
    TaskFactory.register_task_type("urgent", UrgentTask)
    
    task4 = factory.create_task("urgent")
    print(task4.describe())  # Dies ist eine DRINGENDE Aufgabe!
