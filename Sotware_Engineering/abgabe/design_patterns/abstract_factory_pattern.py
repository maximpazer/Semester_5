from abc import ABC, abstractmethod


# ABSTRAKTE PRODUKTE

class AbstractTask(ABC):
    """
    Abstraktes Produkt - Interface für alle Aufgabentypen.
    Jede konkrete Task-Klasse muss describe() implementieren.
    """
    
    @abstractmethod
    def describe(self) -> str:
        """Beschreibt die Aufgabe."""
        pass


# KONKRETE PRODUKTE - SIMPLE VARIANTEN

class SimpleTodoTask(AbstractTask):
    """Einfache allgemeine Aufgabe - Kurzform"""
    
    def describe(self) -> str:
        return "ToDo-Aufgabe"


class SimpleShoppingTask(AbstractTask):
    """Einfache Einkaufsaufgabe - Kurzform"""
    
    def describe(self) -> str:
        return "Einkauf"


class SimpleWorkTask(AbstractTask):
    """Einfache Arbeitsaufgabe - Kurzform"""
    
    def describe(self) -> str:
        return "Arbeit"


# KONKRETE PRODUKTE - DETAILED VARIANTEN

class DetailedTodoTask(AbstractTask):
    """Detaillierte allgemeine Aufgabe - Langform"""
    
    def describe(self) -> str:
        return "Dies ist eine ausführliche, allgemeine ToDo-Aufgabe mit allen Details."


class DetailedShoppingTask(AbstractTask):
    """Detaillierte Einkaufsaufgabe - Langform"""
    
    def describe(self) -> str:
        return "Dies ist eine ausführliche Einkaufsliste mit Mengenangaben und Preisen."


class DetailedWorkTask(AbstractTask):
    """Detaillierte Arbeitsaufgabe - Langform"""
    
    def describe(self) -> str:
        return "Dies ist eine ausführliche Arbeitsaufgabe mit Deadline und Priorität."


# ABSTRAKTE FABRIK

class AbstractTaskFactory(ABC):
    """
    Abstrakte Fabrik - definiert das Interface für alle konkreten Fabriken.
    
    Jede konkrete Fabrik muss alle drei Methoden implementieren,
    um eine vollständige "Familie" von zusammengehörigen Tasks zu erzeugen.
    """
    
    @abstractmethod
    def create_todo_task(self) -> AbstractTask:
        """Erzeugt eine ToDo-Aufgabe."""
        pass
    
    @abstractmethod
    def create_shopping_task(self) -> AbstractTask:
        """Erzeugt eine Einkaufsaufgabe."""
        pass
    
    @abstractmethod
    def create_work_task(self) -> AbstractTask:
        """Erzeugt eine Arbeitsaufgabe."""
        pass


# KONKRETE FABRIKEN

class SimpleTaskFactory(AbstractTaskFactory):
    """
    Konkrete Fabrik für einfache/kurze Task-Varianten.
    
    Alle erzeugten Tasks sind konsistent "simpel" gehalten.
    """
    
    def create_todo_task(self) -> AbstractTask:
        return SimpleTodoTask()
    
    def create_shopping_task(self) -> AbstractTask:
        return SimpleShoppingTask()
    
    def create_work_task(self) -> AbstractTask:
        return SimpleWorkTask()


class DetailedTaskFactory(AbstractTaskFactory):
    """
    Konkrete Fabrik für detaillierte/ausführliche Task-Varianten.
    
    Alle erzeugten Tasks sind konsistent "detailliert" gehalten.
    """
    
    def create_todo_task(self) -> AbstractTask:
        return DetailedTodoTask()
    
    def create_shopping_task(self) -> AbstractTask:
        return DetailedShoppingTask()
    
    def create_work_task(self) -> AbstractTask:
        return DetailedWorkTask()


# CLIENT-CODE

def client_code(factory: AbstractTaskFactory) -> None:
    """
    Der Client arbeitet nur mit der abstrakten Factory.
    Er deiß nicht, welche konkreten Klassen erzeugt werden!
    s
    Args:
        factory: Eine beliebige Factory, die AbstractTaskFactory implementiert
    """
    todo = factory.create_todo_task()
    shopping = factory.create_shopping_task()
    work = factory.create_work_task()
    
    print(f"  ToDo:     {todo.describe()}")
    print(f"  Shopping: {shopping.describe()}")
    print(f"  Work:     {work.describe()}")


if __name__ == "__main__":
    print("=" * 60)
    print("ABSTRACT FACTORY PATTERN - DEMONSTRATION")
    print("=" * 60)
    
    # impleTaskFactory verwenden
    print("\n🔹 Mit SimpleTaskFactory:")
    factory = SimpleTaskFactory()  # oder DetailedTaskFactory()
    todo = factory.create_todo_task()
    shopping = factory.create_shopping_task()
    work = factory.create_work_task()
    
    print(f"  {todo.describe()}")
    print(f"  {shopping.describe()}")
    print(f"  {work.describe()}")
    
    # DetailedTaskFactory verwenden 
    print("\n🔹 Mit DetailedTaskFactory:")
    factory = DetailedTaskFactory()
    todo = factory.create_todo_task()
    shopping = factory.create_shopping_task()
    work = factory.create_work_task()
    
    print(f"  {todo.describe()}")
    print(f"  {shopping.describe()}")
    print(f"  {work.describe()}")
    
    # Client-Code demonstrieren
    print("\n" + "-" * 60)
    print("CLIENT-CODE (arbeitet nur mit abstrakter Factory):")
    print("-" * 60)
    
    print("\n Client bekommt SimpleTaskFactory:")
    client_code(SimpleTaskFactory())
    
    print("\n Client bekommt DetailedTaskFactory:")
    client_code(DetailedTaskFactory())
    
    print("\n" + "=" * 60)
    print("VORTEIL: Client-Code ändert sich NICHT - nur die Factory!")
    print("=" * 60)
