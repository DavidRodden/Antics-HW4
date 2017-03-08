import random
import sys

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *


## by yours truly

##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #
    # pool - current population of genes
    # poolIndex - index pointing to the current population in the pool
    # currentPopFitness - current population being examined
    #
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Genetic")
        self.pool = []
        self.poolIndex = None
        self.currentPopFitness = None

    # initialize the population of genes with random values
    # then resets the fitness list to default values
    #
    def initializeGenePopulation(self, popSize):
        # index set to 0 for the initialization of a population
        self.poolIndex = 0
        # gene includes tuples of board position, random large number
        gene = []
        for g in range(0, popSize):
            # grass and hills
            for i in range(0, 10):
                for j in range(0, 4):
                    gene.append(((i, j), random.uniform(sys.float_info.min, sys.float_info.max)))
            # food
            for i in range(0, 10):
                for j in range(6, 10):
                    gene.append(((i, j), random.uniform(sys.float_info.min, sys.float_info.max)))
            # add gene with respective highscore to the gene pool
            self.pool.append((gene, 0))
            # reset list to default values?

    # generates two child genes from mother and father parent genes
    # does not yet include a mutation process
    #
    # length of mother & father should be equal as the size is based on the number of tiles
    def mateGenes(self, mother, father):
        delimiter = len(mother) / 2
        ourSplit = random.randint(0, delimiter)
        theirSplit = random.randint(delimiter, len(mother))
        children = [mother[:ourSplit] + father[ourSplit: delimiter] + mother[delimiter:theirSplit] + father[theirSplit:], \
               father[:ourSplit] + mother[ourSplit: delimiter] + father[delimiter: theirSplit] + mother[theirSplit:]]
        for child in children:
            mutate = random.uniform(0,1)
            if mutate > 0.8:
                index = random.randint(0,len(child)-1)
                newval = random.uniform(sys.float_info.min, sys.float_info.max)
                child[index] = newval
        return children
                

    # method to generate the next generation of genes from the old one
    # returns the top 5% of the population based on the maximum score obtained from a gene
    def generateNextGenes(self):
        return sorted(self.pool, key=lambda x: x[1])[:len(self.pool) / 20]

    ##
    # getPlacement
    #
    # Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    # Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    # Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        # implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:  # stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    # Choose any x location
                    x = random.randint(0, 9)
                    # Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    # Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        # Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    # getMove
    # Description: Gets the next move from the Player.
    #
    # Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    # Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0, len(moves) - 1)];

        # don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0, len(moves) - 1)];

        return selectedMove

    ##
    # getAttack
    # Description: Gets the attack to be made from the Player
    #
    # Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    # override Player.py function
    # Update the fitness score of the current gene depending on whether the agent has won or lost
    # Judge whether the current gene's fitness has been fully evaluated & advance to next gene
    def registerWin(self, hasWon):
        # currentPopFitness is based on the highest score attained by the gene
        self.currentPopFitness.append(self.pool[self.poolIndex][1])
        return hasWon
