from dataclasses import dataclass
from typing import List, Dict, Any, Protocol


# ===== 1. Core Data Structures =====

@dataclass
class State:
    """Current situation (TASL input)."""
    danger_level: int
    enemy_detected: bool
    resources_low: bool


@dataclass
class ActionScenario:
    """Human-defined action scenario (TASL unit)."""
    name: str          # e.g., "escape"
    description: str   # natural language purpose (What)
    category: str      # abstract category, e.g., "Act", "Explore"


@dataclass
class DecisionResult:
    """Scenario selection result (TASL output)."""
    selected: ActionScenario
    considered: List[ActionScenario]
    reason: str        # transparent selection reason


# ===== 2. Action Scenario List (Human-defined, variable content) =====

SCENARIOS: List[ActionScenario] = [
    ActionScenario(
        name="escape",
        description="Move to a safer area to reduce immediate danger.",
        category="ActOnEnvironment",
    ),
    ActionScenario(
        name="scan",
        description="Scan surroundings to gather information about potential threats.",
        category="AcquireInformation",
    ),
    ActionScenario(
        name="explore",
        description="Explore the area to discover new locations or resources.",
        category="Explore",
    ),
]


# ===== 3. Scenario Selector (Transparent, Rule-Based) =====

def rule_based_selector(state: State, scenarios: List[ActionScenario]) -> DecisionResult:
    """
    Minimal transparent decision algorithm:
    - If danger is high -> escape
    - Else if enemy detected -> scan
    - Else -> explore
    """
    by_name: Dict[str, ActionScenario] = {s.name: s for s in scenarios}

    if state.danger_level >= 7:
        selected = by_name["escape"]
        reason = (
            f"Danger level is high ({state.danger_level} >= 7), "
            f"so scenario 'escape' is selected."
        )
    elif state.enemy_detected:
        selected = by_name["scan"]
        reason = (
            "Enemy is detected, so scenario 'scan' is selected "
            "to gather more information."
        )
    else:
        selected = by_name["explore"]
        reason = (
            "No high danger and no enemy detected, "
            "so scenario 'explore' is selected."
        )

    return DecisionResult(
        selected=selected,
        considered=scenarios,
        reason=reason,
    )


# ===== 4. ReAct Executor (1-to-1, Black-Box Stubs) =====

class ReActAgent(Protocol):
    """Interface for scenario-specific ReAct Agents (black-box)."""
    def run(self, state: State, scenario: ActionScenario) -> Dict[str, Any]:
        ...


class EscapeAgent:
    def run(self, state: State, scenario: ActionScenario) -> Dict[str, Any]:
        # Black-box stub: internal reasoning is intentionally opaque
        return {
            "scenario": scenario.name,
            "description": scenario.description,
            "result": "[Stub] Executed EscapeAgent.",
        }


class ScanAgent:
    def run(self, state: State, scenario: ActionScenario) -> Dict[str, Any]:
        return {
            "scenario": scenario.name,
            "description": scenario.description,
            "result": "[Stub] Executed ScanAgent.",
        }


class ExploreAgent:
    def run(self, state: State, scenario: ActionScenario) -> Dict[str, Any]:
        return {
            "scenario": scenario.name,
            "description": scenario.description,
            "result": "[Stub] Executed ExploreAgent.",
        }


# Scenario → ReActAgent (1-to-1 mapping)
AGENT_REGISTRY: Dict[str, ReActAgent] = {
    "escape": EscapeAgent(),
    "scan": ScanAgent(),
    "explore": ExploreAgent(),
}


def react_executor(state: State, scenario: ActionScenario) -> Dict[str, Any]:
    """
    ReAct Executor: dispatches to the scenario-specific ReActAgent.
    Internal behavior is treated as a black box.
    """
    agent = AGENT_REGISTRY[scenario.name]
    return agent.run(state, scenario)


# ===== 5. Trace Logger (Transparency Log) =====

def trace_logger(
    state: State,
    decision: DecisionResult,
    exec_result: Dict[str, Any],
) -> None:
    print("=== TORA / TASL Transparency Trace ===")
    print(f"State: {state.__dict__}")
    print(f"Selected Scenario: {decision.selected.name}")
    print(f"Selected Description: {decision.selected.description}")
    print(f"Reason (Selection): {decision.reason}")
    print("Considered Scenarios:", [s.name for s in decision.considered])
    print(f"ReAct Executor Scenario: {exec_result['scenario']}")
    print(f"ReAct Executor Result: {exec_result['result']}")
    print("======================================\n")


# ===== 6. End-to-End TORA Flow =====

def run_tora(state: State) -> Dict[str, Any]:
    """
    End-to-end minimal TORA flow:
    1. Scenario enumeration (Action Scenario List)
    2. Transparent selection (Scenario Selector)
    3. Black-box execution (ReAct Executor)
    4. Transparency logging (Trace Logger)
    """
    decision = rule_based_selector(state, SCENARIOS)
    exec_result = react_executor(state, decision.selected)
    trace_logger(state, decision, exec_result)
    return exec_result


if __name__ == "__main__":
    # Example states to see different branches
    states = [
        State(danger_level=8, enemy_detected=True, resources_low=False),
        State(danger_level=3, enemy_detected=True, resources_low=False),
        State(danger_level=2, enemy_detected=False, resources_low=True),
    ]

    for s in states:
        run_tora(s)
