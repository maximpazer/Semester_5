# Nielsens 10 Usability-Heuristiken – Implementierung in der TODO-App

## Prinzipien & Beschreibungen

1. **Sichtbarkeit des Systemstatus:** Das System soll den Nutzer stets über den aktuellen Zustand informieren, z. B. durch Feedback beim Speichern.
2. **Übereinstimmung zwischen System und realer Welt:** Vertraute Begriffe und Symbole verwenden (z. B. 🗑 für Löschen).
3. **Benutzerkontrolle und Freiheit:** Nutzer benötigen einen „Notausgang", um Aktionen abzubrechen oder rückgängig zu machen.
4. **Konsistenz und Standards:** Einheitliche Gestaltung und Plattformkonventionen einhalten.
5. **Fehlervermeidung:** Bestätigungsdialoge vor kritischen Aktionen (z. B. Löschen) einbauen.
6. **Erkennung statt Erinnerung:** Optionen und Aktionen sichtbar machen, damit Nutzer nichts im Kopf behalten müssen.
7. **Flexibilität und Effizienz:** Für fortgeschrittene Nutzer Schnellzugriffe und Shortcuts anbieten.
8. **Ästhetisches und minimalistisches Design:** Nur relevante Informationen anzeigen, keine Ablenkung.
9. **Hilfe bei Fehlererkennung und -behebung:** Klare, verständliche Fehlermeldungen mit Lösungsvorschlägen.
10. **Hilfe und Dokumentation:** Kontextbezogene Hilfe bereitstellen, auch wenn das System intuitiv sein sollte.

---

## Konkrete Umsetzung in der TODO-App

### Prinzip 1: Sichtbarkeit des Systemstatus
**Umsetzung:** Speicherstatus wird als grünes Häkchen (💾 ✓) im Header angezeigt, sobald Daten gespeichert wurden. Die Anzeige erscheint für 5 Sekunden nach jeder Speicheraktion.

**Code-Referenz:** `LayoutView.render_header()` – Zeigt Speicher-Feedback basierend auf `last_save_time`.

---

### Prinzip 2: Übereinstimmung mit der realen Welt
**Umsetzung:** Vertraute Icons und Begriffe:
- 📅 für Fälligkeitsdaten mit relativen Angaben („heute", „morgen", „in 3 Tagen")
- 🗑 für Löschen
- ✏️ für Bearbeiten
- ➕ für Hinzufügen
- ⚠️ für überfällige Aufgaben

**Code-Referenz:** `TaskView._format_due_date()` – Formatiert Daten benutzerfreundlich.

---

### Prinzip 3: Benutzerkontrolle und Freiheit
**Umsetzung:** 
- „✖ Abbrechen"-Button im Bearbeitungsformular
- Erledigte Aufgaben können über ↩ wiederhergestellt werden
- Filter lassen sich jederzeit zurücksetzen

**Code-Referenz:** `TaskView.render_edit_form()` – Speichern und Abbrechen als gleichwertige Optionen.

---

### Prinzip 4: Konsistenz und Standards
**Umsetzung:**
- Primäre Aktionen (Speichern, Hinzufügen) verwenden `type="primary"` (blau)
- Sekundäre Aktionen (Löschen, Abbrechen) in grau
- Einheitliche Icon-Sprache durchgehend

**Code-Referenz:** Alle `st.form_submit_button()` und `st.button()` Aufrufe folgen diesem Schema.

---

### Prinzip 5: Fehlervermeidung
**Umsetzung:** Zweistufiger Löschvorgang – Erster Klick auf 🗑 aktiviert Bestätigungsmodus (❌), zweiter Klick löscht tatsächlich.

**Code-Referenz:** `TaskView._render_task_actions()` – State-basierte Löschbestätigung via `del_confirm_{id}`.

---

### Prinzip 6: Erkennung statt Erinnerung
**Umsetzung:**
- Platzhalter im Eingabefeld: „Was möchten Sie erledigen?"
- Kategorien als Dropdown mit allen verfügbaren Optionen
- Metadaten (Kategorie, Datum) direkt bei jeder Aufgabe sichtbar

**Code-Referenz:** `TaskView.render_task_form()` – Platzhalter und Dropdowns reduzieren Gedächtnislast.

---

### Prinzip 7: Flexibilität und Effizienz
**Umsetzung:**
- Kompaktes einzeiliges Eingabeformular für schnelles Anlegen
- Filter für Status und Kategorie in der Sidebar
- Archiv-Toggle für fortgeschrittene Nutzung

**Code-Referenz:** `SidebarView.render_filters()` und `SidebarView.render_toggles()`.

---

### Prinzip 8: Ästhetisches und minimalistisches Design
**Umsetzung:**
- Max. 800px Breite für fokussierte Darstellung
- Reduziertes CSS ohne visuelle Ablenkung
- Leerzustand: „📝 Keine Aufgaben vorhanden" – klar und dezent

**Code-Referenz:** `LayoutView.apply_responsive_css()` – Minimalistisches Styling.

---

### Prinzip 9: Hilfe bei Fehlererkennung
**Umsetzung:** Spezifische Fehlermeldungen:
- „Titel erforderlich." bei leerem Titel
- „Bitte Namen eingeben" bei leerer Kategorie
- Farbliche Hervorhebung (rot) für überfällige/dringende Aufgaben

**Code-Referenz:** Validierung in `app.py` und `CategoryView._render_add_category_form()`.

---

### Prinzip 10: Hilfe und Dokumentation
**Umsetzung:** Hilfe-Toggle in der Sidebar blendet Kurzanleitung ein:
„Aufgabe eingeben → Kategorie/Datum optional → ➕ klicken. Abhaken verschiebt ins Archiv."

**Code-Referenz:** `LayoutView.render_help()` – Kompakte, kontextbezogene Anleitung.



