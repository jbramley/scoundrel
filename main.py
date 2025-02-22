from game import play_game
from main_menu import MainMenuAction, main_menu


def main():
    while True:
        action = main_menu()
        match action:
            case MainMenuAction.PLAY_GAME:
                play_game()
            case MainMenuAction.SHOW_RULES:
                show_rules()
            case MainMenuAction.QUIT:
                break


def show_rules():
    print("rules")


if __name__ == "__main__":
    main()
