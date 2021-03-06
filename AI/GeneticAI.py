import random
import sys
import time

sys.path.append("..")  # so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *

##
# AIPlayer
# Description: The responsbility of this class is to interact with the game by
# deciding a valid move based on a given game state. This class has methods that
# will be implemented by students in Dr. Nuxoll's AI course.
#
# Authors: David Rodden, Sara Perkins
# Version: 9 March 2017
#
# Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):
    ##
    # __init__
    # Description: Creates a new Player
    #
    # Parameters:
    #   inputPlayerId - The id to give the new player (int)
    #   pool - current population of genes
    #   poolIndex - index pointing to the current population in the pool
    #   currentPopFitness - current population being examined
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer, self).__init__(inputPlayerId, "Genetic Al")
        self.pool = []
        self.poolIndex = 0
        self.currentPopFitness = None
        self.currgenescores = []

        ###
        self.max = 200000000      # max score for a win
        self.popSize = 20 
        self.lastStart = -5       # last start time of a game
        self.numGamesPerGene = 5  # number of games to play per gene
        self.poolStates = []      # need to save states in parallel with the pool to print
        self.topCutoff = 5
        self.evidenceFile = "CS421_HW4_EvidenceFile_perkinss18_roddend17.txt"

        self.initializeGenePopulation()

    ##
    # initializeGenePopulation
    # initialize the population of genes with random values
    # then resets the fitness list to default values
    #
    # Parameters and Return: None
    ##
    def initializeGenePopulation(self):
        # index set to 0 for the initialization of a population
        self.poolIndex = 0
        # gene includes tuples of board position, random large number
        gene = []
        for g in range(0, self.popSize):
            # grass and hills
            for x in range(0, 10):
                for y in range(0, 4):
                    gene.append([(x, y), random.randint(0, self.max / 2)])
            # food
            for x in range(0, 10):
                for y in range(6, 10):
                    gene.append([(x, y), random.randint(0, self.max / 2)])
            # add gene with respective highscore to the gene pool
            self.pool.append([gene, 0])
            gene = []

    ##
    # mateGenes
    # generates two child genes from mother and father parent genes
    # 1 round of crossover for each half of the gene, small chance mutation
    #
    # Parameters:
    #   mom - gene parent 1
    #   dad - gene parent 2
    #
    # Return: array containing 2 children
    ##
    def mateGenes(self, mom, dad):
        # get the gene
        mother = mom[0]
        father = dad[0]

        delimiter = len(mother) / 2  # 40
        ourSplit = random.randint(0, delimiter)
        theirSplit = random.randint(delimiter, len(mother))

        gene1 = mother[:ourSplit] + father[ourSplit: delimiter] + mother[delimiter:theirSplit] + father[theirSplit:]
        gene2 = father[:ourSplit] + mother[ourSplit: delimiter] + father[delimiter: theirSplit] + mother[theirSplit:]
        children = [[gene1, 0], [gene2, 0]]
        for child in children:
            mutate = random.uniform(0, 1)
            if mutate > 0.8:
                index = random.randint(0, len(child[0]) - 1)
                newval = random.randint(0, self.max / 2)
                child[0][index][1] = newval  # value change -- [gene -- [(point,value),...], score]
        return children

    ##
    # generateNextGenes
    # method to generate the next generation of genes from the old one
    # returns the next generation of genes based on the top 5 of the population based
    # on the average score obtained from a gene
    #
    # Parameters: None
    #
    # Return the Next generation
    ##
    def generateNextGenes(self):
        top = sorted(self.pool, key=lambda x: x[1], reverse=True)[:self.topCutoff]

        nextGen = []
        for i in range(0, len(self.pool) / 2):
            m = random.randint(0, len(self.pool) - 1)
            mother = self.pool[m]
            f = random.randint(0, len(self.pool) - 1)
            father = self.pool[f]

            # save the fittest
            fit = random.uniform(0, 1)
            if fit > 0.5:
                m = random.randint(0, len(top) - 1)
                mother = top[m]
            fit = random.uniform(0, 1)
            if fit > 0.5:
                f = random.randint(0, len(top) - 1)
                father = top[f]

            for child in self.mateGenes(mother, father):
                nextGen.append(child)

        return nextGen

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
            self.lastStart = time.clock()  # set the time of the last start of the game
            places = sorted(self.pool[self.poolIndex][0][:40], key=lambda x: x[1], reverse=True)[:11]
            return [p[0] for p in places]
        elif currentState.phase == SETUP_PHASE_2:  # stuff on foe's side
            foodloc = []
            sortedtheirs = sorted(self.pool[self.poolIndex][0][40:], key=lambda x: x[1], reverse=True)
            for loc in sortedtheirs:
                if getConstrAt(currentState, loc[0]) is None:
                    foodloc.append(loc[0])
                    if len(foodloc) == 2:
                        break
            return foodloc
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
        # grab the initial state
        if self.poolIndex == len(self.poolStates):
            self.poolStates.append(currentState)

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
    #
    # Return: random available enemy
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        # Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    # registerWin
    # override Player.py function
    # Update the fitness score of the current gene depending on whether the agent has won or lost
    # Judge whether the current gene's fitness has been fully evaluated & advance to next gene
    # print fittest gene with each change in generation
    #
    # Parameter:
    #   hasWon - true if you won, false if otherwise
    #
    # Return: hasWon
    ##
    def registerWin(self, hasWon):
        # stop the clock
        survivedfor = time.clock() - self.lastStart
        # set the score for the gene based on winning or time of survival
        roundscore = self.max - survivedfor if hasWon else survivedfor / 100000
        self.currgenescores.append(roundscore)

        # check to see if we have completed the last game for a gene
        if len(self.currgenescores) == self.numGamesPerGene:
            # average the scores and set it for the gene
            avgscore = (float)(sum(self.currgenescores)) / (float)(len(self.currgenescores))
            self.pool[self.poolIndex][1] = avgscore
            self.currgenescores = []
            self.poolIndex += 1

        # check to see if we need to start a new generation
        if self.poolIndex == self.popSize:
            # get the gene with the best score, and its state pool = [(gene,score)...]
            genFittest = sorted(self.pool, key=lambda x: x[1], reverse=True)[0]
            fittestState = self.poolStates[self.pool.index(genFittest)]
            self.asciiPrintState(fittestState)
            print("score = " + str(genFittest[1]))

            # reset stuff
            self.poolIndex = 0
            self.poolStates = []
            self.pool = self.generateNextGenes()

        return hasWon

    
    ##
    # asciiPrintState
    #
    # prints a text representation of a GameState to stdout and a file.  This is useful for
    # debugging.
    #
    # Parameters:
    #    state - the state to print
    #
    # Return: None
    ##
    def asciiPrintState(self, state):
        f = open(self.evidenceFile, "a")

        # select coordinate ranges such that board orientation will match the GUI
        # for either player
        coordRange = range(0, 10)
        colIndexes = " 0123456789"
        if (state.whoseTurn == PLAYER_TWO):
            coordRange = range(9, -1, -1)
            colIndexes = " 9876543210"

        # print the board with a border of column/row indexes
        print colIndexes
        f.write(colIndexes + "\n")
        index = 0  # row index
        for x in coordRange:
            row = str(x)
            for y in coordRange:
                constr = getConstrAt(state, (y, x))
                if constr is not None:
                    row += charRepConstr(constr)
                else:
                    row += "."
            print row + str(x)
            f.write(row + str(x) + "\n")
            index += 1
        print colIndexes
        f.write(colIndexes + "\n")

        # print food totals
        p1Food = state.inventories[0].foodCount
        p2Food = state.inventories[1].foodCount
        print " food: " + str(p1Food) + "/" + str(p2Food)
        f.write(" food: " + str(p1Food) + "/" + str(p2Food) + "\n")

        f.close()
