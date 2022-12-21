from Controller import Controller
from Game import Game

def main():
    print("Hello")
    controller = Controller()
    game = Game(controller)

    controller.refresh_frame()

    #balance_before = game.get_balance()
    #print(balance_before)

    #game.click_object('play')

    game.click_object('symbol10')
    print(game.matching_symbol_count('symbol10'))
    

if __name__ == "__main__":
    main()
