"""
VIEW - Präsentationsschicht der TODO-App
Verantwortlichkeiten:
- UI-Rendering mit Streamlit
- Darstellung von Tasks und Kategorien
- Nutzerinteraktionen (Formulare, Buttons)
- Nielsen Usability Heuristics
"""

import streamlit as st
import html
from datetime import date, datetime
from typing import List, Optional
from model import Task


class TaskView:
    """View für Task-Darstellung"""
    
    @staticmethod
    def render_task_form(categories: List[str]) -> dict:
        """Rendert Formular für neue Task (Nielsen #6: Recognition rather than recall)"""
        with st.form("add_task_form", clear_on_submit=True):
            col_title, col_date, col_add = st.columns([3, 1.5, 0.8])
            
            with col_title:
                title = st.text_input(
                    "Titel*",
                    placeholder="Neue Aufgabe",
                    max_chars=200,
                    label_visibility="collapsed",
                    help="Geben Sie einen beschreibenden Titel ein"
                )
                category = st.selectbox(
                    "Kategorie",
                    ["Keine"] + categories,
                    label_visibility="visible"
                )
            
            with col_date:
                due_date = st.date_input(
                    "Fälligkeitsdatum",
                    value=None,
                    min_value=date.today(),
                    label_visibility="visible",
                    help="Optional: Fälligkeitsdatum wählen"
                )
            
            with col_add:
                st.write("")  # Spacing
                submitted = st.form_submit_button(
                    "➕ Hinzufügen",
                    type="primary",
                    use_container_width=True
                )
            
            return {
                "submitted": submitted,
                "title": title,
                "category": category,
                "due_date": due_date
            }
    
    @staticmethod
    def render_task_list(tasks: List[Task], on_toggle, on_edit, on_delete) -> None:
        """Rendert Task-Liste (FR-05, Nielsen #8: Aesthetic and minimalist design)"""
        if not tasks:
            st.caption("Keine Aufgaben vorhanden.")
            return
        
        # Sortierung: Dringliche zuerst
        sorted_tasks = sorted(tasks, key=lambda t: (not t.is_urgent(), -t.id))
        
        for task in sorted_tasks:
            TaskView._render_single_task(task, on_toggle, on_edit, on_delete)
    
    @staticmethod
    def _render_single_task(task: Task, on_toggle, on_edit, on_delete) -> None:
        """Rendert einzelne Task-Zeile"""
        row = st.container()
        with row:
            cols = st.columns([0.5, 5, 1.5])
            
            # Checkbox (FR-04)
            with cols[0]:
                cb_key = f"task_cb_{task.id}"
                if st.checkbox("", key=cb_key, value=task.completed,
                             label_visibility="collapsed"):
                    on_toggle(task.id)
            
            # Task-Info
            with cols[1]:
                TaskView._render_task_info(task)
            
            # Action Buttons
            with cols[2]:
                TaskView._render_task_actions(task, on_edit, on_delete)
    
    @staticmethod
    def _render_task_info(task: Task) -> None:
        """Rendert Task-Informationen"""
        title_html = html.escape(task.title)
        title_style = "text-decoration: line-through; opacity: 0.6;" if task.completed else ""
        
        meta_parts = []
        if task.category != "Keine":
            meta_parts.append(html.escape(task.category))
        
        due_text = TaskView._format_due_date(task.due_date)
        if due_text:
            meta_parts.append(html.escape(due_text))
        
        meta_html = f"<small style='opacity: 0.7;'>{' · '.join(meta_parts)}</small>" if meta_parts else ""
        
        st.markdown(
            f"<div style='padding: 0.6rem 0; border-bottom: 1px solid rgba(128,128,128,0.2);'>"
            f"<div style='font-size: 1rem; {title_style}'>{title_html}</div>{meta_html}</div>",
            unsafe_allow_html=True
        )
    
    @staticmethod
    def _render_task_actions(task: Task, on_edit, on_delete) -> None:
        """Rendert Task-Aktionsbuttons (Nielsen #4: Consistency and standards)"""
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("✏️", key=f"edit_{task.id}", 
                        help="Bearbeiten", use_container_width=True):
                on_edit(task.id)
        
        with btn_col2:
            delete_confirm_key = f"delete_confirm_{task.id}"
            if st.session_state.get(delete_confirm_key):
                if st.button("✓", key=f"confirm_yes_{task.id}",
                           help="Bestätigen", use_container_width=True):
                    on_delete(task.id)
                    st.session_state[delete_confirm_key] = False
            else:
                if st.button("🗑️", key=f"delete_{task.id}",
                           help="Löschen", use_container_width=True):
                    st.session_state[delete_confirm_key] = True
    
    @staticmethod
    def render_edit_form(task: Task, categories: List[str]) -> dict:
        """Rendert Edit-Formular für Task (FR-03)"""
        with st.form(f"edit_form_{task.id}"):
            edit_col_title, edit_col_date, edit_col_action = st.columns([3, 1.2, 0.8])
            
            with edit_col_title:
                title = st.text_input("Titel", value=task.title, max_chars=200)
                category_list = ["Keine"] + categories
                category_index = category_list.index(task.category) if task.category in category_list else 0
                category = st.selectbox("Kategorie", category_list, index=category_index)
            
            with edit_col_date:
                current_due = datetime.fromisoformat(task.due_date).date() if task.due_date else None
                due_date = st.date_input("Fällig", value=current_due, min_value=date.today())
            
            with edit_col_action:
                save = st.form_submit_button("Speichern", type="primary")
                cancel = st.form_submit_button("Abbrechen")
            
            return {
                "saved": save,
                "cancelled": cancel,
                "title": title,
                "category": category,
                "due_date": due_date
            }
    
    @staticmethod
    def _format_due_date(due_str: Optional[str]) -> Optional[str]:
        """Formatiert Fälligkeitsdatum"""
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


class CategoryView:
    """View für Kategorie-Verwaltung"""
    
    @staticmethod
    def render_category_management(categories: List[str], can_add: bool,
                                   on_add, on_delete) -> None:
        """Rendert Kategorie-Verwaltung (FR-06)"""
        with st.expander("Kategorien verwalten"):
            if can_add:
                CategoryView._render_add_category_form(on_add)
            else:
                st.caption("Maximal 5 Kategorien möglich.")
            
            if categories:
                CategoryView._render_category_list(categories, on_delete)
    
    @staticmethod
    def _render_add_category_form(on_add) -> None:
        """Rendert Formular zum Hinzufügen von Kategorien"""
        with st.form("add_category_form"):
            new_category = st.text_input("Neue Kategorie", max_chars=30)
            submit_cat = st.form_submit_button("Hinzufügen")
            
            if submit_cat:
                if new_category.strip():
                    on_add(new_category)
                else:
                    # Nielsen #9: Help users recognize, diagnose, and recover from errors
                    st.error("Bitte einen Namen eingeben.")
    
    @staticmethod
    def _render_category_list(categories: List[str], on_delete) -> None:
        """Rendert Liste bestehender Kategorien"""
        for cat in categories:
            col_a, col_b = st.columns([3, 1])
            col_a.write(cat)
            if col_b.button("Löschen", key=f"del_cat_{cat}"):
                on_delete(cat)


class SidebarView:
    """View für Sidebar mit Filtern"""
    
    @staticmethod
    def render_filters(current_status: str, current_category: str,
                      categories: List[str]) -> dict:
        """Rendert Filter-Optionen (FR-07, Nielsen #7: Flexibility and efficiency)"""
        st.subheader("Filter")
        
        status_options = ["Alle", "Offen", "Erledigt"]
        status = st.radio("Status", status_options,
                         index=status_options.index(current_status))
        
        category_options = ["Alle", "Keine"] + categories
        category_index = category_options.index(current_category) if current_category in category_options else 0
        category = st.selectbox("Kategorie", category_options, index=category_index)
        
        return {"status": status, "category": category}
    
    @staticmethod
    def render_statistics(stats: dict) -> None:
        """Rendert Statistiken (Nielsen #1: Visibility of system status)"""
        col1, col2, col3 = st.columns(3)
        col1.metric("Offen", stats["open"])
        col2.metric("Archiviert", stats["archived"])
        col3.metric("Gesamt", stats["total"])
    
    @staticmethod
    def render_toggles() -> dict:
        """Rendert Toggle-Optionen"""
        show_archived = st.checkbox("Archiv anzeigen",
                                    value=st.session_state.get("show_archived", False))
        show_help = st.checkbox("Hilfe anzeigen",
                               value=st.session_state.get("show_help", False))
        
        return {"show_archived": show_archived, "show_help": show_help}


class ArchiveView:
    """View für Archiv"""
    
    @staticmethod
    def render_archive(tasks: List[Task], on_restore, on_delete) -> None:
        """Rendert Archiv-Ansicht"""
        st.markdown("### Archiv")
        
        if not tasks:
            st.caption("Keine archivierten Aufgaben.")
            return
        
        sorted_tasks = sorted(tasks, key=lambda t: -t.id)
        
        for task in sorted_tasks:
            ArchiveView._render_archived_task(task, on_restore, on_delete)
    
    @staticmethod
    def _render_archived_task(task: Task, on_restore, on_delete) -> None:
        """Rendert einzelne archivierte Task"""
        cols = st.columns([5, 2])
        
        with cols[0]:
            title_html = html.escape(task.title)
            meta_parts = []
            if task.category != "Keine":
                meta_parts.append(html.escape(task.category))
            if task.due_date:
                meta_parts.append(TaskView._format_due_date(task.due_date))
            meta_html = f"<small style='opacity: 0.7;'>{' · '.join(meta_parts)}</small>" if meta_parts else ""
            
            st.markdown(
                f"<div style='padding: 0.6rem 0; border-bottom: 1px solid rgba(128,128,128,0.2);'>"
                f"<div style='font-size: 1rem;'>{title_html}</div>{meta_html}</div>",
                unsafe_allow_html=True
            )
        
        with cols[1]:
            arch_col1, arch_col2 = st.columns(2)
            with arch_col1:
                if st.button("↩️", key=f"restore_{task.id}",
                           help="Wiederherstellen", use_container_width=True):
                    on_restore(task.id)
            with arch_col2:
                if st.button("🗑️", key=f"delete_arch_{task.id}",
                           help="Löschen", use_container_width=True):
                    on_delete(task.id)


class LayoutView:
    """View für Layout und Styling"""
    
    @staticmethod
    def apply_responsive_css() -> None:
        """Wendet responsive CSS an (NFR-Responsive Design)"""
        st.markdown("""
        <style>
            .main .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 1000px;
            }
            .stButton button {
                min-height: 2.5rem;
                padding: 0.5rem 1rem;
            }
            .stTextInput input, .stDateInput input, .stSelectbox select {
                font-size: 1rem;
                padding: 0.5rem;
            }
            div[data-testid="column"] {
                padding: 0.25rem;
            }
            
            @media (max-width: 1024px) {
                .main .block-container {
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
                .stButton button {
                    font-size: 0.95rem;
                }
            }
            
            @media (max-width: 768px) {
                .main .block-container {
                    padding-left: 0.5rem;
                    padding-right: 0.5rem;
                    padding-top: 1rem;
                }
                .stButton button {
                    min-height: 3rem;
                    font-size: 1rem;
                    width: 100%;
                }
                div[data-testid="column"] {
                    width: 100% !important;
                    flex: 100% !important;
                }
                h1 {
                    font-size: 1.75rem !important;
                }
                h3 {
                    font-size: 1.25rem !important;
                }
                label[data-baseweb="checkbox"] {
                    padding: 0.5rem 0;
                }
                section[data-testid="stSidebar"] {
                    min-width: 100%;
                }
            }
            
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
    
    @staticmethod
    def render_header(last_save_time: Optional[datetime]) -> None:
        """Rendert Header (Nielsen #1: Visibility of system status)"""
        st.title("TODO")
        
        if last_save_time:
            st.caption(f"Automatisch gespeichert um {last_save_time.strftime('%H:%M:%S')}")
    
    @staticmethod
    def render_help() -> None:
        """Rendert Hilfe-Sektion (Nielsen #10: Help and documentation)"""
        with st.expander("Anleitung", expanded=True):
            st.write("Neue Aufgabe eintragen, Kategorie wählen, optional ein Datum setzen und hinzufügen.")
    
    @staticmethod
    def render_footer() -> None:
        """Rendert Footer"""
        st.caption("Daten werden automatisch gespeichert und erledigte Aufgaben archiviert.")


from datetime import timedelta
