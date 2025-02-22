import random
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto, StrEnum
from typing import final

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError

MAX_HEALTH: final = 20


class ScoundrelCardType(Enum):
    ENEMY = auto()
    WEAPON = auto()
    HEALTH = auto()


class ScoundrelCardSuit(StrEnum):
    HEART = "♥"
    DIAMOND = "♦"
    SPADE = "♠"
    CLUB = "♣"


@dataclass
class ScoundrelCard:
    type_: ScoundrelCardType
    value: int
    suit: ScoundrelCardSuit

    def __str__(self):
        value = {11: "J", 12: "Q", 13: "K", 14: "A"}.get(self.value, self.value)
        return f"{value}{self.suit}"


class ScoundrelDeck:
    def __init__(self):
        self.deck = deque(
            [
                ScoundrelCard(ScoundrelCardType.WEAPON, i, ScoundrelCardSuit.DIAMOND)
                for i in range(2, 11)
            ]
            + [
                ScoundrelCard(ScoundrelCardType.HEALTH, i, ScoundrelCardSuit.HEART)
                for i in range(2, 11)
            ]
            + [
                ScoundrelCard(ScoundrelCardType.ENEMY, i, ScoundrelCardSuit.SPADE)
                for i in range(2, 15)
            ]
            + [
                ScoundrelCard(ScoundrelCardType.ENEMY, i, ScoundrelCardSuit.CLUB)
                for i in range(2, 15)
            ]
        )

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self, num: int) -> list[ScoundrelCard]:
        return [self.deck.popleft() for _ in range(min(num, len(self.deck)))]

    def __len__(self):
        return len(self.deck)

    def __bool__(self):
        return len(self.deck) > 0


class ScoundrelWeapon:
    def __init__(self, card: ScoundrelCard):
        self.last_enemy: ScoundrelCard | None = None
        assert card.type_ == ScoundrelCardType.WEAPON
        self.card = card

    def can_attack(self, other: ScoundrelCard) -> bool:
        if self.last_enemy is None:
            return True
        return self.last_enemy.value > other.value

    @property
    def value(self):
        return self.card.value

    def __str__(self):
        return str(self.card)


class ScoundrelPlayer:
    def __init__(self):
        self.health = MAX_HEALTH
        self.weapon: ScoundrelWeapon | None = None

    def __bool__(self):
        return self.health > 0


class ScoundrelCardPickerValidator(Validator):
    def __init__(self, num_cards: int):
        self.num_cards = num_cards
        super().__init__()

    def validate(self, document: Document):
        text = document.text
        if not text.isdigit():
            raise ValidationError(message=f"Invalid option: {text}")
        if not (0 < int(text) < self.num_cards):
            raise ValidationError(message=f"Invalid option: {text}")


class YesNoValidator(Validator):
    def validate(self, document: Document):
        text = document.text
        if text.lower() not in ("y", "yes,n", "no"):
            raise ValidationError(message=f"Invalid option: {text}")


def play_game():
    deck = ScoundrelDeck()
    deck.shuffle()
    player = ScoundrelPlayer()

    def bottom_toolbar():
        toolbar = f'<b><style bg="red">Health: </style></b>{player.health:02d} '
        if player.weapon and player.weapon:
            toolbar += f'<b><style bg="blue">Weapon: </style></b>{player.weapon} '
            if player.weapon.last_enemy:
                toolbar += f"(<b>Last Enemy: </b>{player.weapon.last_enemy})"

        return HTML(toolbar)

    prompt_session = PromptSession(bottom_toolbar=bottom_toolbar)
    cards_in_play = 0
    cards_in_room = []
    fled_last_turn = False
    while deck and player:
        cards_in_room += deck.deal(4 - cards_in_play)
        cards_in_play = len(cards_in_room)

        has_consumed_potion_this_turn = False
        still_fighting = True

        print("Current room: " + " ".join(map(str, cards_in_room)))
        did_flee = False
        while still_fighting:
            can_move_on = cards_in_play == 1
            can_flee = not fled_last_turn

            def is_valid(text):
                try:
                    return 0 < int(text) <= cards_in_play
                except ValueError:
                    return (text.lower() == "g" and can_move_on) or (
                        text.lower() == "f" and can_flee
                    )

            prompt_text = "What would you like to do?\n"
            prompt_text += "\n".join(
                f"{i + 1}) Take the {card}" for i, card in enumerate(cards_in_room)
            )
            if can_move_on:
                prompt_text += "\n[G]o to the next room"
            if can_flee:
                prompt_text += "\n[F]lee the room"
            print(prompt_text)
            choice = prompt_session.prompt(
                "Your move: ",
                validator=Validator.from_callable(
                    is_valid, error_message="Invalid input"
                ),
            )
            if choice == "g":
                break
            if choice == "f":
                random.shuffle(cards_in_room)
                deck.deck.extend(cards_in_room)
                cards_in_room.clear()
                cards_in_play = 0
                did_flee = True
                break
            card = cards_in_room[int(choice) - 1]
            match card.type_:
                case ScoundrelCardType.ENEMY:
                    if player.weapon and player.weapon.can_attack(card):
                        yes_no = prompt_session.prompt(
                            "Would you like to fight with your weapon? ",
                            validator=YesNoValidator(),
                        )
                        if yes_no.startswith("y"):
                            damage = max(card.value - player.weapon.value, 0)
                            if damage == 0:
                                print(
                                    f"You deftly circle the enemy and slash it to pieces with your {player.weapon}"
                                )
                            else:
                                print(
                                    "You engage the enemy in mortal combat and end its life"
                                )
                            player.weapon.last_enemy = card
                        else:
                            print(
                                "You put your weapon to the side and pummel the enemy with your bare fists"
                            )
                            damage = card.value
                    else:
                        print("You pummel the enemy with your bare fists")
                        damage = card.value
                    player.health -= damage
                case ScoundrelCardType.HEALTH:
                    if not has_consumed_potion_this_turn:
                        player.health = min(MAX_HEALTH, player.health + card.value)
                        has_consumed_potion_this_turn = True
                        if player.health == MAX_HEALTH:
                            print(
                                "After finishing the potion, you smash the bottle to the floor and let out a guttural roar: ROAARRRRRR!!!"
                            )
                        else:
                            print("You drink the potion and feel better.")
                    else:
                        print(
                            "You go to drink the potion and it slips from your hands and shatters on the floor. A handful of dead roaches come back to life and skitter off."
                        )
                    pass
                case ScoundrelCardType.WEAPON:
                    if player.weapon:
                        print(
                            f"You casually discard your {player.weapon} as you eye the gleaming {card} before you."
                        )
                    player.weapon = ScoundrelWeapon(card)
                    print(
                        f"You hold the {card} in your hands and swish it about a few times, testing its balance."
                    )

            cards_in_room.remove(card)
            cards_in_play -= 1
            if player.health == 0:
                print("You died")
                break
        fled_last_turn = did_flee

        # For each turn:
        # 1. Deal out up to min(4, len(deck)) cards
        # 2. Player can run (if did not run last turn)
        # 3. Otherwise player must pick up at least 3 cards
        # 4. If player health <= 0, end turn and game
    if player and not deck:
        print(
            "You make your way out of the dungeon, dusting yourself off. You have emerged victorious!"
        )
