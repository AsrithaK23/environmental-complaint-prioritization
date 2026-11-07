
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class PriorityResult:
    priority: str
    score: int
    reasons: tuple[str, ...]

    @property
    def reason(self) -> str:
        """Combined explanation, compatible with the existing API contract."""
        return "; ".join(self.reasons)


def _rx(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


# These indicators trigger HIGH priority immediately, unless negated.
CRITICAL = {
    "fire or burning hazard": _rx(
        r"\b(fire(?!\s+(?:drill|extinguisher|alarm|exit|safety))"
        r"|flames?|burning smell|sparks?|sparking|short[- ]circuit)\b"
    ),
    "electrical hazard": _rx(
        r"\b(live wire|exposed wire|electrical shock|electric shock"
        r"|electrocut\w*)\b"
    ),
    "gas or chemical hazard": _rx(
        r"\b(gas\s+(?:leak\w*|smell)|smell\w*\s+(?:of\s+)?gas"
        r"|chemical spill|toxic fumes?|explosion)\b"
    ),
    "sewage overflow": _rx(
        r"\bsewage\W+(?:\w+\W+){0,3}(?:overflow\w*|flood\w*)"
    ),
    "unsafe drinking water": _rx(
        r"\b(?:(?:contaminated|dirty|foul|smelly)\W+"
        r"(?:\w+\W+){0,2}drinking water|drinking water\W+"
        r"(?:\w+\W+){0,3}(?:contaminat\w*|dirty|foul))\b"
    ),
    "serious injury": _rx(
        r"\b(injur\w*|fainted|unconscious|hospitali[sz]ed)\b"
    ),
}

# Non-emergency severity indicators contribute to the score.
MEDIUM = {
    "leak": _rx(r"\bleak\w*\b"),
    "blocked drain": _rx(
        r"\b(?:block|clog)\w*\W+(?:\w+\W+){0,3}drain\b"
        r"|\bdrain\w*\W+(?:\w+\W+){0,3}(?:block|clog)\w*\b"
    ),
    "overflow": _rx(r"\boverflow\w*\b"),
    "waste accumulation": _rx(
        r"\b(?:garbage|trash|waste)\W+"
        r"(?:\w+\W+){0,3}(?:pile\w*|accumulat\w*|dump\w*)\b"
    ),
    "stagnant water or mosquitoes": _rx(
        r"\b(stagnant water|mosquito\w*)\b"
    ),
    "smoke, dust, or foul smell": _rx(
        r"\b(smoke|dust\w*|foul smell|stink\w*)\b"
    ),
    "lighting fault": _rx(
        r"\bbroken\W+(?:street\s*)?light\b"
        r"|\blights?\W+(?:\w+\W+){0,2}(?:broken|not working)\b"
    ),
    "fallen tree or branch": _rx(
        r"\bfallen\s+(?:tree|branch)\b"
        r"|\bbranches?\s+(?:fell|broken)\b"
    ),
    "noise disturbance": _rx(
        r"\b(?:loud|excessive|persistent|continuous)\s+noise\b"
    ),
}

SENSITIVE_LOCATION = _rx(
    r"\b(hostel|canteen|mess|kitchen|lab|library|hospital|"
    r"medical|classroom|auditorium)\b"
)

CATEGORY_CONTEXT = {
    "Waste Management": "waste management",
    "Water / Sanitation": "water or sanitation",
    "Air Pollution": "air quality",
    "Noise Pollution": "noise disturbance",
    "Energy-related Issues": "energy or electrical",
    "Greenery / Landscaping": "greenery or landscaping",
    "Other": "other",
}


def _is_negated(text: str, match_start: int) -> bool:
    """
    Check for a nearby negation immediately before a match.
    This is a lightweight rule, not full natural-language understanding.
    """
    preceding_text = text[max(0, match_start - 60):match_start]

    return bool(
        re.search(
            r"\b(?:no|not|never|without|neither)\b"
            r"(?:\W+\w+){0,3}\W*$",
            preceding_text,
            flags=re.IGNORECASE,
        )
    )


def _find(pattern: re.Pattern, text: str) -> str | None:
    """Return the first match not immediately preceded by a negation."""
    for match in pattern.finditer(text):
        if not _is_negated(text, match.start()):
            return match.group(0)
    return None


def calculate_priority(
    category: str,
    complaint_text: str,
    affected_people: int = 1,
    repeat_count: int = 0,
    location: str = "",
    hours_open: int = 0,
) -> PriorityResult:
    """
    Calculate explainable complaint priority.

    repeat_count:
        Number of earlier distinct users' similar reports, ideally for
        the same category and location within the previous 14 days.

    affected_people:
        Estimated number of people affected.

    location:
        Complaint location, such as "Hostel Block A".

    hours_open:
        Hours since the complaint was created, if it remains unresolved.

    The caller is responsible for obtaining these values from trusted data.
    """
    if not isinstance(complaint_text, str) or not complaint_text.strip():
        raise ValueError("complaint_text must not be empty")

    if not isinstance(category, str) or not category.strip():
        raise ValueError("category must not be empty")

    if (
        isinstance(affected_people, bool)
        or not isinstance(affected_people, int)
        or affected_people < 1
    ):
        raise ValueError("affected_people must be an integer >= 1")

    if (
        isinstance(repeat_count, bool)
        or not isinstance(repeat_count, int)
        or repeat_count < 0
    ):
        raise ValueError("repeat_count must be an integer >= 0")

    if (
        isinstance(hours_open, bool)
        or not isinstance(hours_open, int)
        or hours_open < 0
    ):
        raise ValueError("hours_open must be an integer >= 0")

    text = " ".join(complaint_text.split())
    location_text = location.strip() if isinstance(location, str) else ""
    category_name = category.strip()
    context = CATEGORY_CONTEXT.get(category_name, CATEGORY_CONTEXT["Other"])

    # 1. Safety floor: recognized critical hazards immediately become HIGH.
    for label, pattern in CRITICAL.items():
        hit = _find(pattern, text)
        if hit:
            return PriorityResult(
                priority="HIGH",
                score=10,
                reasons=(f"Safety hazard: {label} ('{hit}')",),
            )

    # 2. Add points for independent indicators.
    score = 0
    reasons: list[str] = []

    severity_hits = {
        label: hit
        for label, pattern in MEDIUM.items()
        if (hit := _find(pattern, text)) is not None
    }

    if severity_hits:
        # One indicator = 2 points; two = 3; three or more = 3.
        score += min(1 + len(severity_hits), 3)
        reasons.append(
            "Severity indicators: "
            + ", ".join(
                f"{label} ('{hit}')"
                for label, hit in severity_hits.items()
            )
        )

    if repeat_count >= 2:
        score += 2
        reasons.append(f"{repeat_count} earlier similar reports")
    elif repeat_count == 1:
        score += 1
        reasons.append("1 earlier similar report")

    # Cap the counted impact to prevent unreasonable scores.
    people = min(affected_people, 50)
    if people >= 10:
        score += 2
        reasons.append(f"Approximately {people} people affected")
    elif people >= 3:
        score += 1
        reasons.append(f"Approximately {people} people affected")

    if SENSITIVE_LOCATION.search(location_text):
        score += 1
        reasons.append(f"Sensitive location: {location_text}")

    if hours_open >= 120:
        score += 2
        reasons.append("Unresolved for 5 or more days")
    elif hours_open >= 48:
        score += 1
        reasons.append("Unresolved for 2 or more days")

    # 3. Convert the score into the contract's priority labels.
    if score >= 4:
        priority = "HIGH"
    elif score >= 2:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    if not reasons:
        reasons.append("No strong severity, recurrence, or impact indicators")

    return PriorityResult(
        priority=priority,
        score=score,
        reasons=(context, *reasons),
    )
