"""Ordered candidates and actual selections shared by the TUI and web view."""

from jev_router_demo.labels import FIELDS, candidate_label
from jev_router_demo.routers.systemone import QUESTIONS


def selected_value(decision, field):
    if decision is None:
        return None
    value = getattr(decision, field)
    return str(value).lower() if isinstance(value, bool) else value


def decision_rows(results):
    rows = []
    for field, label in FIELDS.items():
        routers, selections = {}, []
        for name in ("LLM", "JEV"):
            result = results.get(name)
            selected = selected_value(result.decision, field) if result else None
            selections.append(selected)
            probabilities = ((result.probabilities or {}).get(field, {}) if result else {})
            routers[name] = [
                {"value": value, "label": candidate_label(field, value),
                 "selected": value == selected, "probability": probabilities.get(value)}
                for value in QUESTIONS[field]["criteria"]
            ]
        rows.append({"field": field, "label": label, "routers": routers,
                     "different": all(value is not None for value in selections) and selections[0] != selections[1]})
    return rows
