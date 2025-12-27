"""
Minimalistische TODO-App mit Streamlit
Alle funktionalen Requirements in einer Datei implementiert
Mit Nielsen-Usability-Prinzipien
"""

import streamlit as st
import json
import html
from pathlib import Path
from datetime import date, datetime, timedelta

# ============================================================================
# PERSISTENTE SPEICHERUNG (FR-01)
# ============================================================================

DATA_FILE = Path("todo_data.json")

def load_data():
    """Lädt Daten aus JSON-Datei."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return get_default_data()
    return get_default_data()

def save_data(data):
    """Speichert Daten in JSON-Datei."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # Nielsen #1: Visibility of system status - Feedback beim Speichern
    st.session_state.last_save_time = datetime.now()

def get_default_data():
    """Gibt Standard-Datenstruktur zurück."""
    return {
        "tasks": [],
        "archived_tasks": [],
        "categories": ["Arbeit", "Privat"],
        "next_id": 1
    }

# ============================================================================
# SESSION STATE INITIALISIERUNG
# ============================================================================

if "data" not in st.session_state:
    st.session_state.data = load_data()

if "filter_status" not in st.session_state:
    st.session_state.filter_status = "Alle"

if "filter_category" not in st.session_state:
    st.session_state.filter_category = "Alle"

if "edit_task_id" not in st.session_state:
    st.session_state.edit_task_id = None

if "show_archived" not in st.session_state:
    st.session_state.show_archived = False

if "delete_confirm" not in st.session_state:
    st.session_state.delete_confirm = None

if "show_help" not in st.session_state:
    st.session_state.show_help = False

if "last_save_time" not in st.session_state:
    st.session_state.last_save_time = None

# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def add_task(title, category="Keine", due_date=None):
    """Fügt eine neue Aufgabe hinzu."""
    if not title.strip():
        return False
    
    task = {
        "id": st.session_state.data["next_id"],
        "title": title.strip(),
        "completed": False,
        "category": category,
        "due_date": due_date.isoformat() if due_date else None
    }
    
    st.session_state.data["tasks"].append(task)
    st.session_state.data["next_id"] += 1
    save_data(st.session_state.data)
    return True

def delete_task(task_id):
    """Löscht eine Aufgabe (FR-02)."""
    st.session_state.data["tasks"] = [
        t for t in st.session_state.data["tasks"] 
        if t["id"] != task_id
    ]
    save_data(st.session_state.data)

def toggle_task(task_id):
    """Markiert Aufgabe als erledigt/offen (FR-04) und archiviert bei Erledigung."""
    for task in st.session_state.data["tasks"]:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            # Bei Erledigung ins Archiv verschieben
            if task["completed"]:
                if "archived_tasks" not in st.session_state.data:
                    st.session_state.data["archived_tasks"] = []
                st.session_state.data["archived_tasks"].append(task)
                st.session_state.data["tasks"].remove(task)
            save_data(st.session_state.data)
            break

def restore_task(task_id):
    """Stellt archivierte Aufgabe wieder her."""
    if "archived_tasks" not in st.session_state.data:
        return
    
    for task in st.session_state.data["archived_tasks"]:
        if task["id"] == task_id:
            task["completed"] = False
            st.session_state.data["tasks"].append(task)
            st.session_state.data["archived_tasks"].remove(task)
            save_data(st.session_state.data)
            break

def is_urgent(task):
    """Prüft ob Aufgabe dringlich ist (heute oder morgen fällig)."""
    if not task.get("due_date"):
        return False
    
    try:
        due = datetime.fromisoformat(task["due_date"]).date()
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        return due == today or due == tomorrow
    except:
        return False

def get_urgent_tasks():
    """Gibt alle dringlichen Aufgaben zurück."""
    return [t for t in st.session_state.data["tasks"] if is_urgent(t)]

def update_task(task_id, title, category, due_date):
    """Bearbeitet eine bestehende Aufgabe (FR-03)."""
    if not title.strip():
        return False
    
    for task in st.session_state.data["tasks"]:
        if task["id"] == task_id:
            task["title"] = title.strip()
            task["category"] = category
            task["due_date"] = due_date.isoformat() if due_date else None
            save_data(st.session_state.data)
            return True
    return False

def get_filtered_tasks():
    """Filtert Aufgaben nach Status und Kategorie (FR-07)."""
    # Nur aktive (nicht archivierte) Aufgaben anzeigen
    tasks = st.session_state.data["tasks"]
    
    # Nach Status filtern (nur bei aktiven Aufgaben relevant)
    if st.session_state.filter_status == "Offen":
        tasks = [t for t in tasks if not t["completed"]]
    elif st.session_state.filter_status == "Erledigt":
        tasks = [t for t in tasks if t["completed"]]
    
    # Nach Kategorie filtern
    if st.session_state.filter_category != "Alle":
        tasks = [t for t in tasks if t["category"] == st.session_state.filter_category]
    
    return tasks

def get_archived_tasks():
    """Gibt alle archivierten Aufgaben zurück."""
    if "archived_tasks" not in st.session_state.data:
        st.session_state.data["archived_tasks"] = []
    return st.session_state.data["archived_tasks"]

def add_category(name):
    """Fügt eine neue Kategorie hinzu (FR-06)."""
    name = name.strip()
    if not name:
        return False
    if name in st.session_state.data["categories"]:
        return False
    if len(st.session_state.data["categories"]) >= 5:
        return False
    
    st.session_state.data["categories"].append(name)
    save_data(st.session_state.data)
    return True

def delete_category(name):
    """Löscht eine Kategorie und setzt Tasks auf 'Keine'."""
    if name not in st.session_state.data["categories"]:
        return False
    
    # Tasks auf "Keine" setzen
    for task in st.session_state.data["tasks"]:
        if task["category"] == name:
            task["category"] = "Keine"
    
    st.session_state.data["categories"].remove(name)
    save_data(st.session_state.data)
    return True

def get_stats():
    """Berechnet Statistiken."""
    tasks = st.session_state.data["tasks"]
    return {
        "total": len(tasks),
        "open": sum(1 for t in tasks if not t["completed"]),
        "done": sum(1 for t in tasks if t["completed"])
    }

def format_due_label(due_str):
    """Gibt eine reduzierte Datumsanzeige zurück."""
    if not due_str:
        return None
    try:
        due = datetime.fromisoformat(due_str).date()
        today = date.today()
        if due == today:
            return "heute"
        if due == today + timedelta(days=1):
            return "morgen"
        return due.strftime("%d.%m.%Y")
    except ValueError:
        return due_str

# ============================================================================
# STREAMLIT UI
# ============================================================================

# Page Config
st.set_page_config(
    page_title="TODO App",
    layout="centered"
)

# Responsive CSS
st.markdown("""
<style>
    /* Base responsive container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1000px;
    }
    
    /* Responsive buttons */
    .stButton button {
        min-height: 2.5rem;
        padding: 0.5rem 1rem;
    }
    
    /* Responsive form inputs */
    .stTextInput input, .stDateInput input, .stSelectbox select {
        font-size: 1rem;
        padding: 0.5rem;
    }
    
    /* Task rows responsive */
    div[data-testid="column"] {
        padding: 0.25rem;
    }
    
    /* Tablet adjustments (768px - 1024px) */
    @media (max-width: 1024px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        
        .stButton button {
            font-size: 0.95rem;
        }
    }
    
    /* Mobile adjustments (<768px) */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            padding-top: 1rem;
        }
        
        /* Larger touch targets for mobile */
        .stButton button {
            min-height: 3rem;
            font-size: 1rem;
            width: 100%;
        }
        
        /* Stack columns on mobile */
        div[data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
        
        /* Larger text for readability */
        h1 {
            font-size: 1.75rem !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
        }
        
        /* Checkbox larger on mobile */
        label[data-baseweb="checkbox"] {
            padding: 0.5rem 0;
        }
        
        /* Sidebar full width on mobile when open */
        section[data-testid="stSidebar"] {
            min-width: 100%;
        }
    }
    
    /* Small mobile (<480px) */
    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.25rem;
            padding-right: 0.25rem;
        }
        
        .stButton button {
            padding: 0.75rem 0.5rem;
            font-size: 0.9rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("TODO")

# Nielsen #1: Visibility of system status - Speicherstatus anzeigen
if st.session_state.last_save_time:
    st.caption(
        f"Automatisch gespeichert um {st.session_state.last_save_time.strftime('%H:%M:%S')}"
    )

# ============================================================================
# SIDEBAR: FILTER & VERWALTUNG (FR-07)
# ============================================================================

with st.sidebar:
    st.subheader("Filter")
    status_options = ["Alle", "Offen", "Erledigt"]
    st.session_state.filter_status = st.radio(
        "Status",
        status_options,
        index=status_options.index(st.session_state.filter_status)
    )
    categories = ["Alle", "Keine"] + st.session_state.data["categories"]
    st.session_state.filter_category = st.selectbox(
        "Kategorie",
        categories,
        index=categories.index(st.session_state.filter_category)
        if st.session_state.filter_category in categories else 0
    )

    with st.expander("Kategorien verwalten"):
        current_categories = st.session_state.data["categories"]
        if len(current_categories) < 5:
            with st.form("add_category_form"):
                new_category = st.text_input("Neue Kategorie", max_chars=30)
                submit_cat = st.form_submit_button("Hinzufügen")
                if submit_cat:
                    if add_category(new_category):
                        st.rerun()
                    elif not new_category.strip():
                        st.error("Bitte einen Namen eingeben.")
                    else:
                        st.error("Kategorie existiert bereits oder Limit erreicht.")
        else:
            st.caption("Maximal 5 Kategorien möglich.")

        if current_categories:
            for cat in current_categories:
                col_a, col_b = st.columns([3, 1])
                col_a.write(cat)
                if col_b.button("Löschen", key=f"del_cat_{cat}"):
                    delete_category(cat)
                    st.rerun()

    st.session_state.show_archived = st.checkbox(
        "Archiv anzeigen",
        value=st.session_state.show_archived
    )

    st.session_state.show_help = st.checkbox(
        "Hilfe anzeigen",
        value=st.session_state.show_help
    )

# ============================================================================
# HAUPTBEREICH: NEUE AUFGABE
# ============================================================================

categories_only = st.session_state.data["categories"]

with st.form("add_task_form", clear_on_submit=True):
    # Responsive: Stack on mobile, side-by-side on desktop
    col_title, col_date, col_add = st.columns([3, 1.5, 0.8])

    with col_title:
        new_title = st.text_input(
            "Titel*",
            placeholder="Neue Aufgabe",
            max_chars=200,
            label_visibility="collapsed"
        )
        new_category = st.selectbox(
            "Kategorie",
            ["Keine"] + categories_only,
            label_visibility="visible"
        )

    with col_date:
        new_due_date = st.date_input(
            "Fälligkeitsdatum",
            value=None,
            min_value=date.today(),
            label_visibility="visible"
        )

    with col_add:
        st.write("")  # Spacing for alignment
        submit_task = st.form_submit_button("➕ Hinzufügen", type="primary", use_container_width=True)

    if submit_task:
        if add_task(new_title, new_category, new_due_date):
            st.rerun()
        else:
            st.error("Titel erforderlich.")

if st.session_state.show_help:
    with st.expander("Anleitung", expanded=True):
        st.write("Neue Aufgabe eintragen, Kategorie wählen, optional ein Datum setzen und hinzufügen.")

# ============================================================================
# AUFGABENLISTE (FR-05)
# ============================================================================

st.markdown("### Aufgaben")

filtered_tasks = get_filtered_tasks()

if not filtered_tasks:
    st.caption("Keine Aufgaben vorhanden.")
else:
    filtered_tasks.sort(key=lambda t: (not is_urgent(t), -t["id"]))

    for task in filtered_tasks:
        if st.session_state.edit_task_id == task["id"]:
            with st.form(f"edit_form_{task['id']}"):
                edit_col_title, edit_col_date, edit_col_action = st.columns([3, 1.2, 0.8])
                with edit_col_title:
                    edit_title = st.text_input(
                        "Titel",
                        value=task["title"],
                        max_chars=200
                    )
                    edit_category = st.selectbox(
                        "Kategorie",
                        ["Keine"] + categories_only,
                        index=(["Keine"] + categories_only).index(task["category"])
                        if task["category"] in (["Keine"] + categories_only) else 0
                    )
                with edit_col_date:
                    edit_due_date = st.date_input(
                        "Fällig",
                        value=datetime.fromisoformat(task["due_date"]).date()
                        if task["due_date"] else None,
                        min_value=date.today()
                    )
                with edit_col_action:
                    save_btn = st.form_submit_button("Speichern", type="primary")
                    cancel_btn = st.form_submit_button("Abbrechen")

                if save_btn:
                    if update_task(task["id"], edit_title, edit_category, edit_due_date):
                        st.session_state.edit_task_id = None
                        st.rerun()
                    else:
                        st.error("Titel darf nicht leer sein.")
                if cancel_btn:
                    st.session_state.edit_task_id = None
                    st.rerun()
            continue

        row = st.container()
        with row:
            # Responsive: Adjust column ratios for better mobile display
            cols = st.columns([0.5, 5, 1.5])
            with cols[0]:
                cb_key = f"task_cb_{task['id']}"
                st.session_state[cb_key] = task["completed"]
                st.checkbox(
                    "",
                    key=cb_key,
                    on_change=toggle_task,
                    args=(task["id"],),
                    label_visibility="collapsed"
                )
            with cols[1]:
                title_html = html.escape(task["title"])
                title_style = "text-decoration: line-through; opacity: 0.6;" if task["completed"] else ""
                meta_parts = []
                if task["category"] != "Keine":
                    meta_parts.append(html.escape(task["category"]))
                due_text = format_due_label(task.get("due_date"))
                if due_text:
                    meta_parts.append(html.escape(due_text))
                meta_html = f"<small style='opacity: 0.7;'>{' · '.join(meta_parts)}</small>" if meta_parts else ""
                st.markdown(
                    f"<div style='padding: 0.6rem 0; border-bottom: 1px solid rgba(128,128,128,0.2);'>"
                    f"<div style='font-size: 1rem; {title_style}'>{title_html}</div>{meta_html}</div>",
                    unsafe_allow_html=True
                )
            with cols[2]:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️", key=f"edit_{task['id']}", help="Bearbeiten", use_container_width=True):
                        st.session_state.edit_task_id = task["id"]
                        st.rerun()
                with btn_col2:
                    if st.session_state.delete_confirm == task["id"]:
                        if st.button("✓", key=f"confirm_yes_{task['id']}", help="Bestätigen", use_container_width=True):
                            delete_task(task["id"])
                            st.session_state.delete_confirm = None
                            st.rerun()
                    else:
                        if st.button("🗑️", key=f"delete_{task['id']}", help="Löschen", use_container_width=True):
                            st.session_state.delete_confirm = task["id"]
                            st.rerun()

# ============================================================================
# ARCHIV
# ============================================================================

if st.session_state.show_archived:
    st.markdown("### Archiv")
    archived = get_archived_tasks()
    if not archived:
        st.caption("Keine archivierten Aufgaben.")
    else:
        archived.sort(key=lambda t: -t["id"])
        for task in archived:
            # Responsive: Better mobile layout for archive
            cols = st.columns([5, 2])
            with cols[0]:
                title_html = html.escape(task["title"])
                meta_parts = []
                if task["category"] != "Keine":
                    meta_parts.append(html.escape(task["category"]))
                due_text = format_due_label(task.get("due_date"))
                if due_text:
                    meta_parts.append(html.escape(due_text))
                meta_html = f"<small style='opacity: 0.7;'>{' · '.join(meta_parts)}</small>" if meta_parts else ""
                st.markdown(
                    f"<div style='padding: 0.6rem 0; border-bottom: 1px solid rgba(128,128,128,0.2);'>"
                    f"<div style='font-size: 1rem;'>{title_html}</div>{meta_html}</div>",
                    unsafe_allow_html=True
                )
            with cols[1]:
                arch_col1, arch_col2 = st.columns(2)
                with arch_col1:
                    if st.button("↩️", key=f"restore_{task['id']}", help="Wiederherstellen", use_container_width=True):
                        restore_task(task["id"])
                        st.rerun()
                with arch_col2:
                    if st.button("🗑️", key=f"delete_arch_{task['id']}", help="Löschen", use_container_width=True):
                        st.session_state.data["archived_tasks"].remove(task)
                        save_data(st.session_state.data)
                        st.rerun()

# ============================================================================
# FOOTER
# ============================================================================

st.caption("Daten werden automatisch gespeichert und erledigte Aufgaben archiviert.")
