from card_types import Monster, Sorcery, Land
from game import StepSpec
import time

class Bonecrawler(Monster):  # Formerly: Pawn
    name = "Bonecrawler"
    movement = {
        "forward": 2,
        'left': 2,
        'right': 2,
        'back': 2
    }
    role = "blue"
    original_attack = 100
    original_defense = 200

    def __init__(self, owner):
        super().__init__(
            card_id='bonecrawler',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/bonecrawler.png',
            mana=2
        )

#
class ShadowVine(Monster):  # Formerly: DiagonalRanger
    name = "Shadow Vine"
    movement = {
        "forward": 2,
        "forward-left": 2,
        "back-right": 2,
        "back-left": 2
    }
    role = "blue"
    original_attack = 200
    original_defense = 200

    def __init__(self, owner):
        super().__init__(
            card_id='shadow_vine',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/shadow_vine.png',
            mana=3
        )


class DreadmawQueen(Monster):  # Formerly: Queen
    name = "Dreadmaw Queen"
    movement = {
        "forward": 2,
        "forward-left": 2,
        "forward-right": 2,
        "right": 2,
        "back-left": 2,
        "left": 2,
        "back-right": 2,
        "back": 2
    }
    role = "blue"
    original_attack = 170
    original_defense = 130

    def __init__(self, owner):
        super().__init__(
            card_id='dreadmaw_queen',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/dreadmaw_queen.png',
            mana=4
        )

class FrostRevenant(Monster):
    name = "Frost Revenant"
    movement = {
        "forward": 2,
        "back-left": 1,
        "back": 1
    }
    original_attack = 170
    original_defense = 190
    role = "white"
    def __init__(self, owner):
        super().__init__(
            card_id='frost_revenant',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/frost_revenant.png',
            mana=3
        )


class SolarPaladin(Monster):
    name = "Solar Paladin"
    movement = {
        "forward": 1,
        "back": 1,
        "back-left": 1,
        "right": 1
    }

    original_attack = 230
    original_defense = 130
    role = "red"
    def __init__(self, owner):
        super().__init__(
            card_id='solar_paladin',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/solar_paladin.png',
            mana=4
        )

class SylvanArcher(Monster):
    name = "Sylvan Archer"
    movement = {
        "forward-left": 1,
        "forward-right": 1,
        "back-left": 1,
        "back-right": 1
    }
    role = "blue"
    original_attack = 130
    original_defense = 200

    def __init__(self, owner):
        super().__init__(
            card_id='sylvan_archer',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/sylvan_archer.png',
            mana=2
        )



class Magistra(Monster):
    name = "Magistra"
    movement = {
        "forward": 1,
        "left": 2,
        "right": 2,
        "back-left": 1,
        "back-right": 1
    }
    role = "white"
    original_attack = 170
    original_defense = 190

    def __init__(self, owner):
        super().__init__(
            card_id='magistra',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/magistra.png',
            mana=3
        )



class LordOfTheAbyss(Monster):
    name = "Lord of the Abyss"
    movement = {
        "forward": 1,
        "left": 1,
        "right": 1,
        "back-left": 1,
        "back-right": 1
    }
    role = "black"
    original_attack = 220
    original_defense = 200

    def __init__(self, owner):
        super().__init__(
            card_id='lord_of_the_abyss',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/lord_of_the_abyss.png',
            mana=4
        )


class Stormcaller(Monster):
    name = "Stormcaller"
    movement = {
        "forward-right": 2,
        "back-left": 1,
        "back-right": 1
    }
    role = "black"
    original_attack = 170
    original_defense = 190

    def __init__(self, owner):
        super().__init__(
            card_id='stormcaller',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/stormcaller.png',
            mana=3
        )



class WingsOfTheShatteredSkies(Monster):
    name = "Wings of the Shattered Skies"
    movement = {
        'forward': 2,
        "forward-right": 1,
        "forward-left": 1,
        "back-left": 1,
        "back-right": 1
    }
    role = "blue"
    original_attack = 150
    original_defense = 170

    def __init__(self, owner):
        super().__init__(
            card_id='wings_of_the_shattered_skies',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/wings_of_the_shattered_skies.png',
            mana=2
        )


class AbyssalLeviathan(Monster):
    name = "Abyssal Leviathan"
    movement = {
        "forward": 2,
        "back": 1,
        "left": 1,
        "right": 1
    }
    role = "blue"
    original_attack = 250
    original_defense = 150

    def __init__(self, owner):
        super().__init__(
            card_id='abyssal_leviathan',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/abyssal_leviathan.png',
            mana=5
        )


class BloodthornReaper(Monster):
    name = "Bloodthorn Reaper"
    movement = {
        "forward-left": 2,
        "forward-right": 2,
        "back": 1
    }
    role = "black"
    original_attack = 190
    original_defense = 140

    def __init__(self, owner):
        super().__init__(
            card_id='bloodthorn_reaper',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/bloodthorn_reaper.png',
            mana=3
        )

class CelestialTitan(Monster):
    name = "Celestial Titan"
    movement = {
        "forward": 2,
        "left": 1,
        "right": 1,
        "back": 1
    }
    original_attack = 200
    original_defense = 250
    role = "red"
    def __init__(self, owner):
        super().__init__(
            card_id='celestial_titan',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/celestial_titan.png',
            mana=5
        )






class VolcanicRift(Land):
    name = "Volcanic Rift"
    text = "Burns an opponent's monster for 50 DEF when it steps on this tile."
    creation_needs = ["forward"]
    role = "red"
    def __init__(self, owner):
        super().__init__('volcanic_rift', owner, image='/static/cards/volcanic_rift.png', mana=1)

    def on_enter(self, game, pos, monster):
        if monster.owner != self.owner:
            monster.defense -= 50
            if monster.defense <= 0:
                game.graveyard[monster.owner].append(monster)
                x, y = pos
                game.board[x][y] = None


class SacredGrove(Land):
    name = "Sacred Grove"
    text = "Heals your monster for 30 DEF every turn it's on this tile."
    creation_needs = ['left']
    role = "blue"
    def __init__(self, owner):
        super().__init__('sacred_grove', owner, image='/static/cards/sacred_grove.png', mana=1)

    def on_turn_start(self, game, pos, monster):
        if monster.owner == self.owner:
            monster.defense += 30


class FrozenBarrier(Land):
    name = "Frozen Barrier"
    text = "Opponent's monsters cannot move across this tile."
    creation_needs = ["right", 'forward']
    role = "white"
    def __init__(self, owner):
        super().__init__('frozen_barrier', owner, image='/static/cards/frozen_barrier.png', mana=1)

    def blocks_movement(self, monster):
        if monster.owner != self.owner:
            return True
        return False



# class WearyTravellersInn(Land):
#     name = "Weary Travellers Inn"
#     text = "When your monster lands on this tile, you gain one more move."
#     creation_needs = ["right", 'forward']
#     role = "blue"
#     def __init__(self, owner):
#         super().__init__('weary_travellers_inn', owner, image='/static/cards/weary_travellers_inn.png', mana=1)
#
#     def on_enter(self, game, pos, monster):
#         # Only grant to the tile's owner
#         if monster.owner != self.owner:
#             return
#
#         # Ensure a per-turn tracker exists on the game
#         if not hasattr(game, "_bonus_move_granted"):
#             game._bonus_move_granted = set()
#
#         # Grant at most once per player per turn
#         if monster.owner not in game._bonus_move_granted:
#             game._bonus_move_granted.add(monster.owner)
#             # Give one extra move for the rest of THIS turn
#             game.max_moves_per_turn += 1


class StormNexus(Land):
    name = "Storm Nexus"
    text = "Reduces the ATK of enemy monsters that land on this tile by 40."
    creation_needs = ["back-left"]
    role = "black"
    def __init__(self, owner):
        super().__init__('storm_nexus', owner, image='/static/cards/storm_nexus.png', mana=1)

    def on_enter(self, game, pos, monster):
        if monster.owner != self.owner:
            monster.attack -= 40


class WastelandMine(Land):
    name = "Wasteland Mine"
    text = "An opponents monster going over or landing on this land loses 30 ATK and DEF"
    creation_needs = ["right"]
    role = "red"
    def __init__(self, owner):
        super().__init__('wasteland_mine', owner, image='/static/cards/wasteland_mine.png', mana=1)

    def on_enter(self, game, pos, monster):
        if monster.owner != self.owner:
            monster.attack -= 30
            monster.defense -= 30

    def affect_monster_passing(self, monster):
        if monster.owner != self.owner:
            monster.attack -= 30
            monster.defense -= 30


class RuleOfTheMeek(Land):
    name = "Rule of the Meek"
    text = "Opponent's monsters with ATK or DEF over 150 cannot move across this tile."
    creation_needs = ["forward-right"]
    role = "white"
    def __init__(self, owner):
        super().__init__('rule_of_the_meek', owner, image='/static/cards/rule_of_the_meek.png', mana=1)

    def blocks_movement(self, monster):
        if monster.owner != self.owner and ((monster.defense > 150) and (monster.attack > 150)):
            return True
        return False







# NEW


# =========================
# MONSTERS
# =========================

class EmberRavager(Monster):
    name = "Ember Ravager"
    movement = {
        "forward": 2,
        "left": 1,
        "right": 1,
        "back": 1
    }
    role = "red"
    original_attack = 240
    original_defense = 140

    def __init__(self, owner):
        super().__init__(
            card_id='ember_ravager',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/ember_ravager.png',
            mana=4
        )


class RiftStrider(Monster):
    name = "Rift Strider"
    movement = {
        "forward": "any",
        "back": "any",
        "left": "any",
        "right": "any"
    }
    role = "blue"
    original_attack = 160
    original_defense = 160

    def __init__(self, owner):
        super().__init__(
            card_id='rift_strider',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/rift_strider.png',
            mana=4
        )


class PaleSentinel(Monster):
    name = "Pale Sentinel"
    movement = {
        "forward-left": 1,
        "forward-right": 1,
        "back-left": 2,
        "back-right": 2
    }
    role = "white"
    original_attack = 150
    original_defense = 220

    def __init__(self, owner):
        super().__init__(
            card_id='pale_sentinel',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/pale_sentinel.png',
            mana=3
        )


class GloomStalker(Monster):
    name = "Gloom Stalker"
    movement = {
        "forward-left": 2,
        "forward-right": 2,
        "left": 1,
        "right": 1
    }
    role = "black"
    original_attack = 210
    original_defense = 160

    def __init__(self, owner):
        super().__init__(
            card_id='gloom_stalker',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/gloom_stalker.png',
            mana=4
        )


# =========================
# LANDS (new mechanics)
# =========================

class SanctumOfDawn(Land):
    name = "Sanctum of Dawn"
    text = "At the start of your turn, if your monster is on this tile, gain 1 mana."
    creation_needs = ["left"]
    role = "white"

    def __init__(self, owner):
        super().__init__('sanctum_of_dawn', owner, image='/static/cards/sanctum_of_dawn.png', mana=1)

    def on_turn_start(self, game, pos, monster):
        if monster and monster.owner == self.owner:
            game.mana[self.owner] = game.mana.get(self.owner, 0) + 1


class ObsidianSpikes(Land):
    name = "Obsidian Spikes"
    text = "Enemies lose 40 DEF entering; passing through also shaves 20 ATK."
    creation_needs = ["forward"]
    role = "red"

    def __init__(self, owner):
        super().__init__('obsidian_spikes', owner, image='/static/cards/obsidian_spikes.png', mana=1)

    def on_enter(self, game, pos, monster):
        if monster.owner != self.owner:
            monster.defense -= 40
            if monster.defense <= 0:
                game.graveyard[monster.owner].append(monster)
                x, y = pos
                game.board[x][y] = None

    def affect_monster_passing(self, monster):
        if monster.owner != self.owner:
            monster.attack -= 20


class AetherSpring(Land):
    name = "Aether Spring"
    text = "At the start of your turn, if your monster is here, draw 1."
    creation_needs = ["forward-right"]
    role = "blue"

    def __init__(self, owner):
        super().__init__('aether_spring', owner, image='/static/cards/aether_spring.png', mana=1)

    def on_turn_start(self, game, pos, monster):
        if monster and monster.owner == self.owner and game.decks[self.owner]:
            game.hands[self.owner].append(game.decks[self.owner].pop(0))


class NightshroudBog(Land):
    name = "Nightshroud Bog"
    text = "Enemies entering lose 20 ATK and 20 DEF."
    creation_needs = ["back"]
    role = "black"

    def __init__(self, owner):
        super().__init__('nightshroud_bog', owner, image='/static/cards/nightshroud_bog.png', mana=1)

    def on_enter(self, game, pos, monster):
        if monster.owner != self.owner:
            monster.attack -= 20
            monster.defense -= 20
            if monster.defense <= 0:
                game.graveyard[monster.owner].append(monster)
                x, y = pos
                game.board[x][y] = None


class WardOfCensure(Land):
    name = "Ward of Censure"
    text = "Blocks movement of enemy red or white monsters."
    creation_needs = ["back-left"]
    role = "black"

    def __init__(self, owner):
        super().__init__('ward_of_censure', owner, image='/static/cards/ward_of_censure.png', mana=1)

    def blocks_movement(self, monster):
        return monster.owner != self.owner and (getattr(monster, "role", None) in ("red", "white"))


# =========================
# SORCERIES (tutoring, land control, role synergies)
# =========================





class TideOfKnowledge(Sorcery):
    name = "Tide of Knowledge"
    text = "Draw up to 2 cards. +1 extra if you control at least 2 blue lands."
    activation_needs = ["forward"]
    role = "blue"

    def __init__(self, owner):
        super().__init__('tide_of_knowledge', owner, image='/static/cards/tide_of_knowledge.png', mana=2)

    def affect_board(self, game, target_pos, user_id):
        # count blue lands you control
        blue_lands = sum(
            1 for row in game.land_board for land in row
            if land and land.owner == user_id and getattr(land, "role", None) == "blue"
        )
        draws = 2 + (1 if blue_lands >= 2 else 0)
        for _ in range(draws):
            if game.decks[user_id]:
                game.hands[user_id].append(game.decks[user_id].pop(0))




class RiteOfReclamation(Sorcery):
    name = "Rite of Reclamation"
    text = "Discard a card; destroy an enemy monster; bring back a monster from your graveyard."
    activation_needs = ["forward"]
    role = "black"

    def __init__(self, owner):
        super().__init__('rite_of_reclamation', owner, image='/static/cards/rite.png', mana=3)

    def script(self, game, user_id):
        return [
            StepSpec(kind="discard_from_hand", owner="self", zone="hand", as_key="discarded"),
            StepSpec(kind="select_board_target", owner="opponent", zone="board",
                     filter={"require_enemy": True, "require_monster": True}, as_key="kill_pos"),
            StepSpec(kind="apply_effect", apply_method="do_kill"),
            StepSpec(kind="select_graveyard_card", owner="self", zone="graveyard",
                     filter={"type": "monster"}, as_key="revive_card"),
            StepSpec(kind="apply_effect", apply_method="do_revive"),
        ]

    # apply bodies called by the engine
    def do_kill(self, game, _pos, user_id):
        x, y = game.interaction.temp["kill_pos"]
        target = game.board[x][y]
        if target:
            game.graveyard[target.owner].append(target)
            game.board[x][y] = None

    def do_revive(self, game, _pos, user_id):
        cid = game.interaction.temp["revive_card"]
        # pull the card instance back from graveyard
        pool = game.graveyard[user_id]
        for i, c in enumerate(pool):
            if c.id == cid:
                pool.pop(i)
                # put revived monster to hand (or spawn to a default zone; your choice)
                game.hands[user_id].append(c)
                break




class BlazingRain(Sorcery):
    name = 'Blazing Rain'
    text = "Weaken all opponent's DEF by 50."
    activation_needs = ["back"]
    role = "red"
    def __init__(self, owner):
        super().__init__('blazing_rain', owner, image='/static/cards/blazing_rain.png', mana=3)


    def affect_board(self, game, target_pos, user_id):
        for row in game.board:
            for i, card in enumerate(row):
                if card and card.owner != user_id and isinstance(card, Monster):
                    card.defense -= 50
                    if card.defense <= 0:
                        game.graveyard[card.owner].append(card)
                        row[i] = None


class NaturesResurgence(Sorcery):
    name = 'Natures Resurgence'
    text = 'Increase the DEF of your monsters by 30.'
    activation_needs = [ "forward-right"]
    role = "white"
    def __init__(self, owner):
        super().__init__('natures_resurgence', owner, image='/static/cards/natures_resurgence.png', mana=1)

    def affect_board(self, game, target_pos, user_id):
        for row in game.board:
            for card in row:
                if card and card.owner == user_id and isinstance(card, Monster):
                    card.defense += 30


class MysticDraw(Sorcery):
    name = 'Mystic Draw'
    text = 'Draw 2 cards.'
    activation_needs = ["left", "back"]
    role = "blue"
    def __init__(self, owner):
        super().__init__('mystic_draw', owner, image='/static/cards/mystic_draw.png', mana=2)

    def affect_board(self, game, target_pos, user_id):
        for _ in range(2):
            if game.decks[user_id]:
                game.hands[user_id].append(game.decks[user_id].pop(0))
#

class DivineReset(Sorcery):
    name = 'Divine Reset'
    text = 'Destroy all monsters on the field.'
    activation_needs = ['left', 'right']
    role = "black"
    def __init__(self, owner):
        super().__init__(
            card_id='divine_reset',
            owner=owner,
            image='/static/cards/divine_reset.png',
            mana=2
        )

    def affect_board(self, game, target_pos, user_id):
        for row in game.board:
            for i, card in enumerate(row):
                if card and isinstance(card, Monster):
                    game.graveyard[card.owner].append(card)
                    row[i] = None


class ArcaneTempest(Sorcery):
    name = 'Arcane Tempest'
    text = "Reduce all opponent's ATK by 40."
    activation_needs = ['back-right']
    role = "white"
    def __init__(self, owner):
        super().__init__('arcane_tempest', owner, image='/static/cards/arcane_tempest.png', mana=2)

    def affect_board(self, game, target_pos, user_id):
        for row in game.board:
            for card in row:
                if card and card.owner != user_id and isinstance(card, Monster):
                    card.attack -= 40




class SilentRecruiter(Sorcery):
    name = "Silent Recruiter"
    text = "Choose monster with attack lower or equal to 180 from deck and add to hand."
    activation_needs = ['back']
    role = "white"
    def __init__(self, owner):
        super().__init__(
            card_id="silent_recruiter",
            owner=owner,
            image="/static/cards/silent_recruiter.png",
            mana=2
        )

    def script(self, game, user_id):
        # Build a dynamic filter the FE can also use to pre-highlight
        return [
            StepSpec(kind="select_deck_card", owner="self", zone="deck",
                     filter={"type":"monster", "max_attack":180}, as_key="pick"),
            StepSpec(kind="apply_effect", apply_method="add_picked_to_hand")
        ]

    def add_picked_to_hand(self, game, _pos, user_id):
        cid = game.interaction.temp["pick"]
        deck = game.decks[user_id]
        for i, c in enumerate(deck):
            if c.id == cid:
                deck.pop(i)
                game.hands[user_id].append(c)
                return









class MonarchsSummons(Sorcery):
    name = "Monarch's Summons"
    text = "Tutor a red monster with ATK ≥ 200 from your deck to your hand."
    activation_needs = ["right"]
    role = "red"

    def __init__(self, owner):
        super().__init__('monarchs_summons', owner, image='/static/cards/monarchs_summons.png', mana=2)

    def script(self, game, user_id):
        # Note: UI uses the filter to pre-highlight. We'll re-check in apply.
        return [
            StepSpec(kind="select_deck_card", owner="self", zone="deck",
                     filter={"type": "monster", "role": "red", "min_attack": 200}, as_key="pick"),
            StepSpec(kind="apply_effect", apply_method="add_picked_to_hand")
        ]

    def add_picked_to_hand(self, game, _pos, user_id):
        cid = game.interaction.temp["pick"]
        deck = game.decks[user_id]
        for i, c in enumerate(deck):
            if c.id == cid and c.type == 'monster' and getattr(c, "role", None) == "red" and getattr(c, "attack", 0) >= 200:
                deck.pop(i)
                game.hands[user_id].append(c)
                return

class OneMoreTrick(Sorcery):
    name = "One More Trick"
    text = "Choose a sorcery from deck and add to hand."
    activation_needs = ['forward']
    role = "blue"

    def __init__(self, owner):
        super().__init__('one_more_trick', owner, image="/static/cards/one_more_trick.png", mana=3)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_deck_card", owner="self", zone="deck",
                     filter={"type": "sorcery"}, as_key="pick"),
            StepSpec(kind="apply_effect", apply_method="add_picked_to_hand"),
        ]

    def add_picked_to_hand(self, game, _pos, user_id):
        cid = game.interaction.temp["pick"]
        deck = game.decks[user_id]
        for i, c in enumerate(deck):
            if c.id == cid and c.type == 'sorcery':
                deck.pop(i)
                game.hands[user_id].append(c)
                return

class WanderersCompass(Sorcery):
    name = "Wanderer's Compass"
    text = "Choose a blue sorcery from deck and add to hand."
    activation_needs = ['left']
    role = "blue"

    def __init__(self, owner):
        super().__init__('wanderers_compass', owner, image="/static/cards/wanderers_compass.png", mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_deck_card", owner="self", zone="deck",
                     filter={"type": "sorcery", "role": "blue"}, as_key="pick"),
            StepSpec(kind="apply_effect", apply_method="add_picked_to_hand"),
        ]

    def add_picked_to_hand(self, game, _pos, user_id):
        cid = game.interaction.temp["pick"]
        deck = game.decks[user_id]
        for i, c in enumerate(deck):
            if c.id == cid and c.type == 'sorcery' and getattr(c, "role", None) == "blue":
                deck.pop(i)
                game.hands[user_id].append(c)
                return


# --- TARGET A BOARD MONSTER (ANY/ENEMY/ALLY) -------------------------------

class HexOfInversion(Sorcery):
    name = "Hex of Inversion"
    text = "Choose a monster; swap its ATK and DEF."
    activation_needs = ["back-right"]
    role = "black"

    def __init__(self, owner):
        super().__init__('hex_of_inversion', owner, image='/static/cards/hex_of_inversion.png', mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="any", zone="board",
                     filter={"require_monster": True}, as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_invert")
        ]

    def do_invert(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        card = game.board[x][y]
        if card and isinstance(card, Monster):
            card.attack, card.defense = card.defense, card.attack


class Overcharge(Sorcery):
    name = "Overcharge"
    text = "Choose your monster; it gains +100 ATK and loses 50 DEF."
    activation_needs = ["forward-left"]
    role = "red"

    def __init__(self, owner):
        super().__init__('overcharge', owner, image='/static/cards/overcharge.png', mana=1)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="self", zone="board",
                     filter={"require_monster": True}, as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_buff")
        ]

    def do_buff(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        card = game.board[x][y]
        if card and card.owner == user_id:
            card.attack += 100
            card.defense -= 50
            if card.defense <= 0:
                game.graveyard[card.owner].append(card)
                game.board[x][y] = None


class TargetedDestruction(Sorcery):
    name = "Targeted Destruction"
    text = "Choose and destroy an enemy monster."
    activation_needs = ['forward-right']
    role = "black"

    def __init__(self, owner):
        super().__init__('targeted_destruction', owner, image='/static/cards/targeted_destruction.png', mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="opponent", zone="board",
                     filter={"require_enemy": True, "require_monster": True}, as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_kill")
        ]

    def do_kill(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        card = game.board[x][y]
        if card and card.owner != user_id:
            game.graveyard[card.owner].append(card)
            game.board[x][y] = None


class EmpoweringLight(Sorcery):
    name = "Empowering Light"
    text = "Choose a monster to increase its ATK by 50."
    activation_needs = ['back-left']
    role = "white"

    def __init__(self, owner):
        super().__init__('empowering_light', owner, image='/static/cards/empowering_light.png', mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="any", zone="board",
                     filter={"require_monster": True}, as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_buff")
        ]

    def do_buff(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        card = game.board[x][y]
        if card and isinstance(card, Monster):
            card.attack += 50


class FrostbiteCurse(Sorcery):
    name = "Frostbite Curse"
    text = "Choose a monster to decrease its DEF by 30."
    activation_needs = ['forward']
    role = "red"

    def __init__(self, owner):
        super().__init__('frostbite_curse', owner, image='/static/cards/frostbite_curse.png', mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="any", zone="board",
                     filter={"require_monster": True}, as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_nerf")
        ]

    def do_nerf(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        card = game.board[x][y]
        if card and isinstance(card, Monster):
            card.defense -= 30
            if card.defense <= 0:
                game.graveyard[card.owner].append(card)
                game.board[x][y] = None


class MindSeize(Sorcery):
    name = "Mind Seize"
    text = "Choose an enemy monster to take control of it."
    activation_needs = ['back']
    role = "red"

    def __init__(self, owner):
        super().__init__('mind_seize', owner, image='/static/cards/mind_seize.png', mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="opponent", zone="board",
                     filter={"require_enemy": True, "require_monster": True}, as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_steal")
        ]

    def do_steal(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        card = game.board[x][y]
        if card and card.owner != user_id:
            card.owner = user_id


class PowerSurge(Sorcery):
    name = "Power Surge"
    text = "Choose a monster to double its ATK and DEF."
    activation_needs = ['forward']
    role = "red"

    def __init__(self, owner):
        super().__init__('power_surge', owner, image='/static/cards/power_surge.png', mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="any", zone="board",
                     filter={"require_monster": True}, as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_double")
        ]

    def do_double(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        card = game.board[x][y]
        if card and isinstance(card, Monster):
            card.attack *= 2
            card.defense *= 2


# --- LAND TARGETING ---------------------------------------------------------

class ConsecrateGround(Sorcery):
    name = "Consecrate Ground"
    text = "Destroy an enemy land."
    activation_needs = ["left"]
    role = "white"

    def __init__(self, owner):
        super().__init__('consecrate_ground', owner, image='/static/cards/consecrate_ground.png', mana=2)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_land_target", owner="opponent", zone="land",
                     as_key="pos"),
            StepSpec(kind="apply_effect", apply_method="do_shatter")
        ]

    def do_shatter(self, game, _pos, user_id):
        x, y = game.interaction.temp["pos"]
        land = game.land_board[x][y]
        if land and land.owner != user_id:
            game.land_board[x][y] = None


# --- SACRIFICE / COSTED SELECTION ------------------------------------------

class BloodTithe(Sorcery):
    name = "Blood Tithe"
    text = "Sacrifice one of your monsters; gain 2 mana."
    activation_needs = ["back"]
    role = "black"

    def __init__(self, owner):
        super().__init__('blood_tithe', owner, image='/static/cards/blood_tithe.png', mana=1)

    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="self", zone="board",
                     filter={"require_monster": True}, as_key="sac"),
            StepSpec(kind="apply_effect", apply_method="do_sac_gain")
        ]

    def do_sac_gain(self, game, _pos, user_id):
        print(f"[CARD] {time.time():.6f} do_sac_gain user={user_id} temp_keys={list(game.interaction.temp.keys()) if game.interaction else 'NO-IXN'}")
        x, y = game.interaction.temp["sac"]
        card = game.board[x][y]
        print(f"[CARD] {time.time():.6f} sac at {(x, y)} card={getattr(card, 'id', None)} owner={getattr(card, 'owner', None)} mana_before={game.mana[user_id]}")
        if card and card.owner == user_id:
            game.graveyard[user_id].append(card)
            game.board[x][y] = None
            game.mana[user_id] = game.mana.get(user_id, 0) + 2


# --- MULTI-STEP EXAMPLE (already good) -------------------------------------

class RiteOfReclamation(Sorcery):
    name = "Rite of Reclamation"
    text = "Discard a card; destroy an enemy monster; bring back a monster from your graveyard."
    activation_needs = ["forward"]
    role = "black"

    def __init__(self, owner):
        super().__init__('rite_of_reclamation', owner, image='/static/cards/rite.png', mana=3)

    def script(self, game, user_id):
        return [
            StepSpec(kind="discard_from_hand", owner="self", zone="hand", as_key="discarded"),
            StepSpec(kind="select_board_target", owner="opponent", zone="board",
                     filter={"require_enemy": True, "require_monster": True}, as_key="kill_pos"),
            StepSpec(kind="apply_effect", apply_method="do_kill"),
            StepSpec(kind="select_graveyard_card", owner="self", zone="graveyard",
                     filter={"type": "monster"}, as_key="revive_card"),
            StepSpec(kind="apply_effect", apply_method="do_revive"),
        ]

    def do_kill(self, game, _pos, user_id):
        x, y = game.interaction.temp["kill_pos"]
        target = game.board[x][y]
        if target:
            game.graveyard[target.owner].append(target)
            game.board[x][y] = None

    def do_revive(self, game, _pos, user_id):
        cid = game.interaction.temp["revive_card"]
        pool = game.graveyard[user_id]
        for i, c in enumerate(pool):
            if c.id == cid:
                pool.pop(i)
                game.hands[user_id].append(c)
                break


# --- COMPLEX MULTI-STEP SORCERIES -------------------------------------------

class CircleOfRebirth(Sorcery):
    name = "Circle of Rebirth"
    text = "Discard 2 cards; destroy enemy land; summon monster from graveyard; heal all your monsters for 30."
    activation_needs = ["forward", "back"]
    role = "white"
    
    def __init__(self, owner):
        super().__init__('circle_of_rebirth', owner, image='/static/cards/circle_of_rebirth.png', mana=4)
    
    def script(self, game, user_id):
        return [
            StepSpec(kind="discard_from_hand", owner="self", zone="hand", as_key="discard1"),
            StepSpec(kind="discard_from_hand", owner="self", zone="hand", as_key="discard2"),
            StepSpec(kind="select_land_target", owner="opponent", zone="land", as_key="land_pos"),
            StepSpec(kind="apply_effect", apply_method="do_destroy_land"),
            StepSpec(kind="select_graveyard_card", owner="self", zone="graveyard",
                     filter={"type": "monster"}, as_key="summon_monster"),
            StepSpec(kind="select_board_target", owner="self", zone="board", 
                     filter={"require_monster": False}, as_key="summon_pos"),
            StepSpec(kind="apply_effect", apply_method="do_summon"),
            StepSpec(kind="apply_effect", apply_method="do_heal_all")
        ]
    
    def do_destroy_land(self, game, _pos, user_id):
        x, y = game.interaction.temp["land_pos"]
        game.land_board[x][y] = None
    
    def do_summon(self, game, _pos, user_id):
        monster_id = game.interaction.temp["summon_monster"]
        monster_pos = game.interaction.temp["summon_pos"]
        
        # Find and remove monster from graveyard
        pool = game.graveyard[user_id]
        for i, c in enumerate(pool):
            if c.id == monster_id:
                monster = pool.pop(i)
                break
        else:
            return  # Monster not found
        
        # Place on empty board position
        x, y = monster_pos
        x, y = int(x), int(y)
        if not game.board[x][y]:
            game.board[x][y] = monster
    
    def do_heal_all(self, game, _pos, user_id):
        for row in game.board:
            for card in row:
                if card and card.owner == user_id and hasattr(card, 'defense'):
                    card.defense += 30


class VoidNexusRitual(Sorcery):
    name = "Void Nexus Ritual"
    text = "Sacrifice monster; discard sorcery; destroy enemy monster; steal opponent's next draw."
    activation_needs = ["left", "right"]
    role = "black"
    
    def __init__(self, owner):
        super().__init__('void_nexus_ritual', owner, image='/static/cards/void_nexus_ritual.png', mana=5)
    
    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="self", zone="board",
                     filter={"require_monster": True}, as_key="sacrifice_monster"),
            StepSpec(kind="apply_effect", apply_method="do_sacrifice"),
            StepSpec(kind="discard_from_hand", owner="self", zone="hand", as_key="discard_sorcery"),
            StepSpec(kind="discard_from_hand", owner="self", zone="hand", as_key="discard_sorcery2"),
            StepSpec(kind="select_board_target", owner="opponent", zone="board",
                     filter={"require_enemy": True, "require_monster": True}, as_key="destroy_target"),
            StepSpec(kind="apply_effect", apply_method="do_destroy_enemy"),
            StepSpec(kind="apply_effect", apply_method="do_steal_next_draw")
        ]
    
    def do_sacrifice(self, game, _pos, user_id):
        x, y = game.interaction.temp["sacrifice_monster"]
        card = game.board[x][y]
        if card and card.owner == user_id:
            game.graveyard[user_id].append(card)
            game.board[x][y] = None
    
    def do_destroy_enemy(self, game, _pos, user_id):
        x, y = game.interaction.temp["destroy_target"]
        target = game.board[x][y]
        if target:
            game.graveyard[target.owner].append(target)
            game.board[x][y] = None
    
    def do_steal_next_draw(self, game, _pos, user_id):
        opponent_id = '2' if user_id == '1' else '1'
        if game.decks[opponent_id]:
            stolen_card = game.decks[opponent_id].pop(0)
            game.hands[user_id].append(stolen_card)


class ElementalConvergence(Sorcery):
    name = "Elemental Convergence"
    text = "Choose monster; sacrifice land; summon monster from deck; boost all monsters of same role."
    activation_needs = ["forward", "left", "right"]
    role = "blue"
    
    def __init__(self, owner):
        super().__init__('elemental_convergence', owner, image='/static/cards/elemental_convergence.png', mana=6)
    
    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="any", zone="board",
                     filter={"require_monster": True}, as_key="target_monster"),
            StepSpec(kind="select_land_target", owner="self", zone="land", as_key="sacrifice_land"),
            StepSpec(kind="apply_effect", apply_method="do_destroy_owner_land"),
            StepSpec(kind="select_deck_card", owner="self", zone="deck",
                     filter={"type": "monster", "max_cost": 3}, as_key="summon_elemental"),
            StepSpec(kind="select_board_target", owner="self", zone="board", 
                     filter={"require_monster": False}, as_key="place_elemental"),
            StepSpec(kind="apply_effect", apply_method="do_summon_elemental"),
            StepSpec(kind="apply_effect", apply_method="do_boost_role_mates")
        ]
    
    def do_destroy_owner_land(self, game, _pos, user_id):
        x, y = game.interaction.temp["sacrifice_land"]
        if game.land_board[x][y]:
            game.land_board[x][y] = None
    
    def do_summon_elemental(self, game, _pos, user_id):
        elemental_id = game.interaction.temp["summon_elemental"]
        elemental_pos = game.interaction.temp["place_elemental"]
        
        # Find and remove elemental from deck
        deck = game.decks[user_id]
        for i, c in enumerate(deck):
            if c.id == elemental_id:
                elemental = deck.pop(i)
                break
        else:
            return  # Elemental not found
        
        # Place on empty board position
        x, y = elemental_pos
        x, y = int(x), int(y)
        if not game.board[x][y]:
            game.board[x][y] = elemental
    
    def do_boost_role_mates(self, game, _pos, user_id):
        # Get role of the original target monster
        monster_pos = game.interaction.temp["target_monster"]
        mx, my = monster_pos
        target_monster = game.board[int(mx)][int(my)]
        
        if not target_monster or not hasattr(target_monster, 'role'):
            return
            
        role_to_boost = target_monster.role
        
        # Boost all monsters of the same role on the board
        for row in game.board:
            for card in row:
                if (card and hasattr(card, 'role') and 
                    card.role == role_to_boost and hasattr(card, 'attack')):
                    card.attack += 25
                    if hasattr(card, 'defense'):
                        card.defense += 15


class BurningSacrifice(Sorcery):
    name = "Burning Sacrifice"
    text = "Sacrifice monster; steal monster from deck; destroy enemy land."
    activation_needs = ["forward", "right"]
    role = "red"
    
    def __init__(self, owner):
        super().__init__('burning_sacrifice', owner, image='/static/cards/burning_sacrifice.png', mana=3)
    
    def script(self, game, user_id):
        return [
            StepSpec(kind="select_board_target", owner="self", zone="board",
                     filter={"require_monster": True}, as_key="sacrifice_target"),
            StepSpec(kind="apply_effect", apply_method="do_sacrifice_monster"),
            StepSpec(kind="select_deck_card", owner="opponent", zone="deck",
                     filter={"type": "monster", "min_cost": 2}, as_key="steal_monster"),
            StepSpec(kind="apply_effect", apply_method="do_steal_to_hand"),
            StepSpec(kind="select_land_target", owner="opponent", zone="land", as_key="destroy_land"),
            StepSpec(kind="apply_effect", apply_method="do_destroy_land_effect")
        ]
    
    def do_sacrifice_monster(self, game, _pos, user_id):
        x, y = game.interaction.temp["sacrifice_target"]
        card = game.board[x][y]
        if card and card.owner == user_id:
            # Gain 1 mana for sacrifice
            game.mana[user_id] = game.mana.get(user_id, 0) + 1
            game.graveyard[user_id].append(card)
            game.board[x][y] = None
    
    def do_steal_to_hand(self, game, _pos, user_id):
        monster_id = game.interaction.temp["steal_monster"]
        opponent_id = '2' if user_id == '1' else '1'
        
        # Find and steal from opponent's deck
        deck = game.decks[opponent_id]
        for i, c in enumerate(deck):
            if c.id == monster_id and hasattr(c, 'mana') and c.mana >= 2:
                stolen_monster = deck.pop(i)
                game.hands[user_id].append(stolen_monster)
                break
    
    def do_destroy_land_effect(self, game, _pos, user_id):
        x, y = game.interaction.temp["destroy_land"]
        if game.land_board[x][y]:
            game.land_board[x][y] = None
            # Gain 1 mana for destroying enemy land
            game.mana[user_id] = game.mana.get(user_id, 0) + 1