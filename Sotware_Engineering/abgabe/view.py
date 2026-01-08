# VIEW = Präsentationsschicht 
# Verantwortlichkeiten:
# - UI-Rendering mit Streamlit
# - Darstellung von Tasks und Kategorien
# - Nutzerinteraktionen (Formulare, Buttons)
# - Nielsen Usability Heuristics Implementation

import streamlit as st
import html
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Callable
from model import Task


class TaskView:
    """View für Task-Darstellung"""
    
    @staticmethod
    def render_task_form(categories: List[str]) -> dict:
        """
        Rendert Formular für neue Task
        Nielsen #6: Recognition rather than recall
        Nielsen #8: Aesthetic and minimalist design
        """
        with st.form("add_task_form", clear_on_submit=True, border=False):
            cols = st.columns([4, 2, 2, 1])
            
            with cols[0]:
                title = st.text_input(
                    "Aufgabe",
                    placeholder="Was möchten Sie erledigen?",
                    max_chars=200,
                    label_visibility="collapsed"
                )
            
            with cols[1]:
                category = st.selectbox(
                    "Kategorie",
                    ["Keine"] + categories,
                    label_visibility="collapsed"
                )
            
            with cols[2]:
                due_date = st.date_input(
                    "Fällig",
                    value=None,
                    min_value=date.today(),
                    label_visibility="collapsed",
                    format="DD.MM.YYYY"
                )
            
            with cols[3]:
                submitted = st.form_submit_button(
                    "➕",
                    type="primary",
                    use_container_width=True,
                    help="Aufgabe hinzufügen"
                )
            
            return {
                "submitted": submitted,
                "title": title,
                "category": category,
                "due_date": due_date
            }
    
    @staticmethod
    def render_task_list(tasks: List[Task], on_toggle, on_edit, on_delete, get_color_func: Callable) -> None:
        """
        Rendert Task-Liste
        FR-05: Filterfunktion
        """
        if not tasks:
            st.markdown(
                "<div style='text-align:center; padding:2rem; opacity:0.5;'>"
                "Keine Aufgaben vorhanden</div>",
                unsafe_allow_html=True
            )
            return
        
        for task in tasks:
            TaskView._render_single_task(task, on_toggle, on_edit, on_delete, get_color_func)
    
    @staticmethod
    def _render_single_task(task: Task, on_toggle, on_edit, on_delete, get_color_func: Callable) -> None:
        """Rendert einzelne Task-Zeile"""
        with st.container():
            cols = st.columns([0.4, 5, 1.2])
            
            with cols[0]:
                if st.checkbox("", key=f"cb_{task.id}", value=task.completed,
                             label_visibility="collapsed"):
                    on_toggle(task.id)
            
            with cols[1]:
                TaskView._render_task_info(task, get_color_func)
            
            with cols[2]:
                TaskView._render_task_actions(task, on_edit, on_delete)
    
    @staticmethod
    def _render_task_info(task: Task, get_color_func: Callable) -> None:
        """
        Rendert Task-Informationen
        Layout: Titel oben, Metadaten (Kategorie, Datum) kleiner darunter
        """
        title_html = html.escape(task.title)
        completed_style = "text-decoration: line-through; opacity: 0.5;" if task.completed else ""
        urgent_style = "border-left: 3px solid #ff4b4b; padding-left: 12px;" if task.is_urgent() else "padding-left: 12px;"
        
        # Metadaten sammeln
        meta = []
        if task.category and task.category != "Keine":
            color = get_color_func(task.category)
            text_color = LayoutView.get_text_color_for_bg(color)
            meta.append(
                f"<span style='background:{color}; color:{text_color}; padding:1px 6px; border-radius:4px; "
                f"font-size:0.7rem; font-weight:700;'>{html.escape(task.category)}</span>"
            )
        
        due_text = TaskView._format_due_date(task.due_date)
        if due_text:
            due_color = "#ff4b4b" if task.is_urgent() else "#888"
            meta.append(f"<span style='color:{due_color}; font-size:0.75rem;'>{due_text}</span>")
        
        meta_html = f"<div style='display:flex; align-items:center; gap:8px; margin-top:4px;'>{' '.join(meta)}</div>" if meta else ""
        
        st.markdown(
            f"<div style='padding:0.4rem 0; {urgent_style}'>"
            f"<div style='{completed_style}; font-size:1.05rem; font-weight:400; line-height:1.2;'>{title_html}</div>"
            f"{meta_html}</div>",
            unsafe_allow_html=True
        )
    
    @staticmethod
    def _render_task_actions(task: Task, on_edit, on_delete) -> None:
        """Rendert Task-Aktionsbuttons mit Auto-Reset nach 5 Sekunden"""
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✏️", key=f"edit_{task.id}", help="Bearbeiten"):
                on_edit(task.id)
        with c2:
            confirm_key = f"del_confirm_{task.id}"
            confirm_time_key = f"del_confirm_time_{task.id}"
            
            # Auto-Reset wenn mehr als 5 Sekunden vergangen
            if st.session_state.get(confirm_key):
                confirm_time = st.session_state.get(confirm_time_key)
                if confirm_time and (datetime.now() - confirm_time).seconds > 5:
                    st.session_state[confirm_key] = False
                    del st.session_state[confirm_time_key]
                    st.rerun()
            
            if st.session_state.get(confirm_key):
                if st.button("✖", key=f"confirm_{task.id}", help="Bestätigen"):
                    on_delete(task.id)
                    st.session_state[confirm_key] = False
                    if confirm_time_key in st.session_state:
                        del st.session_state[confirm_time_key]
                    st.rerun()
            else:
                if st.button("🗑", key=f"del_{task.id}", help="Löschen"):
                    st.session_state[confirm_key] = True
                    st.session_state[confirm_time_key] = datetime.now()
                    st.rerun()
    
    @staticmethod
    def render_edit_form(task: Task, categories: List[str]) -> dict:
        """Rendert Edit-Formular"""
        st.markdown("##### ✏️ Aufgabe bearbeiten")
        with st.form(f"edit_form_{task.id}", border=True):
            cols = st.columns([3, 2, 2])
            with cols[0]:
                title = st.text_input("Titel", value=task.title, max_chars=200)
            with cols[1]:
                category_list = ["Keine"] + categories
                cat_idx = category_list.index(task.category) if task.category in category_list else 0
                category = st.selectbox("Kategorie", category_list, index=cat_idx)
            with cols[2]:
                current_due = datetime.fromisoformat(task.due_date).date() if task.due_date else None
                due_date = st.date_input("Fällig", value=current_due, format="DD.MM.YYYY")
            
            btn_cols = st.columns([1, 1, 4])
            with btn_cols[0]:
                save = st.form_submit_button("💾 Speichern", type="primary", use_container_width=True)
            with btn_cols[1]:
                cancel = st.form_submit_button("✖ Abbrechen", use_container_width=True)
            
            return {"saved": save, "cancelled": cancel, "title": title, "category": category, "due_date": due_date}
    
    @staticmethod
    def _format_due_date(due_str: Optional[str]) -> Optional[str]:
        """Formatiert Fälligkeitsdatum"""
        if not due_str: return None
        try:
            due = datetime.fromisoformat(due_str).date()
            today = date.today()
            diff = (due - today).days
            if diff < 0: return "⚠️ überfällig"
            elif diff == 0: return "heute"
            elif diff == 1: return "morgen"
            elif diff <= 7: return f"in {diff} Tagen"
            else: return f"{due.strftime('%d.%m.%Y')}"
        except ValueError: return None


class CategoryView:
    """View für Kategorie-Verwaltung (FR-06)"""
    
    @staticmethod
    def render_category_management(categories_with_colors: List[Dict], can_add: bool,
                                   on_add, on_delete) -> None:
        """Rendert Kategorie-Verwaltung mit Farbauswahl"""
        with st.expander("📁 Kategorien", expanded=False):
            if can_add:
                CategoryView._render_add_category_form(on_add)
            else:
                st.caption("Max. Kategorien erreicht")
            
            if categories_with_colors:
                st.markdown("---")
                CategoryView._render_category_list(categories_with_colors, on_delete)
    
    @staticmethod
    def _render_add_category_form(on_add) -> None:
        """Rendert Formular zum Hinzufügen von Kategorien mit Colorpicker"""
        with st.form("add_category_form", border=False):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                new_category = st.text_input(
                    "Name",
                    max_chars=20,
                    label_visibility="collapsed",
                    placeholder="Kategorie-Name..."
                )
            with cols[1]:
                color = st.color_picker("Farbe", "#4e73df", label_visibility="collapsed")
            with cols[2]:
                submit_cat = st.form_submit_button("➕", use_container_width=True, type="primary")
            
            if submit_cat:
                if new_category.strip():
                    on_add(new_category, color)
                else:
                    st.error("Bitte Namen eingeben")
    
    @staticmethod
    def _render_category_list(categories_with_colors: List[Dict], on_delete) -> None:
        """Rendert Liste bestehender Kategorien mit Farbanzeige"""
        for cat in categories_with_colors:
            cols = st.columns([0.6, 3, 1])
            
            # Farb-Quadrat (Swatch)
            cols[0].markdown(
                f"<div style='width:18px; height:18px; background:{cat['color']}; "
                f"border-radius:4px; margin-top:4px;'></div>",
                unsafe_allow_html=True
            )
            
            # Name als Text daneben (explizit hell für Sidebar-Kontrast)
            cols[1].markdown(
                f"<div style='margin-top:2px; padding-left:4px; white-space:nowrap; overflow:hidden; "
                f"text-overflow:ellipsis; opacity:0.9;'>{html.escape(cat['name'])}</div>",
                unsafe_allow_html=True
            )
            
            # Löschen mit Bestätigung (Two-Step-Delete) + Auto-Reset
            confirm_key = f"del_cat_confirm_{cat['name']}"
            confirm_time_key = f"del_cat_confirm_time_{cat['name']}"
            
            # Auto-Reset wenn mehr als 5 Sekunden vergangen
            if st.session_state.get(confirm_key):
                confirm_time = st.session_state.get(confirm_time_key)
                if confirm_time and (datetime.now() - confirm_time).seconds > 5:
                    st.session_state[confirm_key] = False
                    del st.session_state[confirm_time_key]
                    st.rerun()
            
            if st.session_state.get(confirm_key):
                if cols[2].button("✖", key=f"confirm_cat_{cat['name']}", help="Bestätigen"):
                    on_delete(cat['name'])
                    st.session_state[confirm_key] = False
                    if confirm_time_key in st.session_state:
                        del st.session_state[confirm_time_key]
                    st.rerun()
            else:
                if cols[2].button("🗑", key=f"del_cat_{cat['name']}", help=f"'{cat['name']}' löschen"):
                    st.session_state[confirm_key] = True
                    st.session_state[confirm_time_key] = datetime.now()
                    st.rerun()


class SidebarView:
    """View für Sidebar mit Filtern"""
    
    @staticmethod
    def render_filters(current_status: str, current_category: str,
                      categories: List[str]) -> dict:
        """Rendert Filter-Optionen"""
        st.markdown("#### 🔍 Filter")
        status_options = ["Alle", "Offen"]
        status = st.radio(
            "Status", status_options,
            index=status_options.index(current_status) if current_status in status_options else 0,
            horizontal=True, label_visibility="collapsed"
        )
        category_options = ["Alle"] + categories
        cat_idx = category_options.index(current_category) if current_category in category_options else 0
        category = st.selectbox("Kategorie", category_options, index=cat_idx, label_visibility="collapsed")
        return {"status": status, "category": category}
    
    @staticmethod
    def render_toggles() -> dict:
        """Rendert Toggle-Optionen"""
        st.markdown("#### ⚙️ Optionen")
        show_archived = st.toggle("Archiv anzeigen", value=st.session_state.get("show_archived", False))
        show_help = st.toggle("Hilfe anzeigen", value=st.session_state.get("show_help", False))
        return {"show_archived": show_archived, "show_help": show_help}


class ArchiveView:
    """View für Archiv"""
    
    @staticmethod
    def render_archive(tasks: List[Task], on_restore, on_delete, get_color_func: Callable) -> None:
        """Rendert Archiv-Ansicht"""
        st.markdown("#### Erledigte Aufgaben")
        if not tasks:
            st.caption("Keine erledigten Aufgaben.")
            return
        for task in tasks:
            ArchiveView._render_archived_task(task, on_restore, on_delete, get_color_func)
    
    @staticmethod
    def _render_archived_task(task: Task, on_restore, on_delete, get_color_func: Callable) -> None:
        """Rendert einzelne archivierte Task"""
        with st.container():
            cols = st.columns([0.4, 5, 1.2])
            
            with cols[0]:
                # Symmetrisch zu TaskView: Checkbox (angehakt = erledigt/archiviert)
                # Abwählen stellt wieder her (wie "unerledigt" machen)
                if not st.checkbox("", value=True, key=f"restore_{task.id}", 
                                label_visibility="collapsed"):
                    on_restore(task.id)
            
            with cols[1]:
                title = html.escape(task.title)
                cat_html = ""
                if task.category and task.category != "Keine":
                    color = get_color_func(task.category)
                    text_color = LayoutView.get_text_color_for_bg(color)
                    cat_html = (
                        f"<span style='background:{color}; color:{text_color}; padding:0 4px; border-radius:3px; "
                        f"font-size:0.65rem; font-weight:600; opacity:0.6; margin-left:8px;'>{html.escape(task.category)}</span>"
                    )
                st.markdown(
                    f"<div style='opacity:0.6; padding:0.4rem 0; font-size:1.05rem; line-height:1.2;'>"
                    f"<span style='text-decoration: line-through;'>{title}</span> {cat_html}</div>",
                    unsafe_allow_html=True
                )
            
            with cols[2]:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("↩", key=f"restore_btn_{task.id}", help="Wiederherstellen"):
                        on_restore(task.id)
                with c2:
                    if st.button("🗑", key=f"del_arch_{task.id}", help="Endgültig löschen"):
                        on_delete(task.id)


class LayoutView:
    """Layout und Styling"""
    
    @staticmethod
    def get_text_color_for_bg(hex_color: str) -> str:
        """Berechnet ideale Textfarbe (Schwarz/Weiß) für Hintergrund"""
        try:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) == 3: hex_color = ''.join([c*2 for c in hex_color])
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return "#0e1117" if luminance > 0.5 else "#ffffff"
        except:
            return "#0e1117"

    @staticmethod
    def apply_responsive_css() -> None:
        st.markdown("""
        <style>
            .main .block-container { padding: 1.5rem 1rem; max-width: 800px; }
            .stButton > button { padding: 0.3rem 0.6rem; font-size: 0.85rem; border-radius: 6px; }
            .stTextInput > div > div > input { border-radius: 6px; }
            section[data-testid="stSidebar"] { width: 260px; }
            [data-testid="stMetricValue"] { font-size: 1.3rem; }
            hr { margin: 0.5rem 0; opacity: 0.15; }
            [data-testid="stForm"] { border: none !important; padding: 0 !important; }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_header(last_save_time: Optional[datetime]) -> None:
        """Rendert Header"""
        cols = st.columns([4, 1])
        with cols[0]: st.markdown("# TODO App")
        
        # Toast statt statisches Icon 
        if last_save_time:
            # Checken ob Toast für diesen Save schon gezeigt wurde
            last_shown = st.session_state.get('last_toast_shown')
            if last_shown != last_save_time:
                st.toast("Änderungen gespeichert!", icon="💾")
                st.session_state['last_toast_shown'] = last_save_time
    
    @staticmethod
    def render_help() -> None:
        """Rendert Hilfe (kurze, klare Anleitung)"""
        st.info(
            "Kurzanleitung:\n\n"
            "- Neue Aufgabe: Titel → Kategorie wählen (optional) → Fälligkeitsdatum (optional) → ➕\n"
            "- Erledigen: Checkbox anklicken\n"
            "- Bearbeiten: ✏️ drücken → Änderungen speichern\n"
            "- Löschen: 🗑 drücken → nochmals ❌ bestätigen\n"
            "- Filter: Seitenleiste nutzen, um Aufgaben einzuschränken\n\n"
            "Tipp: Verwende kurze Titel und farbige Kategorien für bessere Übersicht.",
            icon="💡"
        )