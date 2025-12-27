# Nielsen's 10 Usability Heuristics - Implementierung in TODO-App

## Prinzipien & Beschreibungen

1. Visibility of system status: The system should always keep users informed about what is going on through appropriate feedback within a reasonable time. In your app, this could be a loading spinner or a progress bar while tasks are being saved.
2. Match between system and the real world: The system should speak the users' language with words, phrases, and concepts familiar to them. For example, use a trash can icon for deleting items, as it matches a real-world action.
3. User control and freedom: Users often choose functions by mistake and need a clearly marked "emergency exit" to leave the unwanted state. This includes the ability to cancel an action or undo a deletion.
4. Consistency and standards: Users should not have to wonder whether different words, situations, or actions mean the same thing. You should follow platform conventions, such as using greyed-out buttons to indicate they are disabled.
5. Error prevention: Even better than good error messages is a careful design which prevents a problem from occurring in the first place. For your app, this might involve a confirmation dialogue before a user sends a transaction or deletes all tasks.
6. Recognition rather than recall: Minimize the user's memory load by making objects, actions, and options visible. The user should not have to remember information from one part of the dialogue to another.
7. Flexibility and efficiency of use: Accelerators—unseen by the novice user—may often speed up the interaction for the expert user. Common examples are keyboard shortcuts (like Ctrl+C or Ctrl+V) or "power-user" features.
8. Aesthetic and minimalist design: Dialogues should not contain information which is irrelevant or rarely needed. Keep your TODO app interface clean and focused only on essential task information.
9. Help users recognise, diagnose, and recover from errors: Error messages should be expressed in plain language, precisely indicate the problem, and constructively suggest a solution. Instead of an "Error 404," provide a message explaining why a password is too short and how to fix it.
10. Help and documentation: Even though it is better if the system can be used without documentation, it may be necessary to provide help that is easy to search and focused on the user's task. This could be a small "How-to" section in your sidebar.

---

## Konkrete Änderungen in der TODO-App

### Prinzip 1: Visibility of System Status
**Änderung:** Automatischer Speicherstatus wird als grüne Erfolgsmeldung ("✅ Automatisch gespeichert") oben im Interface angezeigt, wenn Daten gespeichert wurden (innerhalb von 3 Sekunden nach Speichervorgang sichtbar).

**Unterstütztes Prinzip:** Nutzer erhalten sofortiges visuelles Feedback, dass ihre Aktion erfolgreich war und Daten persistent gespeichert wurden.

---

### Prinzip 2: Match Between System and Real World
**Änderung:** Icons vor Labels hinzugefügt (🏷️ Kategorie, 📅 Fälligkeitsdatum, 🗑️ Löschen) und verständliche Real-World-Metaphern verwendet.

**Unterstütztes Prinzip:** Nutzer erkennen Funktionen durch vertraute Symbole und Begriffe aus der realen Welt, keine technischen Abstraktionen.

---

### Prinzip 3: User Control and Freedom
**Änderung:** Klarer "❌ Abbrechen"-Button beim Bearbeiten mit Bestätigungsnachricht ("Bearbeitung abgebrochen. Keine Änderungen gespeichert"), die den Nutzer informiert.

**Unterstütztes Prinzip:** Nutzer können jederzeit aus Aktionen aussteigen ohne Datenverlust und erhalten eine klare Bestätigung der Aktion.

---

### Prinzip 4: Consistency and Standards
**Änderung:** Primäre Aktionen (Speichern, Hinzufügen) nutzen konsistent den blauen `type="primary"` Button-Style, sekundäre Aktionen (Löschen, Abbrechen) nutzen grauen Standard-/Secondary-Style.

**Unterstütztes Prinzip:** Einheitliche visuelle Hierarchie macht Hauptaktionen sofort erkennbar und folgt Standard-UI-Konventionen.

---

### Prinzip 5: Error Prevention
**Änderung:** Bestätigungsdialog ("Wirklich löschen?" mit Ja/Nein-Buttons) vor dem Löschen jeder Aufgabe implementiert.

**Unterstütztes Prinzip:** Verhindert versehentliches Löschen wichtiger Daten durch vorgelagertes Sicherheitsnetz.

---

### Prinzip 6: Recognition Rather Than Recall
**Änderung:** Erweiterte Platzhalter-Texte ("z.B. Präsentation vorbereiten, Einkaufen gehen...") und Hilfe-Tooltips bei allen Eingabefeldern hinzugefügt.

**Unterstütztes Prinzip:** Nutzer müssen sich nicht erinnern, was einzugeben ist – Beispiele und Hilfe zeigen es direkt im Kontext.

---

### Prinzip 7: Flexibility and Efficiency of Use
**Änderung:** "🔄 Neu laden"-Button im Footer für schnellen Zugriff und primäre Buttons mit voller Breite (`use_container_width=True`) für effiziente Touch-/Klick-Bedienung.

**Unterstütztes Prinzip:** Power-User können schneller arbeiten durch prominente Aktions-Buttons und Schnellzugriff-Features.

---

### Prinzip 8: Aesthetic and Minimalist Design
**Änderung:** Reduzierter Footer mit nur essentiellen Informationen und klare Leerzustand-Nachricht mit Icon ("📝 Keine Aufgaben vorhanden. Erstellen Sie oben Ihre erste Aufgabe!").

**Unterstütztes Prinzip:** Interface bleibt fokussiert auf wesentliche Informationen, keine ablenkenden oder irrelevanten Details.

---

### Prinzip 9: Help Users Recognise, Diagnose, and Recover from Errors
**Änderung:** Spezifische Fehlermeldungen wie "❌ Fehler: Der Titel darf nicht leer sein. Bitte geben Sie einen Titel ein." statt generischer Meldungen implementiert.

**Unterstütztes Prinzip:** Nutzer verstehen sofort, was falsch ist und wie sie es beheben können – klare Sprache und konstruktive Lösungsvorschläge.

---

### Prinzip 10: Help and Documentation
**Änderung:** "❓ Hilfe anzeigen"-Checkbox in der Sidebar mit kontextsensitiven Schritt-für-Schritt-Anleitungen (z.B. "So erstellen Sie eine Aufgabe: 1. Titel eingeben, 2. Kategorie wählen...").

**Unterstütztes Prinzip:** Hilfe ist verfügbar, aber nicht aufdringlich, und wird direkt am relevanten Ort angezeigt – fokussiert auf die aktuelle Nutzer-Aufgabe.


