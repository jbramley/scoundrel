from enum import StrEnum

from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt


class MainMenuAction(StrEnum):
    PLAY_GAME = "p"
    SHOW_RULES = "s"
    QUIT = "q"


class MainMenuValidator(Validator):
    def validate(self, document: Document) -> None:
        text = document.text

        try:
            MainMenuAction(text.lower())
        except ValueError:
            raise ValidationError(message=f"Invalid option: {text}")


def main_menu() -> MainMenuAction:
    print("""SCOUNDREL!

An implementation of Scoundrel, originally designed by Zach Gage and Kurt Bieg.
Learned about from Riffle Shuffle & Roll on YouTube https://www.youtube.com/watch?v=7fP-QLtWQZs

What Would you like to do?
 [P]lay a game
 [S]how the rules
 [Q]uit
    """)
    return MainMenuAction(
        prompt("Your choice: ", validator=MainMenuValidator()).lower()
    )
