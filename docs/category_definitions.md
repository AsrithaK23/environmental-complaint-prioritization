# Environmental Complaint Category Definitions

## Purpose
Defines the standard complaint categories used across the dataset, ML model, backend, and frontend.

## Categories

| Category | Definition |
|---|---|
| **Waste Management** | Garbage accumulation, littering, overflowing bins, and improper waste disposal. |
| **Water / Sanitation** | Water leakage, blocked drains, stagnant water, and sanitation issues. |
| **Air Pollution** | Smoke, dust, fumes, and other air-quality issues. |
| **Noise Pollution** | Excessive or disturbing noise from machinery, construction, vehicles, or loudspeakers. |
| **Energy-related Issues** | Electricity wastage, faulty lighting, and inefficient energy usage. |
| **Greenery / Landscaping** | Plant damage, garden maintenance, overgrown grass, and fallen branches. |
| **Other** || **Other** | Campus infrastructure or maintenance complaints that do not fit any of the six specific categories, such as broken benches, signboards, or railings. | |

## Labelling Rules

1. Assign one primary category to each complaint based on its main issue.
2. Use the exact category names listed above.
3. For complaints involving multiple issues, label the primary concern.
4. Use **Other** only when no specific category reasonably fits.

## Team Usage

- **Person 1:** Labels and validates dataset records.
- **Person 2:** Uses the categories as ML classification labels.
- **Person 3:** Implements priority rules and department routing.
- **Person 4:** Displays categories consistently in the frontend.

**Status:** Proposed standard, subject to team agreement.