# TODO Application – Software Engineering Project

## 1. Project Overview
This project implements a cross-platform TODO application developed according to
Software Engineering best practices, including Requirements Engineering (SMART),
MVC architecture, and established design patterns.

The goal is to design, implement, and document a maintainable system that fulfills
both functional and non-functional requirements.


## 2. Requirements Engineering

All requirements are formulated according to the **SMART principle**
(Specific, Measurable, Accepted, Realistic, Timely) and are uniquely identifiable
to ensure full traceability throughout the project lifecycle.

### 2.1 Functional Requirements

Functional requirements describe **what** the system must do.
At least five MUST requirements are fully implemented.

| ID     | Description                                                                 | Priority |
|--------|------------------------------------------------------------------------------|----------|
| FR-01  | The system must store tasks persistently so data is not lost on restart.     | MUSS     |
| FR-02  | The system must allow the user to delete existing TODO items.                | MUSS     |
| FR-03  | The system must allow the user to edit the content of existing TODO items.   | MUSS     |
| FR-04  | The system must enable marking tasks as completed or open.                  | MUSS     |
| FR-05  | The system must display all TODO items in a clear list format.               | MUSS     |
| FR-06  | The user should be able to create and manage up to five categories.          | SOLL     |
| FR-07  | The system should allow filtering tasks by status.                           | SOLL     |
| FR-08  | Tasks can include a due date selected via a calendar picker (< 3 clicks).   | KANN     |


### 2.2 Non-Functional Requirements

Non-functional requirements describe **how well** the system performs,
based on ISO/IEC 25010 quality characteristics.

| ID      | Category       | Description                                                             | Priority |
|---------|---------------|-------------------------------------------------------------------------|----------|
| NFR-01  | Performance   | A new task can be created in under 5 seconds.                          | MUSS     |
| NFR-02  | Usability     | The UI adheres to Nielsen’s 10 Usability Heuristics.                    | MUSS     |
| NFR-03  | Performance   | The system reacts to user input within 200–300 ms.                     | MUSS     |
| NFR-04  | Security      | Passwords (if used) are stored using a secure hashing algorithm.       | SOLL     |
| NFR-05  | Compatibility | The application supports cross-platform execution.                    | MUSS     |
| NFR-06  | Reliability   | The application ensures 99.5% monthly availability.                   | SOLL     |



## 3. Architecture & Quality Constraints

### 3.1 MVC Architecture
The system strictly follows the Model-View-Controller (MVC) pattern:

- Model: Task, Category, Persistence Logic
- View: UI Components (Task List, Editor, Filters)
- Controller: User interactions and business logic coordination

This separation improves maintainability and testability.


### 3.2 Design Patterns

The following design patterns are implemented:

- Factory Pattern: Creation of Task objects
- Abstract Factory Pattern: Platform-specific UI components
- Adapter Pattern: Integration of persistence mechanisms (e.g. local storage vs DB)


## 4. Usability Traceability (Nielsen)

Each usability heuristic is explicitly mapped to UI elements.

| Heuristic | Implementation Example |
|----------|------------------------
