
from collections import Counter
import copy
import time
import math

class ExamplePlayer:
    def __init__(self, colour):
        """
        This method is called once at the beginning of the game to initialise
        your player. You should use this opportunity to set up your own internal
        representation of the game state, and any other information about the 
        game state you would like to maintain for the duration of the game.

        The parameter colour will be a string representing the player your 
        program will play as (White or Black). The value will be one of the 
        strings "white" or "black" correspondingly.
        """
        # TODO: Set up state representation.

        self.colour = colour
        if self.colour == "white":
            self.opponentColour = "black"
        else:
            self.opponentColour = "white"

        self.movesRemaining = 250
        self.timeRemaining = 60

        self.board = {(x, y):0 for x in range(8) for y in range(8)}

        white_tokens = [(0,1), (1,1),   (3,1), (4,1),   (6,1), (7,1),
                        (0,0), (1,0),   (3,0), (4,0),   (6,0), (7,0)]
        black_tokens = [(0,7), (1,7),   (3,7), (4,7),   (6,7), (7,7),
                        (0,6), (1,6),   (3,6), (4,6),   (6,6), (7,6)]

        for xy in white_tokens:
            self.board[xy] = +1
        for xy in black_tokens:
            self.board[xy] = -1

    def action(self):
        """
        This method is called at the beginning of each of your turns to request 
        a choice of action from your program.

        Based on the current state of the game, your player should select and 
        return an allowed action to play on this turn. The action must be
        represented based on the spec's instructions for representing actions.
        """
        # TODO: Decide what action to take, and return it

        startTimer = time.time()
        # print("time remaining", self.timeRemaining)
        # depth = 4
        bestMove = None
        if self.isAnyMovePossible(self.board, self.colour) == True:
            moves = self.getAllPossibleMoves(self.board, self.colour)
            # print(moves)
            #Changing the number of ply for minimax tree to budget time and get best possible moves         
            # If the time remaining < 3 seconds, then just apply simpleGreedy and increase depth according to time
            if self.timeRemaining < 5:
                depth = 2
            if self.timeRemaining < 15:
                depth = 3
            elif self.timeRemaining < 30:
                depth = 4
            else:
                if self.movesRemaining > 248: # play fast for first moves
                    depth = 3
                elif self.movesRemaining > 40:
                    depth = 5
                else:
                    depth = 4
            
            best = None
            bestMove == None
            alpha = None
            beta = None
            for move in moves: # this is the max turn(1st level of minimax), so next should be min's turn
                newBoard = copy.deepcopy(self.board)
                self.doMove(newBoard,move)
                #Beta is always inf here as there is no parent MIN node. So no need to check if we can prune or not.
                # print("move", move)
                moveVal = self.alphaBeta_pruning(newBoard, self.colour, depth, 'min', self.opponentColour, alpha, beta)
                # print("move val: ", moveVal, move)
                # print('alpha, beta, moveVal', alpha, beta, moveVal)
                # input("Press ENTER")
                if moveVal != None:
                    if best == None or moveVal > best:
                        bestMove = move
                        best = moveVal
                    if alpha == None or best > alpha:
                        alpha = best
            if bestMove == None:
                bestMove = moves[0]
        else:
            print("No Possible move!")

        stopTimer =  time.time()
        self.timeRemaining =  self.timeRemaining - (stopTimer - startTimer)
        self.movesRemaining = self.movesRemaining - 1

        # input("Press ENTER")

        return bestMove


    def update(self, colour, action):
        """
        This method is called at the end of every turn (including your player’s 
        turns) to inform your player about the most recent action. You should 
        use this opportunity to maintain your internal representation of the 
        game state and any other information about the game you are storing.

        The parameter colour will be a string representing the player whose turn
        it is (White or Black). The value will be one of the strings "white" or
        "black" correspondingly.

        The parameter action is a representation of the most recent action
        conforming to the spec's instructions for representing actions.

        You may assume that action will always correspond to an allowed action 
        for the player colour (your method does not need to validate the action
        against the game rules).
        """
        # TODO: Update state representation in response to action.

        if action[0] == "BOOM":
            position = action[1]
            x, y = position
            self.board[position] = 0
            # Recursive booms
            self.checkCollateralBOOM(self.board, x, y)
        else:
            nb_token_moved = action[1]
            start_position = action[2]
            end_position = action[3]
            if self.board[start_position] > 0:
                self.board[start_position] -= nb_token_moved
                self.board[end_position] += nb_token_moved
            elif self.board[start_position] < 0:
                self.board[start_position] += nb_token_moved
                self.board[end_position] -= nb_token_moved
            else:
                print("Action ERROR")

    # Returns whether any of the <colour> pieces can make a valid move at this time
    def isAnyMovePossible(self, board, colour):
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position
            
            # Check if this position has our colour
            if (nb_token > 0 and colour == "white") or (nb_token < 0 and colour == "black"):
                nb_token = abs(nb_token)
                for i in range(1,nb_token+1):
                    if self.canMoveToPosition(board, colour, x, y, x-i, y) == True:            
                        # Can move left
                        return True
                    if self.canMoveToPosition(board, colour, x, y, x+i, y) == True:            
                        # Can move right
                        return True
                    if self.canMoveToPosition(board, colour, x, y, x, y-i) == True:            
                        # Can move down
                        return True
                    if self.canMoveToPosition(board, colour, x, y, x, y+i) == True:            
                        # Can move up
                        return True
        
        # If it can eliminate an enemy token, it has move
        if self.isBoomPossible(board, colour) == True:
            return True
            
        return False

    # Check whether (x1,y1) can move to (x2,y2) in one move
    def canMoveToPosition(self, board, colour, x1, y1, x2, y2):
        # check if positions are inside the board
        if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x1 > 7 or y1 > 7 or x2 > 7 or y2 > 7:
            return False
        #check (x2,y2) position if there is enemy token(s)
        if (colour == "white" and board[(x2,y2)] < 0) or (colour == "black" and board[(x2,y2)] > 0):
            return False

        return True

    # check distance between the current token and each enemy position
    def checkDistance(self, board, colour, xa, ya, xb, yb):
        best_dist = 1000
        save_best_pos = 1000
        # compute euclidean distance between :
        #   - initial position and each enemy token
        #   - final position and each enemy token
        for position, nb_token in board.items():
            # if white player
            if colour == "white" and nb_token < 0:
                dist_initial_state = math.sqrt( (xa-position[0])**2 + (ya-position[1])**2 )
                dist_final_state = math.sqrt( (xb-position[0])**2 + (yb-position[1])**2 )
                if dist_initial_state < save_best_pos:
                    save_best_pos = dist_initial_state
                if dist_initial_state < best_dist and dist_final_state < dist_initial_state and dist_final_state < save_best_pos:
                    best_dist = dist_initial_state
            # if black player
            elif colour == "black" and nb_token > 0:
                dist_initial_state = math.sqrt( (xa-position[0])**2 + (ya-position[1])**2 )
                dist_final_state = math.sqrt( (xb-position[0])**2 + (yb-position[1])**2 )
                if dist_initial_state < save_best_pos:
                    save_best_pos = dist_initial_state
                if dist_initial_state < best_dist and dist_final_state < dist_initial_state and dist_final_state < save_best_pos:
                    best_dist = dist_initial_state
        
        if best_dist == 1000:
            return False

        return True


    # Returns whether any of the <colour> pieces can make a Boom
    def isBoomPossible(self, board, colour):
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position
            
            # Check if this position has a enemy token next to him
            if nb_token > 0 and colour == "white":
                for i in range(-1,2):
                    for j in range(-1,2):
                        if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                            if board[(x+i,y+j)] < 0: # if there is an enemy token
                                return True
            elif nb_token < 0 and colour == "black":
                for i in range(-1,2):
                    for j in range(-1,2):
                        if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                            if board[(x+i,y+j)] > 0: # if there is an enemy token
                                return True  
        return False


    # Get a list of all possible moves of <colour>
    def getAllPossibleMoves(self, board, colour):
        moves = []
        
        isBoomPossible = self.isBoomPossible(board, colour)
        nb_boom_move = 0
        # Loop through all board positions
        for position, nb_token in board.items():
            x, y = position

            # check if that position has one of our token
            if (nb_token > 0 and colour == "white") or (nb_token < 0 and colour == "black"):
                moves_for_position, isBoom = self.getAllPossibleMovesAtPosition(board, colour, x, y, nb_token)
                for move in moves_for_position:
                    if move[0] == "BOOM":
                        moves.insert(0,move) # append move at beginning of list
                        nb_boom_move += 1
                    else:
                        moves.insert(nb_boom_move,move) # append move at end of list

        # for i in range(len(moves)):
        #     if moves[i][0] == "BOOM":
        #         moves.insert(0, moves.pop(i))
        
        return moves

    # Returns a tuple : list of all possible moves at the current position and if the moves are Boom moves
    def getAllPossibleMovesAtPosition(self, board, colour, x, y, nb_token):
        # MOVE action
        moves = []
        isBoom = False

        boom_moves = self.getAllBoomMovesAtPosition(board, colour, x, y, nb_token)

        for m in boom_moves:
            moves.append(m)


        if len(boom_moves) == 0:
            n = abs(nb_token)
            for i in range(1,n+1): # move to x/y +- i square
                for j in range(1,n+1): # move j nb token
                    # Can move left
                    if self.canMoveToPosition(board, colour, x, y, x-i, y) == True:
                        if self.checkDistance(board, colour, x, y, x-i, y) == True: 
                            moves.append(("MOVE", j, (x, y), (x-i, y)))
                    # Can move right
                    if self.canMoveToPosition(board, colour, x, y, x+i, y) == True:  
                        if self.checkDistance(board, colour, x, y, x+i, y) == True: 
                            moves.append(("MOVE", j, (x, y), (x+i, y)))
                    # Can move down
                    if self.canMoveToPosition(board, colour, x, y, x, y-i) == True:                                
                        if self.checkDistance(board, colour, x, y, x, y-i) == True:  
                            moves.append(("MOVE", j, (x, y), (x, y-i)))
                    # Can move up    
                    if self.canMoveToPosition(board, colour, x, y, x, y+i) == True:                                
                        if self.checkDistance(board, colour, x, y, x, y+i) == True:
                            moves.append(("MOVE", j, (x, y), (x, y+i)))
        else:
            isBoom == True
            # print(boom_moves)
            # self.print_board_prototype(board)
            # print(moves)

        return moves, isBoom

    def getAllBoomMovesAtPosition(self, board, colour, x, y, nb_token):
        # BOOM action
        boom_moves = []
        if nb_token > 0 and colour == "white":
            for i in range(-1,2):
                for j in range(-1,2):
                    if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                        if board[(x+i,y+j)] < 0: # if there is an enemy token
                            boom_moves.append(("BOOM", (x, y)))
        elif nb_token < 0 and colour == "black":
            for i in range(-1,2):
                for j in range(-1,2):
                    if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                        if board[(x+i,y+j)] > 0: # if there is an enemy token
                            boom_moves.append(("BOOM", (x, y)))
        return boom_moves


    # perform the move and "updates" the board
    def doMove(self, board, move):
        # Will perform the move
        if move[0] == "MOVE":
            nb_token_moved = move[1]
            start_position = move[2]
            end_position = move[3]
            if board[start_position] > 0:
                # current pos
                board[start_position] -= nb_token_moved
                # next pos
                board[end_position] += nb_token_moved
            else:
                # current pos
                board[start_position] += nb_token_moved
                # next pos
                board[end_position] -= nb_token_moved
        else: # if move[0] == "BOOM"
            # current pos
            board[move[1]] = 0
            x, y = move[1]
            self.checkCollateralBOOM(board, x, y)

    # checks if there is a recursive explosion of token
    def checkCollateralBOOM(self, board, x, y):
        for i in range(-1,2):
            for j in range(-1,2):
                if x+i >= 0 and y+j >= 0 and x+i <= 7 and y+j <= 7: # if (i,j) is inside the board
                    if board[(x+i,y+j)] != 0: # if there is a token on position (i,j)
                        board[(x+i,y+j)] = 0
                        self.checkCollateralBOOM(board, x+i, y+j)


    # Alpha Beta pruning algorithm
    def alphaBeta_pruning(self, board, colour, depth, turn, opponentColour, alpha, beta):
        if depth > 1: #Comes here depth-1 times and goes to else for leaf nodes.
            depth -= 1
            opti = None
            if turn == 'max' and self.isAnyMovePossible(board, colour) == True:
                moves = self.getAllPossibleMoves(board, colour) #Gets all possible moves for player
                # print(moves)
                for move in moves:
                    # print("current move alpha and depth", depth, move)
                    nextBoard = copy.deepcopy(board)
                    self.doMove(nextBoard,move)
                    if opti == None or beta == None or beta > opti:
                        value = self.alphaBeta_pruning(nextBoard, colour, depth, 'min', opponentColour, alpha, beta)
                        if value != None:
                            if opti == None or value > opti: # for us alpha needs to be the smallest as possible
                                opti = value
                            if alpha == None or opti > alpha:
                                alpha = opti
                            # print('move depth:', depth, move)
                    # print("alpha", alpha)

            elif turn == 'min' and self.isAnyMovePossible(board, colour) == True:
                moves = self.getAllPossibleMoves(board, opponentColour) #Gets all possible moves for the opponent
                for move in moves:
                    # print("current move beta and depth", depth, move)
                    nextBoard = copy.deepcopy(board)
                    self.doMove(nextBoard,move)
                    if alpha == None or opti == None or alpha < opti: #None conditions are to check for the first times
                        value = self.alphaBeta_pruning(nextBoard, colour, depth, 'max', opponentColour, alpha, beta)
                        if value != None:
                            if opti == None or value < opti: # for us beta needs to be the biggest as possible
                                opti = value
                                # print(opti)
                            if beta == None or opti < beta:
                                beta = opti
                            # print('move depth:', depth, move)
            #         print("beta", beta)

            # input("Press ENTER")
            return opti # opti will contain the best value for player in MAX turn and worst value for player in MIN turn


        else: #Comes here for the last level i.e leaf nodes
            value = 0
            # self.print_board_prototype(board)
            # input("Press the <ENTER> key to continue...")
            for position, nb_token in board.items():
                x, y = position
                #Below, we count the number of token in a stack for each colour.
                #A player stack of more than 1 token is 1.1 times more valuable than a stack of 1 token.
                #An opponent stack of more than 1 token is 1.1 times worse for the player than a stack of 1 token.
                #By assigning more weight on stacks with several tokens, the AI will prefer killing opponent stacks of several token to killing a stack of 1 token.
                #It will also prefer saving player stacks of several tokens to saving player stack of 1 token when the situation demands.
                # second attempt
                if (colour == "white" and board[position] == 1) or (colour == "black" and board[position] == -1): # if my colour and position has 1 token
                    value += 1
                elif (colour == "white" and board[position] == -1) or (colour == "black" and board[position] == 1): # if opponent colour and position has 1 token
                    value -= 1
                elif (colour == "white" and board[position] > 1) or (colour == "black" and board[position] < -1): # if my colour and position has stack of tokens
                    value += (abs(board[position]) *1.1)
                elif (colour == "white" and board[position] < -1) or (colour == "black" and board[position] > 1): # if opponent colour and position has stack of tokens
                    value -= (abs(board[position]) *1.1)

                # first attempt
                # if (colour == "white" and board[position] > 0) or (colour == "black" and board[position] < 0): # if my colour and position has 1 token
                #     value += board[position]
                # elif (colour == "white" and board[position] < 0) or (colour == "black" and board[position] > 0): # if opponent colour and position has 1 token
                #     value += board[position]

            # print('val: ', value)
            return value

    # display board
    def print_board_prototype(self, board):

        new_board = []
        i=0
        j=8
        new_board = list(board.values())
        inter = list()
        for _ in range(8):
            inter.append(new_board[i:j])
            i = j
            j = j+8

        new_board = []
        for i in range(0,8):
            new_board.append([inter[j][7-i] for j in range(0,8)])

        stri = '-'*50
        for j in new_board:
            stri+='\n'
            for item in j:
                stri += '|\t'+ str(item)+'\t'
            stri += '\n'
            stri += '-'*50

        print(stri.expandtabs(3))

            

