## ADDED Requirements

### Requirement: Connection form inputs
The application SHALL provide inputs for User ID, Password (masked), Initial Catalog (game DB, default `GameDB`), Data Source (server/IP), and Area database name (default `GameDBArea`).

#### Scenario: Defaults prefilled
- **WHEN** the connection panel is shown for the first time
- **THEN** User ID defaults to `sa`, Initial Catalog to `GameDB`, and Area to `GameDBArea`, with Password and Data Source empty

### Requirement: Required-field validation before connect
The application SHALL reject a connection attempt when Password or Data Source is empty and SHALL show an explanatory message.

#### Scenario: Missing password or data source
- **WHEN** the user clicks Connect with an empty Password or empty Data Source
- **THEN** the app shows a validation message and does not attempt to connect

### Requirement: Establish SQL Server connection
The application SHALL connect to SQL Server via `pyodbc` using the Microsoft ODBC Driver, applying a connection timeout, and SHALL reflect a connected state on success.

#### Scenario: Successful connect
- **WHEN** the user submits valid credentials and the server is reachable
- **THEN** the app opens a connection, marks state as connected, enables the feature panels, and shows a success message

#### Scenario: Failed connect
- **WHEN** the credentials are invalid or the server is unreachable
- **THEN** the app remains disconnected and shows the driver error message

#### Scenario: Prevent double connect
- **WHEN** the user clicks Connect while already connected
- **THEN** the app shows a message that it is already connected and does not open a second connection

### Requirement: Disconnect
The application SHALL allow the user to disconnect, closing the connection and disabling the feature panels.

#### Scenario: Disconnect closes connection
- **WHEN** the user clicks Disconnect while connected
- **THEN** the connection is closed, feature panels are disabled, and state returns to disconnected

### Requirement: Parameterized query execution
The application SHALL execute all database statements using parameterized queries (bound parameters), and SHALL NOT build SQL by interpolating raw user input.

#### Scenario: Values passed as parameters
- **WHEN** any operation runs a statement that includes user-provided values
- **THEN** those values are passed as bound parameters rather than concatenated into the SQL text

#### Scenario: Execution error surfaced
- **WHEN** a statement raises a database error
- **THEN** the operation fails safely and the error message is shown to the user
