## ADDED Requirements

### Requirement: Create a game account
The application SHALL support creating a new account in the Area database's `account` table. It SHALL reject creation when the UserName already exists, and SHALL store the password (and security password) as a SQL Server SHA1 hex hash.

#### Scenario: Create new account
- **WHEN** the user enters a new UserName and password and clicks create
- **THEN** the app verifies the UserName does not exist in `<Area>..account`, then inserts a new account row whose `PassWord` and `SecPsw` are computed as `substring(sys.fn_VarBinToHexStr(hashbytes('SHA1', ?)), 3, 128)` and whose remaining fields use the established defaults

#### Scenario: Duplicate account name
- **WHEN** the entered UserName already exists
- **THEN** the app shows a "name already taken" message and does not insert

### Requirement: Change an account password
The application SHALL support changing an existing account's password in the Area database, verifying the account exists first, and hashing the new password with the same SHA1 hex formula.

#### Scenario: Change password
- **WHEN** the user enters an existing UserName and a new password and clicks change
- **THEN** the app verifies the account exists, then updates `PassWord` to `substring(sys.fn_VarBinToHexStr(hashbytes('SHA1', ?)), 3, 128)`

#### Scenario: Account does not exist
- **WHEN** the entered UserName does not exist in `<Area>..account`
- **THEN** the app shows a "no such account" message and does not update
