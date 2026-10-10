
import csv
import random
from pathlib import Path

SEED = 42
random.seed(SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_FILE = PROJECT_ROOT / "dataset" / "raw" / "complaints_raw.csv"

# Each category contains several interchangeable phrases.
# These are synthetic examples, not real campus complaints.
COMPLAINT_PATTERNS = {
    "Waste Management": [
        "Garbage has accumulated near {place} and has not been collected.",
        "The dustbin at {place} is overflowing.",
        "Plastic wrappers and food waste are scattered around {place}.",
        "Waste is being dumped beside {place}.",
        "The waste collection area near {place} smells unpleasant.",
        "The bins near {place} have not been emptied for several days.",
        "Litter is spreading around {place} after lunch.",
        "Food waste has been left unattended near {place}.",
        "There are no usable waste bins near {place}.",
        "Mixed garbage is piling up outside {place}.",
        "Waste is attracting flies near {place}.",
        "The garbage collection point at {place} needs attention.",
    ],
    "Water / Sanitation": [
        "A water tap is leaking near {place}.",
        "Water is stagnating beside {place}.",
        "The drain near {place} is blocked.",
        "There is an unpleasant sewage smell around {place}.",
        "The washroom near {place} requires cleaning.",
        "Water is being wasted because a tap near {place} will not close.",
        "The drinking water area near {place} is dirty.",
        "A pipe appears to be leaking beside {place}.",
        "The drain near {place} is overflowing.",
        "There is standing water near {place} after cleaning.",
        "The washbasins at {place} are not draining properly.",
        "The sanitation facilities near {place} need maintenance.",
    ],
    "Air Pollution": [
        "Smoke is spreading across {place}.",
        "Dust from nearby work is affecting the air around {place}.",
        "Someone is burning waste near {place}.",
        "The air around {place} smells strongly of fumes.",
        "Dust clouds are entering {place} during construction.",
        "Exhaust fumes are collecting near {place}.",
        "Burning leaves are producing smoke near {place}.",
        "The air quality around {place} seems poor because of dust.",
        "A smoky smell is coming from the area beside {place}.",
        "Dust is spreading from the road near {place}.",
        "Fumes from equipment are affecting {place}.",
        "Waste burning near {place} is causing air pollution.",
    ],
    "Noise Pollution": [
        "Loud machinery is disturbing people near {place}.",
        "Construction noise can be heard inside {place}.",
        "Excessive honking is disturbing the area around {place}.",
        "Loudspeakers near {place} are being used at high volume.",
        "Continuous drilling noise is coming from beside {place}.",
        "Generator noise is disturbing people near {place}.",
        "Loud music is disturbing the surroundings of {place}.",
        "The noise from maintenance work near {place} is excessive.",
        "Vehicles are creating excessive noise near {place}.",
        "A machine near {place} is making a very loud sound.",
        "Repeated loud announcements are disturbing {place}.",
        "Noise from nearby work is affecting the quiet environment at {place}.",
    ],
    "Energy-related Issues": [
        "Lights are remaining switched on in the empty {place}.",
        "A corridor light near {place} is not working.",
        "Fans are running in an unoccupied {place}.",
        "Electricity appears to be wasted near {place}.",
        "The outdoor lights near {place} remain on during daylight.",
        "A faulty light is flickering near {place}.",
        "The lights in {place} are not turning off.",
        "An electrical fitting near {place} needs maintenance.",
        "Air conditioning is running in an empty {place}.",
        "Several lights near {place} are damaged.",
        "The lighting system near {place} is consuming energy unnecessarily.",
        "A switch near {place} does not control the lights properly.",
    ],
    "Greenery / Landscaping": [
        "Plants near {place} are drying out and need watering.",
        "The garden beside {place} is poorly maintained.",
        "Broken branches are lying near {place}.",
        "The grass around {place} has become overgrown.",
        "Plants near {place} have been damaged.",
        "The trees around {place} need maintenance.",
        "Garden waste has been left near {place}.",
        "The landscaped area at {place} is full of weeds.",
        "A damaged plant bed near {place} needs attention.",
        "The plants around {place} are not being maintained.",
        "Leaves and branches are blocking the walkway near {place}.",
        "The green space near {place} requires cleaning and care.",
    ],
    "Other": [
        "An environmental issue was noticed near {place} but its category is unclear.",
        "The surroundings of {place} need an environmental inspection.",
        "There is an unusual environmental concern near {place}.",
        "The area near {place} requires a general environmental review.",
        "An unidentified environmental problem has been reported at {place}.",
        "The environmental condition around {place} needs attention.",
        "A concern about the campus environment has been raised near {place}.",
        "Please inspect the surroundings of {place} for an environmental issue.",
        "An environmental maintenance concern was noticed at {place}.",
        "The campus environment near {place} may require further assessment.",
        "There is an unresolved environmental concern around {place}.",
        "Please review an unspecified environmental issue at {place}.",
    ],
}

PLACES = [
    "the main block", "the library", "the canteen",
    "the science laboratory", "the parking area", "the hostel",
    "the auditorium", "the sports ground", "the main entrance",
    "the second-floor corridor", "the garden", "the workshop",
    "the classroom block", "the bus stop", "the back gate",
    "the administration office", "the washroom", "the courtyard",
    "the water station", "the campus road",
]


def generate_rows():
    rows = []
    complaint_number = 1

    for category, patterns in COMPLAINT_PATTERNS.items():
        # 12 patterns x 20 locations = 240 potential combinations,
        # sample 120 unique combinations per category.
        combinations = [
            (pattern, place)
            for pattern in patterns
            for place in PLACES
        ]
        selected = random.sample(combinations, 120)

        for pattern, place in selected:
            rows.append({
                "complaint_id": f"SYN-{complaint_number:04d}",
                "complaint_text": pattern.format(place=place),
                "category": category,
                "source_type": "synthetic",
            })
            complaint_number += 1

    random.shuffle(rows)
    return rows


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    rows = generate_rows()

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "complaint_id",
                "complaint_text",
                "category",
                "source_type",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Dataset created: {OUTPUT_FILE}")
    print(f"Total examples: {len(rows)}")
    print("\nCategory counts:")

    counts = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1

    for category, count in sorted(counts.items()):
        print(f"  {category}: {count}")

    print("\nReminder: these are synthetic examples.")
    print("Review label quality and wording before ML training.")


if __name__ == "__main__":
    main()
