from card_types import Monster, Sorcery, Land

# prompt - great, now let's generate some images, they should be high quality, square
#
# style should be evocative of old school anime, but also old school western animation, though very realistic and very stylized, little line work, full body shots, and a lot of camera perspective, let's try bonecrawler first

class Bonecrawler(Monster):  # Formerly: Pawn
    name = "Bonecrawler"
    movement = {
        "forward": 1,
        'left': 1
    }
    original_attack = 100
    original_defense = 200

    def __init__(self, owner):
        super().__init__(
            card_id='bonecrawler',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/bonecrawler.png',
            mana=1
        )

#
class ShadowVine(Monster):  # Formerly: DiagonalRanger
    name = "Shadow Vine"
    movement = {
        "forward": 'any',
        "forward-left": 'any',
        "back-right": 'any',
        # "back-right": 'any'
    }
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
        "forward": 'any',
        "forward-left": 'any',
        # "forward-right": 'any',
        "right": 'any',
        "back-left": 'any',
        # "left": 'any',
        # "back-right": 'any',
        "back": 'any'
    }
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
        "forward": 'any',
        "back-left": 1,
        "back": 1
    }
    original_attack = 180
    original_defense = 150

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
        "forward": 'any',
        "back": 'any',
        "back-left": 'any',
        "right": 'any'
    }

    original_attack = 230
    original_defense = 130

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
        "left": 'any',
        "right": 'any',
        "back-left": 1,
        "back-right": 1
    }

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
        "forward": 'any',
        "left": 1,
        "right": 1,
        "back-left": 'any',
        "back-right": 'any',
        'back': 1
    }
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
        "forward-right": 'any',
        "left": 1,
        "right": 1,
        "back-left": 1,
        "back-right": 1
    }
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
        'forward': 'any',
        "forward-right": 1,
        "forward-left": 1,
        "back-left": 1,
        "back-right": 1
    }

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
        "forward": 'any',
        "back": 1,
        "left": 1,
        "right": 1
    }
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
        "forward-left": 'any',
        "forward-right": 'any',
        "back-left": 1,
        "back-right": 1
    }
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
        "forward": 'any',
        "left": 'any',
        "right": 'any',
        "back": 'any'
    }
    original_attack = 200
    original_defense = 250

    def __init__(self, owner):
        super().__init__(
            card_id='celestial_titan',
            owner=owner,
            attack=self.original_attack,
            defense=self.original_defense,
            image='/static/cards/celestial_titan.png',
            mana=6
        )





class BlazingRain(Sorcery):
    name = 'Blazing Rain'
    text = "Weaken all opponent's DEF by 50."
    activation_needs = ["back"]
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
    activation_needs = ["forward", "forward-right"]
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

    def __init__(self, owner):
        super().__init__('arcane_tempest', owner, image='/static/cards/arcane_tempest.png', mana=2)

    def affect_board(self, game, target_pos, user_id):
        for row in game.board:
            for card in row:
                if card and card.owner != user_id and isinstance(card, Monster):
                    card.attack -= 40




class TargetedDestruction(Sorcery):
    name = "Targeted Destruction"
    text = "Choose and destroy an enemy monster."
    activation_needs = ['forward-right']

    def __init__(self, owner):
        super().__init__(
            card_id="targeted_destruction",
            owner=owner,
            image="/static/cards/targeted_destruction.png",
            mana=2
        )

    def requires_additional_input(self):
        return True

    def get_valid_targets(self, game, user_id):
        return [
            [x, y] for x, row in enumerate(game.board)
            for y, card in enumerate(row)
            if card and card.owner != user_id and isinstance(card, Monster)
        ]

    def resolve_with_input(self, game, user_id, pos):
        x, y = pos
        card = game.board[x][y]
        if card and card.owner != user_id:
            game.graveyard[card.owner].append(card)
            game.board[x][y] = None
            return True, 'Targeted Destruction has resolved'
        else:
            return False, 'Invalid target'


class EmpoweringLight(Sorcery):
    name = "Empowering Light"
    text = "Choose a monster to increase its ATK by 50."
    activation_needs = ['back-left']  # Optional highlight rules

    def __init__(self, owner):
        super().__init__(
            card_id="empowering_light",
            owner=owner,
            image="/static/cards/empowering_light.png",
            mana=2
        )

    def requires_additional_input(self):
        return True

    def get_valid_targets(self, game, user_id):
        return [
            [x, y]
            for x, row in enumerate(game.board)
            for y, card in enumerate(row)
            if card and isinstance(card, Monster)
        ]

    def resolve_with_input(self, game, user_id, pos):
        x, y = pos
        card = game.board[x][y]
        if card:
            card.attack += 50
            return True, f"{card.name} gained 500 ATK!"
        return False, "Invalid target"


class FrostbiteCurse(Sorcery):
    name = "Frostbite Curse"
    text = "Choose a monster to decrease its DEF by 30."
    activation_needs = ['forward']

    def __init__(self, owner):
        super().__init__(
            card_id="frostbite_curse",
            owner=owner,
            image="/static/cards/frostbite_curse.png",
            mana=2
        )

    def requires_additional_input(self):
        return True

    def get_valid_targets(self, game, user_id):
        return [
            [x, y]
            for x, row in enumerate(game.board)
            for y, card in enumerate(row)
            if card and isinstance(card, Monster)
        ]

    def resolve_with_input(self, game, user_id, pos):
        x, y = pos
        card = game.board[x][y]
        if card:
            card.defense -= 30
            return True, f"{card.name} lost 300 DEF!"
        return False, "Invalid target"


class MindSeize(Sorcery):
    name = "Mind Seize"
    text = "Choose an enemy monster to take control of it."
    activation_needs = ['back', 'back-right']

    def __init__(self, owner):
        super().__init__(
            card_id="mind_seize",
            owner=owner,
            image="/static/cards/mind_seize.png",
            mana=2
        )

    def requires_additional_input(self):
        return True

    def get_valid_targets(self, game, user_id):
        return [
            [x, y]
            for x, row in enumerate(game.board)
            for y, card in enumerate(row)
            if card and card.owner != user_id and isinstance(card, Monster)
        ]

    def resolve_with_input(self, game, user_id, pos):
        x, y = pos
        card = game.board[x][y]
        if card and card.owner != user_id:
            card.owner = user_id
            return True, f"You took control of {card.name}!"
        return False, "Invalid target"


class PowerSurge(Sorcery):
    name = "Power Surge"
    text = "Choose a monster to double its ATK and DEF."
    activation_needs = ['forward', 'left']

    def __init__(self, owner):
        super().__init__(
            card_id="power_surge",
            owner=owner,
            image="/static/cards/power_surge.png",
            mana=2
        )

    def requires_additional_input(self):
        return True

    def get_valid_targets(self, game, user_id):
        return [
            [x, y]
            for x, row in enumerate(game.board)
            for y, card in enumerate(row)
            if card and isinstance(card, Monster)
        ]

    def resolve_with_input(self, game, user_id, pos):
        x, y = pos
        card = game.board[x][y]
        if card:
            card.attack *= 2
            card.defense *= 2
            return True, f"{card.name}'s ATK and DEF were doubled!"
        return False, "Invalid target"

class VolcanicRift(Land):
    name = "Volcanic Rift"
    text = "Burns an opponent's monster for 50 DEF when it steps on this tile."
    creation_needs = ["forward", 'back']

    def __init__(self, owner):
        super().__init__('volcanic_rift', owner, image='/static/cards/volcanic_rift.png', mana=2)

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

    def __init__(self, owner):
        super().__init__('sacred_grove', owner, image='/static/cards/sacred_grove.png', mana=3)

    def on_turn_start(self, game, pos, monster):
        if monster.owner == self.owner:
            monster.defense += 30


class FrozenBarrier(Land):
    name = "Frozen Barrier"
    text = "Opponent's monsters cannot move across this tile."
    creation_needs = ["back-right", 'forward']

    def __init__(self, owner):
        super().__init__('frozen_barrier', owner, image='/static/cards/frozen_barrier.png', mana=1)

    def blocks_movement(self, monster):
        if monster.owner != self.owner:
            return True
        return False


class StormNexus(Land):
    name = "Storm Nexus"
    text = "Reduces the ATK of enemy monsters that land on this tile by 40."
    creation_needs = ["back-left"]

    def __init__(self, owner):
        super().__init__('storm_nexus', owner, image='/static/cards/storm_nexus.png', mana=2)

    def on_enter(self, game, pos, monster):
        if monster.owner != self.owner:
            monster.attack -= 40


class WastelandMine(Land):
    name = "Wasteland Mine"
    text = "An opponents monster going over or landing on this land loses 30 ATK and DEF"
    creation_needs = ["right"]

    def __init__(self, owner):
        super().__init__('wasteland_mine', owner, image='/static/cards/wasteland_mine.png', mana=3)

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
    creation_needs = ["forward-right", 'right']

    def __init__(self, owner):
        super().__init__('rule_of_the_meek', owner, image='/static/cards/rule_of_the_meek.png', mana=1)

    def blocks_movement(self, monster):
        if monster.owner != self.owner and ((monster.defense > 150) and (monster.attack > 150)):
            return True
        return False