from Controller import Controller
from Game import Game

def main():
    print("Hello")
    controller = Controller()
    game = Game(controller)

    controller.refresh_frame()

    #assert game.is_rules_open == False
    print(game.matching_symbol_count('symbolA'))
    

if __name__ == "__main__":
    main()
