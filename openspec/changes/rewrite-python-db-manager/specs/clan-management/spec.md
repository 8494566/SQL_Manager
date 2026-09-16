## ADDED Requirements

### Requirement: Max out a clan
The application SHALL support maxing out a clan's stats by name, setting the clan's spare-person/spare-num, money, exp, level, tech tiers, and popularity to their configured maximum values.

#### Scenario: Max clan by name
- **WHEN** the user enters a clan name and clicks max-clan
- **THEN** the app updates the `Clan` row matching the name, setting ClanPaySparePerson=250, ClanPaySpareNum=250, ClanSparePerson=250, ClanSpareNum=250, ClanMoney=99999999, ClanExp=99999999, ClanLevel=25, ClanTech=20, ClanTech2=20, ClanTech3=20, Popularity=99999999

#### Scenario: Requires connection
- **WHEN** the user clicks max-clan while not connected
- **THEN** the app rejects the operation with a message to connect first

### Requirement: Delete a clan
The application SHALL support deleting a clan by name using a valid parameterized `DELETE` statement, replacing the original broken SQL (`WHERE ClanName = =`).

#### Scenario: Delete clan by name
- **WHEN** the user enters a clan name and confirms delete
- **THEN** the `Clan` row matching the name is deleted
