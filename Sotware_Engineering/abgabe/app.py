# orchestrierung
# MVC-Architektur
import streamlit as st
from datetime import datetime
from controller import ApplicationController
from view import (TaskView, CategoryView, SidebarView, ArchiveView, LayoutView)

# SESSION STATE INITIALISIERUNG
if "app_controller" not in st.session_state:
    st.session_state.app_controller = ApplicationController()

if "filter_status" not in st.session_state:
    st.session_state.filter_status = "Alle"

if "filter_category" not in st.session_state:
    st.session_state.filter_category = "Alle"

if "edit_task_id" not in st.session_state:
    st.session_state.edit_task_id = None

if "show_archived" not in st.session_state:
    st.session_state.show_archived = False

if "show_help" not in st.session_state:
    st.session_state.show_help = False

if "last_save_time" not in st.session_state:
    st.session_state.last_save_time = None

# CONTROLLER INSTANZEN
app_controller = st.session_state.app_controller
task_controller = app_controller.get_task_controller()
category_controller = app_controller.get_category_controller()

# STREAMLIT UI

# Page Config
st.set_page_config(
    page_title="To-do App",
    layout="centered"
)

# Responsive CSS
LayoutView.apply_responsive_css()

# Header
LayoutView.render_header(st.session_state.last_save_time)

# SIDEBAR: FILTER (FR-05)

with st.sidebar:
    # liefert dictionary mit filter_status und filter_category
    filter_result = SidebarView.render_filters(
        st.session_state.filter_status,
        st.session_state.filter_category,
        category_controller.get_all_categories()
    )
    st.session_state.filter_status = filter_result["status"]
    st.session_state.filter_category = filter_result["category"]
    
    st.divider()
    
    # Kategorie-Management (lambda = anonyme inline-definierte Funktionen)
    CategoryView.render_category_management(
        categories_with_colors=category_controller.get_categories_with_colors(),
        can_add=category_controller.can_add_category(),
        on_add=lambda name, color: category_controller.create_category(name, color) and st.rerun(),
        on_delete=lambda name: category_controller.delete_category(name) and st.rerun()
    )
    
    st.divider()
    
    # Toggles
    toggle_result = SidebarView.render_toggles()
    st.session_state.show_archived = toggle_result["show_archived"]
    st.session_state.show_help = toggle_result["show_help"]

# HAUPTBEREICH: NEUE AUFGABE

form_data = TaskView.render_task_form(category_controller.get_all_categories())

if form_data["submitted"]:
    if task_controller.create_task(
        form_data["title"],
        form_data["category"],
        form_data["due_date"]
    ):
        st.session_state.last_save_time = datetime.now()
        st.rerun()
    else:
        st.error("Titel erforderlich.")

if st.session_state.show_help:
    LayoutView.render_help()

# AUFGABENLISTE (FR-05)

st.markdown("### Aufgaben")

# Gefilterte Tasks holen
filtered_tasks = task_controller.get_filtered_tasks(
    st.session_state.filter_status if st.session_state.filter_status != "Alle" else None,
    st.session_state.filter_category
)

# Edit-Modus prüfen
if st.session_state.edit_task_id:
    task_to_edit = task_controller.get_task(st.session_state.edit_task_id)
    if task_to_edit:
        edit_data = TaskView.render_edit_form(
            task_to_edit,
            category_controller.get_all_categories()
        )
        
        if edit_data["saved"]:
            if task_controller.update_task(
                st.session_state.edit_task_id,
                edit_data["title"],
                edit_data["category"],
                edit_data["due_date"]
            ):
                st.session_state.edit_task_id = None
                st.session_state.last_save_time = datetime.now()
                st.rerun()
            else:
                st.error("Titel darf nicht leer sein.")
        
        if edit_data["cancelled"]:
            st.session_state.edit_task_id = None
            st.rerun()
else:
    # Task-Liste rendern
    TaskView.render_task_list(
        tasks=filtered_tasks,
        on_toggle=lambda task_id: (
            task_controller.toggle_task_completion(task_id),
            setattr(st.session_state, 'last_save_time', datetime.now()),
            st.rerun()
        ),
        on_edit=lambda task_id: (
            setattr(st.session_state, 'edit_task_id', task_id),
            st.rerun()
        ),
        on_delete=lambda task_id: (
            task_controller.delete_task(task_id),
            setattr(st.session_state, 'last_save_time', datetime.now()),
            st.rerun()
        ),
        get_color_func=category_controller.get_category_color
    )

# ARCHIV

if st.session_state.show_archived:
    ArchiveView.render_archive(
        tasks=task_controller.get_archived_tasks(),
        on_restore=lambda task_id: (
            task_controller.restore_task(task_id),
            setattr(st.session_state, 'last_save_time', datetime.now()),
            st.rerun()
        ),
        on_delete=lambda task_id: (
            task_controller.delete_task(task_id),
            setattr(st.session_state, 'last_save_time', datetime.now()),
            st.rerun()
        ),
        get_color_func=category_controller.get_category_color
    )

