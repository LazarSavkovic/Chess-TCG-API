
from card_types import Monster, Sorcery, Land
from random import shuffle, choice
from util import get_playable_card_classes, build_capped_deck
from card_types import evaluate_creation_or_activation_needs
from random import shuffle

from random import shuffle
from util import get_playable_card_classes

# Build registry card_id -> class
_CARD_CLASS_BY_ID = None
def _class_by_id():
    global _CARD_CLASS_BY_ID
    if _CARD_CLASS_BY_ID is None:
        _CARD_CLASS_BY_ID = {}
        for cls in get_playable_card_classes():
            # assumes each class exposes a unique .card_id (string)
            _CARD_CLASS_BY_ID[getattr(cls, "card_id", cls.__name__)] = cls
    return _CARD_CLASS_BY_ID

def build_instances_from_rows(rows, owner):
    out = []
    reg = _class_by_id()
    for r in (rows or []):
        cid = r.get("card_id")
        qty = int(r.get("qty", 1))
        cls = reg.get(cid)
        if not cls:
            # Unknown card id -> skip (or raise)
            continue
        for _ in range(max(1, qty)):
            out.append(cls(owner))
    shuffle(out)
    return out

def validate_deck_payload(payload, *, max_main=40, max_land=15, max_copies=3):
    """Return (ok, msg)"""
    if not isinstance(payload, dict) or "piles" not in payload:
        return False, "Invalid deck file"

    piles = payload["piles"]
    main = piles.get("MAIN", [])
    land = piles.get("LAND", [])
    # (SIDE is allowed but unused during start; you can add it later)

    # size checks (tune as you wish, or just warn)
    if len(main) == 0:
        return False, "MAIN pile is empty"
    # Optional: enforce exact sizes if your rules want it
    # total_main = sum(row.get("qty", 1) for row in main)
    # total_land = sum(row.get("qty", 1) for row in land)
    # if total_main != max_main: return False, f"MAIN must be {max_main} cards"
    # if total_land != max_land: return False, f"LAND must be {max_land} cards"

    # copy cap
    from collections import Counter
    c = Counter()
    for row in main + land:
        c[row.get("card_id")] += int(row.get("qty", 1))
    over = [cid for cid, n in c.items() if n > max_copies]
    if over:
        return False, f"Too many copies of: {', '.join(over)} (>{max_copies})"

    # card id existence check (optional)
    reg = _class_by_id()
    missing = [r.get("card_id") for r in (main + land) if r.get("card_id") not in reg]
    if missing:
        return False, f"Unknown card ids: {', '.join(sorted(set(missing)))}"

    return True, "ok"




class ChessGame:
    def __init__(self):
        self.board = self.init_board()
        self.land_board = self.init_land_board()

        self.players = ['1', '2']
        self.turn_index = 0
        self.moves_this_turn = 0
        self.max_moves_per_turn = 3
        self.center_tile_control = {'1': 0, '2': 0}

        self.mana = {'1': 50, '2': 50}
        self.graveyard = {'1': [], '2': []}

        # runtime state
        self.decks = {'1': [], '2': []}
        self.land_decks = {'1': [], '2': []}
        self.hands = {'1': [], '2': []}
        self.summoned_this_turn = set()
        self.sorcery_used_this_turn = set()
        self.land_placed_this_turn = set()

    def reset_runtime_state(self):
        self.board = self.init_board()
        self.land_board = self.init_land_board()
        self.turn_index = 0
        self.moves_this_turn = 0
        self.center_tile_control = {'1': 0, '2': 0}
        self.mana = {'1': 50, '2': 50}
        self.graveyard = {'1': [], '2': []}
        self.hands = {'1': [], '2': []}
        self.summoned_this_turn = set()
        self.sorcery_used_this_turn = set()
        self.land_placed_this_turn = set()

    def apply_decks_and_start(self, deck_rows_p1, land_rows_p1, deck_rows_p2, land_rows_p2):
        """
        deck_rows_* and land_rows_* are compressed rows from your export:
        [{card_id, qty, position}]
        """
        self.reset_runtime_state()

        self.decks['1'] = build_instances_from_rows(deck_rows_p1, '1')
        self.decks['2'] = build_instances_from_rows(deck_rows_p2, '2')
        self.land_decks['1'] = build_instances_from_rows(land_rows_p1, '1')
        self.land_decks['2'] = build_instances_from_rows(land_rows_p2, '2')

        # initial draw (5)
        for pid in ['1', '2']:
            # guard if short decks
            draw_n = min(5, len(self.decks[pid]))
            self.hands[pid] = [self.decks[pid].pop() for _ in range(draw_n)]


    @staticmethod
    def get_valid_summon_positions(user_id):
        r = 0 if user_id == '2' else 5
        return [[r, col] for col in range(6)]

    def draw_card(self, user_id):
        if self.decks[user_id]:
            self.hands[user_id].append(self.decks[user_id].pop(0))

    def summon_card(self, slot_index, to_pos, user_id):
        if user_id != self.current_player:
            return False, "Not your turn"
        if user_id in self.summoned_this_turn:
            return False, "You've already summoned this turn"
        print(to_pos)

        if to_pos not in self.get_valid_summon_positions(user_id):
            return False, "Invalid summon position"

        tx, ty = to_pos
        if self.board[tx][ty] is not None:
            return False, "Tile is occupied"

        hand = self.hands[user_id]
        if not (0 <= slot_index < len(hand)):
            return False, "Invalid card slot"

        card = hand.pop(slot_index)
        if self.mana[user_id] < card.mana:
            return False, "Not enough mana"
        self.mana[user_id] -= card.mana
        self.board[tx][ty] = card
        self.summoned_this_turn.add(user_id)
        return True, f"{card.name} summoned!"

    def init_board(self):
        board = [[None for _ in range(6)] for _ in range(6)]

        return board

    def init_land_board(self):
        land_board = [[None for _ in range(7)] for _ in range(7)]

        return land_board

    @property
    def current_player(self):
        return self.players[self.turn_index]

    def toggle_turn(self):

        self.turn_index = (self.turn_index + 1) % len(self.players)
        self.moves_this_turn = 0
        self.summoned_this_turn.clear()
        self.sorcery_used_this_turn.clear()
        self.land_placed_this_turn.clear()
        self.draw_card(self.current_player)

        for x in range(6):
            for y in range(6):
                card = self.board[x][y]
                land = self.land_board[x][y]
                if card and land and hasattr(land, 'on_turn_start'):
                    land.on_turn_start(self, (x, y), card)

    def can_move(self, user_id):
        return user_id == self.current_player and self.moves_this_turn < self.max_moves_per_turn

    def direct_attack(self, pos, user_id):
        if not self.can_move(user_id):
            return False, "You've used all your moves", False

        x, y = pos
        card = self.board[x][y]
        if not card or card.owner != user_id:
            return False, "Invalid card selected", False

        opponent = '2' if user_id == '1' else '1'
        back_row = 0 if user_id == '1' else 5
        if x != back_row:
            return False, "Not in position for direct attack", False

        self.mana[opponent] -= card.mana

        self.moves_this_turn += 1

        # Optional win check
        if self.mana[opponent] <= 0:
            self.mana[opponent] = 0
            return True, f"{card.name} dealt a final blow!", True

        return True, f"{card.name} attacked directly for {card.mana} mana!", False


    def move(self, from_pos, to_pos, user_id):
        if not self.can_move(user_id):
            return False, "You've used all your moves"

        fx, fy = from_pos
        tx, ty = to_pos
        card = self.board[fx][fy]

        if not card:
            return False, "No card at source"
        if card.owner != user_id:
            return False, "That's not your card"
        if not Monster.can_move(card, from_pos, to_pos, self.board):
            return False, "Invalid move"
        # Blocked path check (no jumping)
        dx = tx - fx
        dy = ty - fy
        step_x = 0 if dx == 0 else dx // abs(dx)
        step_y = 0 if dy == 0 else dy // abs(dy)

        x, y = fx + step_x, fy + step_y
        while (x, y) != (tx, ty):
            if self.board[x][y] is not None:
                return False, "Path blocked by another monster"
            x += step_x
            y += step_y
            land = self.land_board[x][y]
            if land:
                if hasattr(land, 'blocks_movement') and land.blocks_movement(card):
                    return False, f"{land.name} blocks movement!"

        target = self.board[tx][ty]
        target_land = self.land_board[tx][ty]
        if target_land:
            if hasattr(target_land, 'blocks_movement') and target_land.blocks_movement(card):
                return False, f"{target_land.name} blocks movement!"
            if hasattr(target_land, 'affects_monster_passing'):
                target_land.affects_monster_passing(card)
                return False, f"{target_land.name} blocks movement!"
            else:
                if hasattr(target_land, 'on_enter'):
                    target_land.on_enter(self, (tx, ty), card)

        if target:
            if target.owner == card.owner:
                return False, "Can't capture your own card"
            if card.attack > target.defense:
                self.graveyard[target.owner].append(target)
                self.board[tx][ty] = card
                self.board[fx][fy] = None
                self.moves_this_turn += 1
                return True, f"{card.name} defeated {target.name}!"
            if card.attack == target.defense:
                self.graveyard[target.owner].append(target)
                self.graveyard[card.owner].append(card)
                self.board[tx][ty] = None
                self.board[fx][fy] = None
                self.moves_this_turn += 1
                return True, f"{card.name} and {target.name} defeated!"
            else:
                self.graveyard[card.owner].append(card)
                self.board[fx][fy] = None
                self.moves_this_turn += 1
                return True, f"{card.name} was killed by {target.name}!"
        else:
            self.board[tx][ty] = card
            self.board[fx][fy] = None
            self.moves_this_turn += 1
            return True, "Move successful"

        self.board[tx][ty] = card
        self.board[fx][fy] = None
        self.moves_this_turn += 1
        return True, "Move successful"

    def game_can_activate_card(self, slot_index, user_id, target_pos):
        print('slot', slot_index, user_id, target_pos)
        print('here game_can_activate_card')
        if user_id != self.current_player:
            return False, "Not your turn", False

        if user_id in self.sorcery_used_this_turn:
            return False, "You've already used a sorcery this turn", False

        hand = self.hands[user_id]
        if not (0 <= slot_index < len(hand)):
            return False, "Invalid card slot", False

        card = hand[slot_index]
        print(card.name)
        if card.type != 'sorcery':
            return False, "This is not a sorcery", False

        if self.mana[user_id] < card.mana:
            return False, "Not enough mana", False

        if target_pos is None:
            return False, "No activation position provided", False

        activation_status = evaluate_creation_or_activation_needs(card, self, target_pos[0], target_pos[1])
        print(activation_status, 'act status')

        if activation_status == 0:
            return False, "Activation needs not met", False

        elif activation_status == 1:
            mana_available = self.mana.get(user_id, 0)
            if mana_available < card.mana:
                return False, "Not enough mana", False
            return True, "Card can be activated", False

        elif activation_status == 2:
            return True, "Card can be activated for free", True

        # Optional fallback
        return False, "Unknown activation status", False

    def activate_sorcery(self, slot_index, user_id, target_pos, reduce_mana=True):
        hand = self.hands[user_id]
        card = hand[slot_index]

        if reduce_mana:
            self.mana[user_id] -= card.mana

        hand.pop(slot_index)
        self.graveyard[user_id].append(card)
        self.sorcery_used_this_turn.add(user_id)

        card.affect_board(self, tuple(target_pos), user_id)

        return True, f"{card.name} activated!"

    def game_can_place_land(self, slot_index, user_id, to_pos):
        if user_id != self.current_player:
            return False, "Not your turn", False

        if user_id in self.land_placed_this_turn:
            return False, "You've already created a land this turn", False

        land_deck = self.land_decks[user_id]
        if not (0 <= slot_index < len(land_deck)):
            return False, "Invalid card slot", False

        card = land_deck[slot_index]
        if card.type != 'land':
            return False, "Not a land card", False

        x, y = to_pos
        if self.land_board[x][y] is not None:
            return False, "Land already exists here", False

        if self.board[x][y] is not None:
            return False, "Tile is occupied", False

        activation_status = evaluate_creation_or_activation_needs(card, self, x, y)

        if activation_status == 0:
            return False, "Activation needs not met", False
        elif activation_status == 1 and self.mana[user_id] < card.mana:
            return False, "Not enough mana", False

        # Success — return third value indicating if it's free
        return True, "Card can be activated for free" if activation_status == 2 else "Card can be activated", activation_status == 2

    def place_land(self, slot_index, user_id, to_pos, reduce_mana=True):
        x, y = to_pos

        land_deck = self.land_decks[user_id]
        card = land_deck[slot_index]

        self.land_placed_this_turn.add(user_id)
        if reduce_mana:
            self.mana[user_id] -= card.mana

        land_deck.pop(slot_index)
        self.land_board[x][y] = card

        return True, f"{card.name} placed as land"

