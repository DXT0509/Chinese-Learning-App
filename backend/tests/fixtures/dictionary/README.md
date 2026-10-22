# Synthetic dictionary fixture

`cedict-test.u8` was authored for parser, importer and API tests. Its ten rows exercise
CC-CEDICT v1 syntax; it is not copied from or presented as a CC-CEDICT release. Definitions
are synthetic test labels, not learner-facing translations. This fixture is available
under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), attribution:
ChineseLearningApp test fixture contributors. The importer uses its normal source metadata
in isolated tests solely to exercise that contract. Do not import it into development or
production as a real dictionary.
