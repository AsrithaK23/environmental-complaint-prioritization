
from ml.predict import predict_complaint


AMBIGUOUS_COMPLAINTS = [
    {
        "id": 1,
        "text": (
            "Due to construction there is lot of dust near BSN "
            "and also the noise is disturbing."
        ),
        "possible_categories": ["Air Pollution", "Noise Pollution"],
    },
    {
        "id": 2,
        "text": (
            "Garbage is overflowing near the hostel and the smell "
            "is making the surrounding air unpleasant."
        ),
        "possible_categories": ["Waste Management", "Air Pollution"],
    },
    {
        "id": 3,
        "text": (
            "There is a water leak near the canteen, making the "
            "path slippery and causing a foul smell."
        ),
        "possible_categories": ["Water / Sanitation", "Other"],
    },
    {
        "id": 4,
        "text": (
            "The generator near the library is very noisy and "
            "produces smoke."
        ),
        "possible_categories": ["Noise Pollution", "Air Pollution"],
    },
    {
        "id": 5,
        "text": (
            "Tree branches are blocking the pathway and the "
            "nearby streetlight is not working."
        ),
        "possible_categories": [
            "Greenery / Landscaping",
            "Energy-related Issues",
        ],
    },
    {
        "id": 6,
        "text": (
            "Construction vehicles create dust and loud noise "
            "near the main gate every morning."
        ),
        "possible_categories": ["Air Pollution", "Noise Pollution"],
    },
    {
        "id": 7,
        "text": (
            "Wastewater is flowing beside the garbage collection "
            "area and creating a bad smell."
        ),
        "possible_categories": [
            "Water / Sanitation",
            "Waste Management",
        ],
    },
]


def main():
    print("\nAMBIGUOUS COMPLAINT EVALUATION")
    print("=" * 70)

    for item in AMBIGUOUS_COMPLAINTS:
        result = predict_complaint(item["text"])

        print(f"\nTest {item['id']}: {item['text']}")
        print(f"Possible categories: {item['possible_categories']}")
        print(f"Predicted primary category: {result['category']}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Needs review: {result['needs_review']}")

        print("Explanation:")
        explanations = result.get("explanation", [])
        if explanations:
            for feature in explanations:
                print(
                    f"  - {feature['term']}: "
                    f"{feature['contribution']}"
                )
        else:
            print("  No influential matched terms found.")

        print("Suggested next step:")
        print(result.get("suggested_next_step", "Not available"))

        if result["category"] not in item["possible_categories"]:
            print(
                "CHECK: Prediction is outside the listed "
                "plausible categories. Review it manually."
            )

        print("-" * 70)


if __name__ == "__main__":
    main()
