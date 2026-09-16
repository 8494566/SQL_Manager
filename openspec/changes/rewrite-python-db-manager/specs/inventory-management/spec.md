## ADDED Requirements

### Requirement: Predefined class item-set fills
The application SHALL support applying predefined item-set blobs to a bound character's inventory container. Each preset targets a specific container (6 or 7) and job/class, replacing that container's contents. The blob payloads SHALL be extracted verbatim from the original source into Python data assets.

#### Scenario: Apply a class item set
- **WHEN** the user selects a class preset (e.g. a 4-class/5-class/2-class job) for a bound character
- **THEN** the app deletes existing `Goods` rows for that character and container, then inserts a `Goods` row with the preset's `GoodsBuf` blob and `GoodsNum` for that container

#### Scenario: Requires bound character
- **WHEN** the user applies a preset without a bound character
- **THEN** the app rejects the operation with a message to bind first

### Requirement: Copy equipment blob from a character
The application SHALL support reading the bound character's equipment blob (`GoodsBuf`) and quantity (`GoodsNum`) from container 7 into an in-app clipboard.

#### Scenario: Copy equipment
- **WHEN** the user clicks copy-equipment for a bound character
- **THEN** the app reads `GoodsBuf` and `GoodsNum` from `Goods` for that character and container 7 and stores them in memory

#### Scenario: Nothing to copy
- **WHEN** the character has no equipment row in container 7
- **THEN** the app shows a message that there is nothing to copy

### Requirement: Paste equipment blob to a character
The application SHALL support writing the previously copied equipment blob back to a bound character's container 7.

#### Scenario: Paste equipment
- **WHEN** the user clicks paste-equipment for a bound character after a successful copy
- **THEN** the app deletes existing container-7 `Goods` rows for that character and inserts a row with the copied `GoodsBuf` and `GoodsNum`

#### Scenario: Paste without prior copy
- **WHEN** the user clicks paste-equipment with no blob copied
- **THEN** the app shows a message that there is nothing to paste
