# interactions.py
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Literal

StepKind = Literal[
    "pay_cost",
    "discard_from_hand",
    "select_board_target",
    "select_land_target",
    "select_graveyard_card",
    "select_deck_card",
    "apply_effect",
]

@dataclass
class StepSpec:
    kind: StepKind
    owner: Optional[str] = None
    zone: Optional[str] = None
    filter: Optional[Dict[str, Any]] = None
    as_key: Optional[str] = None
    apply_method: Optional[str] = None
    cost: Optional[Dict[str, Any]] = None

@dataclass
class PendingInteraction:
    type: Literal["sorcery"]
    owner: str                   # '1' or '2'
    slot_index: int              # hand index
    card_id: str
    free: bool
    pos: Optional[Tuple[int, int]] = None
    steps: List[StepSpec] = field(default_factory=list)
    cursor: int = 0
    temp: Dict[str, Any] = field(default_factory=dict)

    def current_step(self) -> Optional[StepSpec]:
        if 0 <= self.cursor < len(self.steps):
            return self.steps[self.cursor]
        return None

    def advance(self):
        self.cursor += 1

    def done(self) -> bool:
        return self.cursor >= len(self.steps)
