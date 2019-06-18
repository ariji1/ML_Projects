from gym import spaces
import numpy as np
import random
from itertools import groupby
from itertools import product

# class TicTacToe():

#     def __init__(self):
#         """initialise the board"""
        
#         # initialise state as an array
#         self.state = [np.nan for _ in range(9)]  # initialises the board position, can initialise to an array or matrix
#         # all possible numbers
#         self.all_possible_numbers = [i for i in range(1, len(self.state) + 1)] # , can initialise to an array or matrix

#         self.reset()


#     def is_winning(self, curr_state):
#         """Takes state as an input and returns whether any row, column or diagonal has winning sum
#         Example: Input state- [1, 2, 3, 4, nan, nan, nan, nan, nan]
#         Output = False"""
 

#     def is_terminal(self, curr_state):
#         # Terminal state could be winning state or when the board is filled up

#         if self.is_winning(curr_state) == True:
#             return True, 'Win'

#         elif len(self.allowed_positions(curr_state)) ==0:
#             return True, 'Tie'

#         else:
#             return False, 'Resume'


#     def allowed_positions(self, curr_state):
#         """Takes state as an input and returns all indexes that are blank"""
#         return [i for i, val in enumerate(curr_state) if np.isnan(val)]


#     def allowed_values(self, curr_state):
#         """Takes the current state as input and returns all possible (unused) values that can be placed on the board"""

#         used_values = [val for val in curr_state if not np.isnan(val)]
#         agent_values = [val for val in self.all_possible_numbers if val not in used_values and val % 2 !=0]
#         env_values = [val for val in self.all_possible_numbers if val not in used_values and val % 2 ==0]

#         return (agent_values, env_values)


#     def action_space(self, curr_state):
#         """Takes the current state as input and returns all possible actions, i.e, all combinations of allowed positions and allowed values"""

#         agent_actions = product(self.allowed_positions(curr_state), self.allowed_values(curr_state)[0])
#         env_actions = product(self.allowed_positions(curr_state), self.allowed_values(curr_state)[1])
#         return (agent_actions, env_actions)



#     def state_transition(self, curr_state, curr_action):
#         """Takes current state and action and returns the board position just after agent's move.
#         Example: Input state- [1, 2, 3, 4, nan, nan, nan, nan, nan], action- [7, 9] or [position, value]
#         Output = [1, 2, 3, 4, nan, nan, nan, 9, nan]
#         """


#     def step(self, curr_state, curr_action):
#         """Takes current state and action and returns the next state, reward and whether the state is terminal. Hint: First, check the board position after
#         agent's move, whether the game is won/loss/tied. Then incorporate environment's move and again check the board status.
#         Example: Input state- [1, 2, 3, 4, nan, nan, nan, nan, nan], action- [7, 9] or [position, value]
#         Output = ([1, 2, 3, 4, nan, nan, nan, 9, nan], -1, False)"""


#     def reset(self):
#         return self.state


class TicTacToe:
    def __init__(self):
        # Our 3*3 start is represented as one dimensional array of 9 values
        self.start = [0]*9
        
        #The env will be able to handle 2 sets of players 
        # Odd player has only options [1, 3, 5, 7, 9]
        self.player1 = None # These values are passed as input to the QLearning process
        # Even player has only options [2, 4, 6, 8]
        self.player2 = None # These values are passed as input to the QLearning process

    #reset the game
    def reset(self):
        self.start = [0] * 9
        
    #take the next step and return reward
    def step(self, is_X, step):
        self.start[step-1]= self.next_Move(is_X)
        reward, done = self.evaluate()
        return reward, done

   #evaluate function
    def evaluate(self):
        # "rows"
        for i in range(3):
            if (self.start[i*3] + self.start[i*3+1] + self.start[i*3+2]) == 15:
                return 1.0, True
        #columns
        for i in range(3):
            if (self.start[i+0] + self.start[i+3] + self.start[i+6]) == 15:
                return 1.0, True
        #"draw"
        if not any(space == 0 for space in self.start):
            return 0.0, True
        # diagonal
        if (self.start[0] + self.start[4] + self.start[8]) == 15:
            return 1.0, True
        if (self.start[2] + self.start[4] + self.start[6]) == 15:
            return 1.0, True
       
        return 0.0, False
    
    #Possible moves
    def possibleMoves(self):
        blank_spots =  [steps + 1 for steps, spot in enumerate(self.start) if spot == 0]
        return blank_spots

    #pick a possible move based on the odd or even player
    def next_Move(self, is_X):
        # we will shuffle the set of remaining options and pop the first from the list to be used for our move.
        if(is_X):
            self.player1.options = random.sample(self.player1.options, len(self.player1.options))
            return self.player1.options.pop()
        # We have one set of player playing odd and the other even, 
        # so we need to switch between the two to determine the next move.
        else:
            self.player2.options = random.sample(self.player2.options, len(self.player2.options))
            return self.player2.options.pop()

    #begin training with default values.
    def startTraining(self, player1, player2, iterations, odd=True, verbose = False):
        self.player1=player1
        self.player2=player2
        print("Training Started")
        for i in range(iterations):
            if verbose: print("trainining ", i)
            self.player1.game_begin()
            self.player2.game_begin()
            self.reset()
            done = False

            #Odd player always begins the game for this simulation,hence set to true by default
            is_X = odd
            while not done:
                if is_X:
                    step = self.player1.epslion_greedy(self.start, self.possibleMoves())
                else:
                    step = self.player2.epslion_greedy(self.start, self.possibleMoves())

                # 'reward' value is 0 or 1 and 'done',is True if game ends (win, lose, draw) False otherwise.
                reward, done = self.step(is_X, step)
                
                if (reward == 1):  # won, reward 10 for the agent winning.
                    if (is_X):
                        self.player1.updateQ(10, self.start, self.possibleMoves())
                        self.player2.updateQ(-10, self.start, self.possibleMoves())
                    else: # -10 for losing.
                        self.player1.updateQ(-10, self.start, self.possibleMoves())
                        self.player2.updateQ(10, self.start, self.possibleMoves())
                elif (done == False):  # Reward -1 for the move that doesn't end the game
                    if (is_X):
                        self.player1.updateQ(-1, self.start, self.possibleMoves())
                else:
                    self.player1.updateQ(reward, self.start, self.possibleMoves())
                    self.player2.updateQ(reward, self.start, self.possibleMoves())

                is_X = not is_X  # switch players
        print ("Training Done")

    #save Qtables
    def saveStates(self):
        self.player1.saveQ("oddPolicy")
        self.player2.saveQ("evenPolicy")

    #return Qtables
    def getQ(self):
        return self.player1.Q, self.player2.Q


