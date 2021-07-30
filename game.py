"""
    File name: game.py
    Author: Aris Kalgreadis
    Date created: 30/07/2021
    Python Version: 3.7
"""

import random
from collections import defaultdict


class Card(object):
    # Single card object
    def __init__(self, suit: str, rank: int):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other) -> bool:
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False

    def __str__(self) -> str:
        return self.suit + '-' + str(self.rank)


class Deck(object):
    # Deck of cards
    def __init__(self):
        self.cards = []
        suits = ['A', 'B', 'C', 'D', 'E']
        for r in range(4):
            for s in suits:
                self.cards.append(Card(s, r))
        random.shuffle(self.cards)


class Player(object):
    # Each player in the game
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.suits = defaultdict(int)
        self.memory = defaultdict(list)
        self.score = 0

    # Add card to players hand
    def addCardToHand(self, card: Card):
        self.hand.append(card)
        self.suits[card.suit] += 1

    # Add to players memory cards that asked in previous rounds and they did not have
    def addToMemory(self, card: Card, player_name: str):
        # Remove previous memory of this card
        for key, value in self.memory.items():
            if card in value:
                value.remove(card)

        # Add recent memory
        self.memory[player_name].append(card)

    # Check if a player has a quartet in his hand. If yes put it on the table and remove it from the hand
    def checkForQuartet(self):
        for k in list(self.suits.keys()):
            if self.suits[k] == 4:
                quartet = []
                for c in list(self.hand):
                    if c.suit == k:
                        quartet.append(c)
                        self.hand.remove(c)
                del self.suits[k]
                print('{} has a quartet!'.format(self.name))
                print('{}  is putting down {}'.format(
                    self.name, ' '.join(map(str, quartet))))
                self.score += 1

    # Select a card to ask
    def selectCard(self) -> Card:
        # Find all possible cards the player can ask
        cards_to_ask = []
        for key, value in self.suits.items():
            ranks_available = [c.rank for c in self.hand if c.suit == key]
            ranks_to_get = [value for value in list(
                range(4)) if value not in ranks_available]

            for r in ranks_to_get:
                cards_to_ask.append(Card(key, r))

        print("There are {} cards {} can ask for".format(
            len(cards_to_ask), self.name))
        # Return a random choice from all available cards
        return random.choice(cards_to_ask)

    # Checks if requested card is in players hand and if so remove it
    def getCard(self, card: Card) -> bool:
        if card in self.hand:  # if card in hand, returns count and removes the card from hand
            self.hand.remove(card)
            self.suits[card.suit] -= 1

            if self.suits[card.suit] == 0:  # if last delete card key from hand
                del self.suits[card.suit]
            return True
        else:
            return False

    # Helper function to print players hand
    def displayHand(self):
        print(self.name, ": ", ' '.join(map(str, self.hand)))

    # Returns true is player cannot play any more in this game
    def finishedPlaying(self) -> bool:
        return len(self.hand) == 0


class PlayQuartet(object):
    # A class to play the quartet game
    def __init__(self):
        self.deck = Deck()  # initialize deck

        self.players = []  # initialize and add 4 players
        names = ['Anna', 'Bert', 'Claudia', 'Dan']
        for n in names:
            self.players.append(Player(n))

    # Returns true when games end condition has been met
    def endOfPlayCheck(self) -> bool:
        return all(list(map(lambda x: x.finishedPlaying(), self.players)))

    # Play the game
    def play(self):
        # Deal cards
        for i in range(len(self.deck.cards)):
            player_index = i % len(self.players)
            self.players[player_index].addCardToHand(self.deck.cards[i])

        # Check for Quartets on first hand
        for p in self.players:
            p.checkForQuartet()

        # Choose randomly the first player
        active_player = random.choice(self.players)
        while not self.endOfPlayCheck():
            for p in self.players:
                p.displayHand()

            print("It's {}'s turn.".format(active_player.name))
            available_players = [x for x in self.players if x !=
                                 active_player and not x.finishedPlaying()]

            # Select card to ask
            card = active_player.selectCard()

            # Select opponent - Random selection with memory
            idx_list = []
            if len(available_players) == 1:
                idx = 0
            else:
                for i in range(len(available_players)):
                    if card not in active_player.memory[available_players[i].name]:
                        idx_list.append(i)
                idx = random.choice(idx_list)

            opponent = available_players[idx]

            print("{} is asking {} for {}".format(
                active_player.name, opponent.name, str(card)))
            # Ask for the card from selected opponent
            result = opponent.getCard(card)

            if result:  # If player had requested card add it to hand and check finish turn conditions
                active_player.addCardToHand(card)
                print("{} gets {} from {}".format(
                    active_player.name, str(card), opponent.name))

                active_player.checkForQuartet()

                if active_player.finishedPlaying():
                    print('{} is out of cards'.format(active_player.name))
                    # If the last player you took a card from is also finished set the previous player as the next
                    if opponent.finishedPlaying():
                        print('{} is out of cards'.format(opponent.name))
                        active_player = available_players[idx - 1]
                    else:
                        active_player = opponent

            else:  # If player did not have the card end the turn and add it to his memory
                active_player.addToMemory(card, opponent.name)
                print("{} does not have {}".format(opponent.name, str(card)))
                print("It's now {}'s turn".format(opponent.name))
                active_player = opponent

            print("")

        print("All players out of cards - game is over!")
        for p in self.players:
            print("{} has {} quartets".format(p.name, p.score))


if __name__ == "__main__":
    game = PlayQuartet()
    game.play()
