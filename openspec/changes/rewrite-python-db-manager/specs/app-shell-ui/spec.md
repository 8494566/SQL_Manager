## ADDED Requirements

### Requirement: Application shell and window
The application SHALL launch as a Flet desktop window with a fixed title, a default size suitable for the feature panels, and a single top-level layout that hosts the connection area and the feature panels.

#### Scenario: App launches
- **WHEN** the user starts the packaged executable
- **THEN** a Flet window opens showing the connection form and the feature panels in a disabled (not-yet-connected) state

#### Scenario: Window has app identity
- **WHEN** the window is shown
- **THEN** it displays the application title and icon and is resizable within sane minimum bounds

### Requirement: Modern theming
The application SHALL provide a modern visual theme with support for light and dark modes and a user-accessible toggle, using Flet's Material theming.

#### Scenario: Toggle dark mode
- **WHEN** the user activates the theme toggle
- **THEN** the UI switches between light and dark themes without restarting and the choice persists for the session

### Requirement: Navigation between feature panels
The application SHALL organize GM features into distinct panels (connection, character, inventory, clan, account, message) reachable via navigation without losing connection state.

#### Scenario: Switch panels while connected
- **WHEN** the user is connected and navigates from the character panel to the clan panel
- **THEN** the clan panel is shown and the connection remains active

### Requirement: User feedback for actions
The application SHALL present success and error feedback for every user-triggered operation via non-blocking notifications (snackbar/toast or inline banner).

#### Scenario: Operation reports outcome
- **WHEN** any GM operation completes or fails
- **THEN** the UI shows a message describing success or the error, without a blocking modal for routine outcomes
