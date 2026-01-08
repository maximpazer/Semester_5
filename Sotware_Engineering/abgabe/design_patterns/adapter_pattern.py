"""
Adapter Pattern - Externe Aufgabenquelle in TODO-App integrieren

Das Adapter Pattern wird verwendet:
- Wenn eine externe Schnittstelle nicht mit der internen kompatibel ist
- Wenn bestehender Code NICHT geändert werden soll
- Wenn verschiedene Datenformate vereinheitlicht werden müssen

SZENARIO:
- Unsere TODO-App verwendet intern die Task-Klasse (aus model.py)
- Eine externe "ProjectManagement-API" liefert Aufgaben in einem ANDEREN Format
- Der Adapter übersetzt zwischen beiden Formaten

STRUKTUR:
┌──────────────────────────────────────────────────────────────────────┐
│  CLIENT (TODO-App)                                                   │
│  ─────────────────                                                   │
│  Erwartet Objekte mit:                                               │
│  - id, title, completed, category, due_date                          │
│  - Methoden: validate(), is_urgent(), to_dict()                      │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ nutzt
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  CLIENT-SCHNITTSTELLE (TaskInterface)                                │
│  ────────────────────────────────────                                │
│  Definiert das erwartete Interface                                   │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ implementiert
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ADAPTER (ExternalTaskAdapter)                                       │
│  ─────────────────────────────                                       │
│  - Implementiert TaskInterface                                       │
│  - Enthält Referenz auf ExternalTask                                 │
│  - Übersetzt zwischen den Formaten                                   │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ wrapped
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  SERVICE (ExternalProjectAPI)                                        │
│  ────────────────────────────                                        │
│  Liefert ExternalTask-Objekte mit ANDEREM Format:                    │
│  - task_id, task_name, status, project, deadline                     │
└──────────────────────────────────────────────────────────────────────┘
"""

from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# 1. CLIENT-SCHNITTSTELLE (Interface das der Client erwartet)
# ═══════════════════════════════════════════════════════════════════════════════

class TaskInterface(ABC):
    """
    Client-Schnittstelle - definiert das Protokoll für alle Task-Objekte.
    
    Unsere TODO-App erwartet, dass alle Tasks dieses Interface implementieren.
    Das entspricht dem Format unserer internen Task-Klasse aus model.py.
    """
    
    @property
    @abstractmethod
    def id(self) -> int:
        """Eindeutige ID der Aufgabe"""
        pass
    
    @property
    @abstractmethod
    def title(self) -> str:
        """Titel/Name der Aufgabe"""
        pass
    
    @property
    @abstractmethod
    def completed(self) -> bool:
        """Erledigt-Status"""
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """Kategorie der Aufgabe"""
        pass
    
    @property
    @abstractmethod
    def due_date(self) -> Optional[str]:
        """Fälligkeitsdatum als ISO-String"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validiert die Task-Daten"""
        pass
    
    @abstractmethod
    def is_urgent(self) -> bool:
        """Prüft ob Aufgabe dringlich ist"""
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict:
        """Serialisiert Task für JSON-Speicherung"""
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# 2. SERVICE (Externe API mit INKOMPATIBLEM Format)
# ═══════════════════════════════════════════════════════════════════════════════

class ExternalTask:
    """
    Externes Aufgaben-Format von der "ProjectManagement-API".
    
    ACHTUNG: Komplett anderes Format als unsere interne Task-Klasse!
    - task_id statt id
    - task_name statt title
    - status ("open"/"done") statt completed (bool)
    - project statt category
    - deadline (datetime) statt due_date (string)
    - priority (1-5) - hat unser internes Format gar nicht!
    """
    
    def __init__(self, task_id: str, task_name: str, status: str,
                 project: str, deadline: Optional[datetime], priority: int):
        self.task_id = task_id           # z.B. "PM-1234"
        self.task_name = task_name       # z.B. "Review Code"
        self.status = status             # "open" oder "done"
        self.project = project           # z.B. "Backend-Refactoring"
        self.deadline = deadline         # datetime-Objekt
        self.priority = priority         # 1 (niedrig) bis 5 (hoch)


class ExternalProjectAPI:
    """
    Fiktive externe API für Projektmanagement-Aufgaben.
    
    Diese API liefert Aufgaben in einem Format, das NICHT mit
    unserer internen Task-Klasse kompatibel ist.
    """
    
    def __init__(self):
        # Simulierte externe Daten
        self._external_tasks = [
            ExternalTask(
                task_id="PM-001",
                task_name="Backend API refactoren",
                status="open",
                project="Backend",
                deadline=datetime.now() + timedelta(days=1),  # Morgen = dringend!
                priority=5
            ),
            ExternalTask(
                task_id="PM-002",
                task_name="Unit Tests schreiben",
                status="done",
                project="Testing",
                deadline=datetime.now() + timedelta(days=7),
                priority=3
            ),
            ExternalTask(
                task_id="PM-003",
                task_name="Dokumentation aktualisieren",
                status="open",
                project="Docs",
                deadline=None,  # Kein Deadline
                priority=2
            ),
            ExternalTask(
                task_id="PM-004",
                task_name="Code Review für PR #42",
                status="open",
                project="Backend",
                deadline=datetime.now(),  # Heute = dringend!
                priority=4
            ),
        ]
    
    def fetch_all_tasks(self) -> List[ExternalTask]:
        """Holt alle Aufgaben von der externen API"""
        return self._external_tasks
    
    def fetch_task_by_id(self, task_id: str) -> Optional[ExternalTask]:
        """Holt eine einzelne Aufgabe nach ID"""
        for task in self._external_tasks:
            if task.task_id == task_id:
                return task
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ADAPTER (Übersetzt zwischen externem und internem Format)
# ═══════════════════════════════════════════════════════════════════════════════

class ExternalTaskAdapter(TaskInterface):
    """
    Adapter - übersetzt ExternalTask in das TaskInterface-Format.
    
    Der Adapter:
    - Implementiert das TaskInterface (was der Client erwartet)
    - Enthält eine Referenz auf das externe Objekt (ExternalTask)
    - Übersetzt alle Aufrufe in das externe Format
    
    So kann der Client mit externen Tasks arbeiten, ohne zu wissen,
    dass sie aus einer anderen Quelle stammen!
    """
    
    def __init__(self, external_task: ExternalTask, internal_id: int):
        """
        Args:
            external_task: Das zu adaptierende externe Task-Objekt
            internal_id: Interne numerische ID (da externe IDs Strings sind)
        """
        self._external = external_task
        self._internal_id = internal_id
    
    # --- Property-Übersetzungen ---
    
    @property
    def id(self) -> int:
        """Übersetzt task_id (string) zu id (int)"""
        return self._internal_id
    
    @property
    def title(self) -> str:
        """Übersetzt task_name zu title"""
        return self._external.task_name
    
    @property
    def completed(self) -> bool:
        """Übersetzt status ("open"/"done") zu completed (bool)"""
        return self._external.status == "done"
    
    @property
    def category(self) -> str:
        """Übersetzt project zu category"""
        return self._external.project
    
    @property
    def due_date(self) -> Optional[str]:
        """Übersetzt deadline (datetime) zu due_date (ISO-string)"""
        if self._external.deadline is None:
            return None
        return self._external.deadline.date().isoformat()
    
    # --- Methoden-Implementierungen ---
    
    def validate(self) -> bool:
        """Validiert die Task-Daten (wie in model.py)"""
        return bool(self._external.task_name and self._external.task_name.strip())
    
    def is_urgent(self) -> bool:
        """Prüft ob Aufgabe dringlich ist (heute oder morgen fällig)"""
        if self._external.deadline is None:
            return False
        due = self._external.deadline.date()
        today = date.today()
        tomorrow = today + timedelta(days=1)
        return due == today or due == tomorrow
    
    def to_dict(self) -> Dict:
        """Serialisiert in das interne Dictionary-Format"""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "category": self.category,
            "due_date": self.due_date
        }
    
    # --- Zusätzliche Methode für externe Daten ---
    
    def get_original_id(self) -> str:
        """Gibt die ursprüngliche externe ID zurück"""
        return self._external.task_id
    
    def get_priority(self) -> int:
        """Gibt die Priorität zurück (nur extern verfügbar)"""
        return self._external.priority


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CLIENT-CODE (Demonstration)
# ═══════════════════════════════════════════════════════════════════════════════

def display_task(task: TaskInterface) -> None:
    """
    Client-Funktion die NUR das TaskInterface kennt.
    
    Sie funktioniert sowohl mit internen Tasks als auch mit
    adaptierten externen Tasks - ohne Änderung!
    """
    status = "✅" if task.completed else "⬜"
    urgent = "🔴 DRINGEND!" if task.is_urgent() else ""
    due = f"(Fällig: {task.due_date})" if task.due_date else "(Kein Datum)"
    
    print(f"  {status} [{task.id}] {task.title}")
    print(f"      Kategorie: {task.category} | {due} {urgent}")


def display_all_tasks(tasks: List[TaskInterface]) -> None:
    """Zeigt alle Tasks an (Client kennt nur TaskInterface)"""
    for task in tasks:
        display_task(task)
        print()


if __name__ == "__main__":
    print("=" * 70)
    print("ADAPTER PATTERN - DEMONSTRATION")
    print("=" * 70)
    
    # --- 1. Externe API simulieren ---
    print("\n📡 Externe ProjectManagement-API wird abgefragt...")
    external_api = ExternalProjectAPI()
    external_tasks = external_api.fetch_all_tasks()
    
    print(f"   → {len(external_tasks)} Aufgaben gefunden (externes Format)")
    
    # --- 2. Externe Tasks über Adapter in internes Format übersetzen ---
    print("\n🔄 Adapter übersetzt ins interne Format...")
    
    adapted_tasks: List[TaskInterface] = []
    for idx, ext_task in enumerate(external_tasks, start=100):
        adapter = ExternalTaskAdapter(ext_task, internal_id=idx)
        adapted_tasks.append(adapter)
    
    # --- 3. Client-Code arbeitet mit adaptierten Tasks ---
    print("\n📋 Alle Aufgaben (Client sieht nur TaskInterface):")
    print("-" * 70)
    display_all_tasks(adapted_tasks)
    
    # --- 4. Demonstration: Daten sind korrekt übersetzt ---
    print("=" * 70)
    print("VERGLEICH: Externes vs. Adaptiertes Format")
    print("=" * 70)
    
    ext = external_tasks[0]
    adapted = adapted_tasks[0]
    
    print(f"\n🔹 EXTERNES FORMAT (ExternalTask):")
    print(f"   task_id:   {ext.task_id}")
    print(f"   task_name: {ext.task_name}")
    print(f"   status:    {ext.status}")
    print(f"   project:   {ext.project}")
    print(f"   deadline:  {ext.deadline}")
    print(f"   priority:  {ext.priority}")
    
    print(f"\n🔹 ADAPTIERTES FORMAT (TaskInterface):")
    print(f"   id:        {adapted.id}")
    print(f"   title:     {adapted.title}")
    print(f"   completed: {adapted.completed}")
    print(f"   category:  {adapted.category}")
    print(f"   due_date:  {adapted.due_date}")
    print(f"   is_urgent: {adapted.is_urgent()}")
    
    print(f"\n🔹 Als Dictionary (to_dict):")
    print(f"   {adapted.to_dict()}")
    
    print("\n" + "=" * 70)
    print("VORTEIL: Der Client-Code (display_task) wurde NICHT geändert!")
    print("Er arbeitet mit JEDEM Objekt das TaskInterface implementiert.")
    print("=" * 70)
