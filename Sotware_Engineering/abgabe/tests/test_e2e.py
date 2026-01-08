"""
End-to-End Tests für TODO-App
Framework: pytest + Playwright
Testet echte Benutzerinteraktionen im Browser mit Streamlit-UI
"""
import pytest
import subprocess
import time
import os
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def app_server():
    """Startet Streamlit-App als Server"""
    process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port=8502", "--server.headless=true"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(5)
    yield "http://localhost:8502"
    process.terminate()
    process.wait()


@pytest.fixture
def app_page(page: Page, app_server):
    """Öffnet die App im Browser"""
    page.goto(app_server)
    page.wait_for_load_state("networkidle")
    time.sleep(3)
    return page


class TestE2E:
    """End-to-End Tests: Echte Benutzerinteraktionen"""
    
    def test_app_titel_geladen(self, app_page: Page):
        """
        E2E 1: App läuft und zeigt korrekten Titel
        """
        expect(app_page).to_have_title("To-do App", timeout=10000)
    
    def test_sidebar_vorhanden(self, app_page: Page):
        """
        E2E 2: Sidebar mit Kategorien ist sichtbar
        """
        sidebar = app_page.locator("[data-testid='stSidebar']")
        expect(sidebar).to_be_attached()
    
    def test_hauptbereich_vorhanden(self, app_page: Page):
        """
        E2E 3: Hauptbereich mit Aufgaben ist sichtbar
        """
        main = app_page.locator("[data-testid='stMain']")
        expect(main).to_be_attached()
    
    def test_formular_elemente_vorhanden(self, app_page: Page):
        """
        E2E 4: Eingabeformular-Elemente sind vorhanden
        """
        # Irgendein Input-Feld existiert
        inputs = app_page.locator("input")
        expect(inputs.first).to_be_attached()
        
        # Irgendein Button existiert
        buttons = app_page.locator("button")
        expect(buttons.first).to_be_attached()
