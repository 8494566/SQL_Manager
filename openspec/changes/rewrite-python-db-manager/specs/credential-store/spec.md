## ADDED Requirements

### Requirement: Remember connection securely
The application SHALL offer an opt-in "remember me" that stores the last connection secrets (at least Data Source and Password, optionally User ID/Catalog/Area) in a local, encrypted file, and SHALL NOT use the Windows registry or store secrets in plaintext.

#### Scenario: Save on opt-in connect
- **WHEN** the user enables "remember me" and connects successfully
- **THEN** the connection secrets are written to a local encrypted store

#### Scenario: Prefill from store
- **WHEN** the app starts and a saved store exists
- **THEN** the connection form is prefilled from the decrypted store and "remember me" is shown as enabled

### Requirement: Clear stored credentials
The application SHALL allow the user to disable "remember me", which SHALL delete the stored credentials.

#### Scenario: Disable clears store
- **WHEN** the user disables "remember me"
- **THEN** the local encrypted store is deleted and no secrets remain on disk

### Requirement: No plaintext secrets on disk
The application SHALL never persist passwords in plaintext or in the Windows registry.

#### Scenario: Store is encrypted
- **WHEN** credentials are persisted
- **THEN** the on-disk representation is encrypted and unreadable as plaintext
