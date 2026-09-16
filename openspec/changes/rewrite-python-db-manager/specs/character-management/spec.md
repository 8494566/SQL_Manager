## ADDED Requirements

### Requirement: Bind a character before editing
The application SHALL require a character to be bound before any character edit operation, and SHALL support binding by exact ActorName or by numeric ActorID. Binding SHALL load and cache the character's current stats.

#### Scenario: Bind by name
- **WHEN** the user enters an ActorName and clicks Bind
- **THEN** the app queries the `Actor` row by name and caches point, HoldMoney, ExploitAll, ExploitLevel, CampID, Sex, ActorID, ShoppingMoney

#### Scenario: Bind by ID
- **WHEN** the user enters a numeric ActorID and clicks Bind
- **THEN** the app queries the `Actor` row by ActorID and caches the same stats

#### Scenario: Character not found
- **WHEN** the bind lookup returns no row
- **THEN** the app shows a "character not found" message and does not enter a bound state

#### Scenario: Edit blocked without binding
- **WHEN** the user triggers any edit operation while no character is bound
- **THEN** the app rejects the operation with a message to bind a character first

### Requirement: Add points and gold using current value
The application SHALL support adding an amount to the bound character's `point` and `HoldMoney`, computed from the currently stored database value (re-read at operation time), and SHALL write the new absolute total.

#### Scenario: Add points
- **WHEN** the user enters an amount and clicks add-points
- **THEN** the app sets `Actor.point` to current-value + amount for the bound character

#### Scenario: Add gold
- **WHEN** the user enters an amount and clicks add-gold
- **THEN** the app sets `Actor.HoldMoney` to current-value + amount for the bound character

### Requirement: Fill gold and shopping money
The application SHALL support setting the bound character's `HoldMoney` and `ShoppingMoney` to the maximum fill value (99999999).

#### Scenario: Max gold
- **WHEN** the user clicks fill-gold
- **THEN** `Actor.HoldMoney` is set to 99999999 for the bound character

#### Scenario: Max shopping money
- **WHEN** the user clicks fill-shopping
- **THEN** `Actor.ShoppingMoney` is set to 99999999 for the bound character

### Requirement: Add experience with overflow guard
The application SHALL support adding experience to `ExploitAll`, and SHALL clamp the result to a safe 32-bit-range value (2130000000) if the computed value overflows or goes negative.

#### Scenario: Add exp normally
- **WHEN** the user enters an amount and clicks add-exp
- **THEN** `Actor.ExploitAll` is set to current-value + amount

#### Scenario: Overflow clamp
- **WHEN** the computed experience is negative (overflow)
- **THEN** `Actor.ExploitAll` is set to 2130000000

### Requirement: Set level
The application SHALL support setting `ExploitLevel` to a user-provided value for the bound character.

#### Scenario: Set level
- **WHEN** the user enters a level and clicks set-level
- **THEN** `Actor.ExploitLevel` is set to the entered value

### Requirement: Rename character
The application SHALL support renaming the bound character's `ActorName`.

#### Scenario: Rename
- **WHEN** the user enters a new name and clicks rename
- **THEN** `Actor.ActorName` is updated for the bound character

### Requirement: Set camp and sex
The application SHALL support setting `CampID` and `Sex` from a two-value selection (1 or 2).

#### Scenario: Set camp
- **WHEN** the user selects a camp value and clicks set-camp
- **THEN** `Actor.CampID` is set to the selected value (1 or 2)

#### Scenario: Set sex
- **WHEN** the user selects a sex value and clicks set-sex
- **THEN** `Actor.Sex` is set to the selected value (1 or 2)

### Requirement: Reset clan membership
The application SHALL support resetting the bound character's `ClanID` to 0 to fix stuck-in-clan issues.

#### Scenario: Reset clan id
- **WHEN** the user clicks reset-clan
- **THEN** `Actor.ClanID` is set to 0 for the bound character

### Requirement: Delete character
The application SHALL support deleting the bound character by name using a valid parameterized `DELETE` statement, replacing the original broken SQL.

#### Scenario: Delete by name
- **WHEN** the user confirms delete for the bound character
- **THEN** the `Actor` row matching the name is deleted

### Requirement: Transfer character to another account
The application SHALL support moving a character to another account by resolving the target account's UserID from the Area account table by UserName, then updating the character's owning user-id column. The user-id column name SHALL be configurable to correct the original `UsreID` typo.

#### Scenario: Transfer to existing account
- **WHEN** the user provides a target account name and the bound character
- **THEN** the app resolves the account UserID from `<Area>..account` by UserName and updates the character's owner user-id to that UserID

#### Scenario: Target account missing
- **WHEN** the target account name does not exist
- **THEN** the app shows an error and does not modify the character

### Requirement: View character stat summary
The application SHALL provide a read-only summary of the bound character's key stats (point, level, gold, exp, ActorID) with camp and sex rendered as human-readable labels.

#### Scenario: Show summary
- **WHEN** the user opens the message/summary view for a bound character
- **THEN** the app displays the cached stats with CampID 1 shown as one faction label and otherwise the other, and Sex 1 as one label and otherwise the other
