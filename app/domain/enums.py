from __future__ import annotations

from enum import Enum
from typing import Dict, Tuple, Union


class ComponentType(str, Enum):
    energy_supply = "energy_supply"
    battery_optimization = "battery_optimization"
    heatpump_optimization = "heatpump_optimization"


class EventAction(str, Enum):
    start = "start"
    end = "end"


class EventType(str, Enum):
    supply_energy_start = "supply_energy_start"
    supply_energy_end = "supply_energy_end"
    battery_optimization_start = "battery_optimization_start"
    battery_optimization_end = "battery_optimization_end"
    heatpump_optimization_start = "heatpump_optimization_start"
    heatpump_optimization_end = "heatpump_optimization_end"


# Mapping from event type to (component, action)
EVENT_TYPE_TO_COMPONENT_ACTION: Dict[EventType, Tuple[ComponentType, EventAction]] = {
    EventType.supply_energy_start: (
        ComponentType.energy_supply,
        EventAction.start,
    ),
    EventType.supply_energy_end: (
        ComponentType.energy_supply,
        EventAction.end,
    ),
    EventType.battery_optimization_start: (
        ComponentType.battery_optimization,
        EventAction.start,
    ),
    EventType.battery_optimization_end: (
        ComponentType.battery_optimization,
        EventAction.end,
    ),
    EventType.heatpump_optimization_start: (
        ComponentType.heatpump_optimization,
        EventAction.start,
    ),
    EventType.heatpump_optimization_end: (
        ComponentType.heatpump_optimization,
        EventAction.end,
    ),
}


def resolve_component_action(
    event_type: Union[str, EventType],
) -> Tuple[ComponentType, EventAction]:
    """
    Given an event type, return the associated (component, action).
    Raises KeyError if the event type is unsupported.
    """
    if isinstance(event_type, str):
        try:
            et = EventType(event_type)
        except ValueError as exc:
            raise KeyError(f"Unsupported event type: {event_type}") from exc
    else:
        et = event_type
    return EVENT_TYPE_TO_COMPONENT_ACTION[et]


