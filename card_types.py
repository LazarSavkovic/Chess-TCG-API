import uuid


class Card:
    name = "Default Card"
    role = 'default role'
    def __init__(self, card_type, card_id, owner, image='', mana=0):
        self.id = str(uuid.uuid4())      # unique instance ID
        self.card_id = card_id           # shared ID for this card type
        self.type = card_type            # 'monster', 'land', or 'sorcery'
        self.owner = owner               # user who owns it
        self.image = image
        self.mana = mana

    def to_dict(self):
        return {
            'name': self.name,
            'role': self.role,
            'id': self.id,
            'card_id': self.card_id,
            'type': self.type,
            'owner': self.owner,
            'image': self.image,
            'mana': self.mana
        }

class Monster(Card):
    movement = {}
    original_attack = 0
    original_defense = 0

    def __init__(self, card_id, owner, attack, defense, image='', mana=0):
        super().__init__('monster', card_id, owner, image, mana)
        self.attack = attack
        self.defense = defense

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'attack': self.attack,
            'defense': self.defense,
            'movement': self.movement,
            'original_attack': self.original_attack,
            'original_defense': self.original_defense,

        })
        return base


    @staticmethod
    def can_move(card, from_pos, to_pos, board):
        fx, fy = from_pos
        tx, ty = to_pos
        dx, dy = tx - fx, ty - fy

        if dx == 0 and dy == 0:
            return False  # no movement

        # Normalize deltas to direction unit vectors
        dir_x = 0 if dx == 0 else dx // abs(dx)
        dir_y = 0 if dy == 0 else dy // abs(dy)

        direction = Monster.resolve_direction(dir_x, dir_y, card.owner)
        if not direction:
            return False

        allowed_range = card.__class__.movement.get(direction)
        if not allowed_range:
            return False

        steps = max(abs(dx), abs(dy))
        if allowed_range != 'any' and steps > allowed_range:
            return False

        # Optional: check for blocking pieces between start and end
        # or add collision detection here if needed

        return True

    @staticmethod
    def resolve_direction(dx, dy, owner):
        # Flip perspective for owner '2'
        if owner == '2':
            dx = -dx
            dy = -dy

        direction_map = {
            (-1,  0): "forward",
            (-1, -1): "forward-left",
            (-1,  1): "forward-right",
            ( 0, -1): "left",
            ( 0,  1): "right",
            ( 1,  0): "back",
            ( 1, -1): "back-left",
            ( 1,  1): "back-right"
        }
        return direction_map.get((dx, dy))


class Sorcery(Card):
    activation_needs = [] # default: no constraints
    text = ''
    def __init__(self, card_id, owner, image='', mana=0):
        super().__init__('sorcery', card_id, owner, image, mana)



    def affect_board(self, game, user_id):
        """
        Override this in subclasses to define what the card does.
        """
        pass

    def to_dict(self):
        base = super().to_dict()
        base['activation_needs'] = self.activation_needs
        base['text'] = self.text
        base['effect'] = self.__class__.__name__  # optional, for display
        return base


class Land(Card):
    creation_needs = [] # default: no constraints
    text = ''
    def __init__(self, card_id, owner, image='', mana=0):
        super().__init__('land', card_id, owner, image, mana)


    def affect_board(self, game, user_id):
        """
        Override this in subclasses to define what the card does.
        """
        pass

    def blocks_movement(self, monster):
        return False

    def on_enter(self, game, pos, monster):
        pass

    def on_turn_start(self, game, pos, monster):
        pass

    def to_dict(self):
        base = super().to_dict()
        base['creation_needs'] = self.creation_needs
        base['text'] = self.text
        base['effect'] = self.__class__.__name__  # optional, for display
        return base

def satisfies_need(game, x, y, direction, owner, required_role=None):
    print(required_role, 'req role')
    dx, dy = get_direction_offset(direction, owner)
    tx, ty = x + dx, y + dy

    if not (0 <= tx < len(game.board) and 0 <= ty < len(game.board[0])):
        return 0

    # --- Check the tile in the required direction on monster board ---
    target_card = game.board[tx][ty]
    if isinstance(target_card, Monster):

        # ✅ Only count your own lands
        if target_card.owner != owner:
            return 0


        for dir in target_card.movement:
            range_val = target_card.movement[dir]
            if range_val not in (1, 2, 'any'):
                continue

            offset = get_direction_offset(dir, target_card.owner)
            if offset is None:
                continue
            nx, ny = offset
            if [tx + nx, ty + ny] == [x, y]:
                print(target_card.role)
                if required_role and getattr(target_card, "role", None) == required_role:

                    return 2
                return 1

    # --- Check the land board in the same direction ---
    target_card = game.land_board[tx][ty]
    if isinstance(target_card, Land):

        # ✅ Only count your own lands
        if target_card.owner != owner:
            return 0

        for dir in target_card.creation_needs:
            offset = get_direction_offset(dir, target_card.owner)
            if offset is None:
                continue
            nx, ny = offset
            if [tx + nx, ty + ny] == [x, y]:
                if required_role and getattr(target_card, "role", None) == required_role:
                    return 2
                return 1

    return 0


def evaluate_creation_or_activation_needs(card, game, x, y):
    needs = getattr(card, "activation_needs", None) if card.type == "sorcery" else getattr(card, "creation_needs", None)
    if not needs:
        return 2  # No needs? Always playable for free


    results = [satisfies_need(game, x, y, direction, card.owner, required_role=getattr(card, "role", None)) for direction in needs]
    print(results, "results")
    if all(r == 2 for r in results):
        return 2  # All match and same role → free
    elif all(r >= 1 for r in results):
        return 1  # All satisfied but not all match → paid
    else:
        return 0  # At least one not satisfied → blocked



def get_direction_offset(direction, owner=None):
    forward = -1 if owner == '1' else 1
    left = -1 if owner == '1' else 1
    right = 1 if owner == '1' else -1

    mapping = {
        "forward": (forward, 0),
        "back": (-forward, 0),
        "left": (0, left),
        "right": (0, right),
        "forward-left": (forward, left),
        "forward-right": (forward, right),
        "back-left": (-forward, left),
        "back-right": (-forward, right),
    }
    return mapping.get(direction, (0, 0))

