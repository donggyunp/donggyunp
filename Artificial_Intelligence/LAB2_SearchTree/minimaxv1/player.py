#!/usr/bin/env python3
import random
import os
from fishing_game_core.game_tree import Node
from fishing_game_core.player_utils import PlayerController
from fishing_game_core.shared import ACTION_TO_STR
import math
from time import time
from operator import itemgetter, attrgetter
# test

def printerr(s):
    s += '\n'
    os.write(2,str.encode(s))

class PlayerControllerHuman(PlayerController):
    def player_loop(self):
        """
        Function that generates the loop of the game. In each iteration
        the human plays through the keyboard and send
        this to the game through the sender. Then it receives an
        update of the game through receiver, with this it computes the
        next movement.
        :return:
        """

        while True:
            # send message to game that you are ready
            msg = self.receiver()
            if msg["game_over"]:
                return


class PlayerControllerMinimax(PlayerController):

    def __init__(self):
        super(PlayerControllerMinimax, self).__init__()

    def player_loop(self):
        """
        Main loop for the minimax next move search.
        :return:
        """

        # Generate game tree object
        first_msg = self.receiver()
        # Initialize your minimax model
        model = self.initialize_model(initial_data=first_msg)
        #printerr("first message: " + str(first_msg))
        #if step==1:
        #    return (step % N_FISH, random.randint(0, N_SPECIES - 1))

        #mstats = {'stay':0.0,'up':0.0,'down':0.0,'left':0.0,'right':0.0}
        #nmoves = 1.0
        while True:
            msg = self.receiver()
            #printerr("-----------------------------------")
            #printerr("message: " + str(first_msg) + '\n')

            # Create the root node of the game tree
            node = Node(message=msg, player=0)
            #printerr("initial node: " + str(node) + '\n')

            # Possible next moves: "stay", "left", "right", "up", "down"
            best_move = self.search_best_next_move(
                model=model, initial_tree_node=node)

            #mstats[best_move] += 1
            
            '''
            if nmoves % 5== 0:
                printerr("Stay: " + str(mstats.get('stay') / nmoves))
                printerr("Up: " + str(mstats.get('up')/nmoves))
                printerr("Down: " + str(mstats.get('down')/nmoves))
                printerr("Left: " + str(mstats.get('left')/nmoves))
                printerr("Right: " + str(mstats.get('right')/nmoves))
            
            nmoves += 1
            '''
            # Execute next action
            self.sender({"action": best_move, "search_time": None})

    def initialize_model(self, initial_data):
        """
        Initialize your minimax model 
        :param initial_data: Game data for initializing minimax model
        :type initial_data: dict
        :return: Minimax model
        :rtype: object

        Sample initial data:
        { 'fish0': {'score': 11, 'type': 3}, 
          'fish1': {'score': 2, 'type': 1}, 
          ...
          'fish5': {'score': -10, 'type': 4},
          'game_over': False }

        Please note that the number of fishes and their types is not fixed between test cases.
        """
        # EDIT THIS METHOD TO RETURN A MINIMAX MODEL ###
        return None

    def search_best_next_move(self, model, initial_tree_node):
        """
        Use your minimax model to find best possible next move for player 0 (green boat)
        :param model: Minimax model
        :type model: object
        :param initial_tree_node: Initial game tree node 
        :type initial_tree_node: game_tree.Node 
            (see the Node class in game_tree.py for more information!)
        :return: either "stay", "left", "right", "up" or "down"
        :rtype: str
        """

        # EDIT THIS METHOD TO RETURN BEST NEXT POSSIBLE MODE FROM MINIMAX MODEL ###
        
        # Don't forget to initialize the children of the current node 
        #       with its compute_and_get_children() method!

        initial_tree_node.__class__ = MinimaxNode
        max_depth = 7
        starttime = time()
        model = MinimaxTree(initial_tree_node, starttime, max_depth)

        for d in range(1 ,max_depth+1):
            model.max_depth = d
            _ = model.minimax(model.root)
            best_move = model.best_move
            tdiff = (time() - starttime) * 1000
            printerr("MAXDEPTH = " + str(d))
            #printerr("time for this this depth: " + str((time()-starttime)*1000))
            if tdiff > 10:
                return ACTION_TO_STR[best_move]

        #printerr("CHILDREN = \n")
        #for i in range(len(children)):
        #    printerr(str(i) + " " + ACTION_TO_STR[i] + " : " \
        #    + str(children[i]))

        #random_move = random.randrange(5)
        #return ACTION_TO_STR[random_move]
        printerr("all depths reached...")
        return ACTION_TO_STR[best_move]

class MinimaxTree:
    def __init__(self, root, starttime, max_depth=2):
        self.root = root  # root is a MinimaxNode
        self.best_move = 0
        self.max_depth = max_depth
        self.starttime = starttime
        self.state_table = {} # hash map
    
    def statestr(self,state):
        hookA = state.hook_positions.get(0)
        hookB = state.hook_positions.get(1)
        s = 'A' + str(hookA) + 'B' + str(hookB) + '_' # or just distance??
        for i,(fish,fpos) in enumerate(state.fish_positions.items()):
            s += 'fish' + str(fish) + str(fpos) + '_'
        return s

    def isend(self, state):
        return len(state.fish_positions) == 0

    # RECURSION!!!!!
    def minimax(self, node, curr_depth = 0, alpha = float('-inf'), 
            beta = float('inf')):
        state = node.state
        pl = node.state.player 

        # TODO: increase maximum allowed depth here!!!!!
        # BASE CASE, leaves
        curr_time = time()
        tdiff = (curr_time - self.starttime) * 1000 # in millisec
        
        # check end state
        if self.isend(state):
            a_points = node.state.player_scores.get(0)
            b_points = node.state.player_scores.get(1)
            self.best_move = 0
            if a_points-b_points > 0:
                self.state_table[hash(self.statestr(state))] = 1e200
                return 1e200
            elif a_points-b_points == 0:
                self.state_table[hash(self.statestr(state))] = 0
                return 0
            else:
                self.state_table[hash(self.statestr(state))] = -1e200
                return -1e200
 
        children = node.compute_and_get_children()

        # check if leaf / BASE CASE
        if children is None or curr_depth >= self.max_depth: # or tdiff > 49:
             heur = heuristic(node.state)
             node.heur = heur
             #printerr("depth in base: " + str(curr_depth))
             #printerr("heur value in base: " + str(heur))
             #self.state_table[hash(self.statestr(state))] = heur
             return heur

        # check in hash map
        #v = self.state_table.get(hash(self.statestr(state))) 
        #if v is not None:
        #    return v 

        #printerr("DEPTH = " + str(curr_depth) + ";PLAYER="+str(pl))

        # sort children after move order 
        if curr_depth < self.max_depth - 1:
            h_children = []
            for i in range(len(children)):
                child = children[i]
                cstate = child.state
                v = self.state_table.get(hash(self.statestr(cstate)))
                if v is not None:
                    h_children.append((v, child))
                else:
                    h_children.append((-1e100, child))
            h_children = sorted(h_children, key=itemgetter(0))        
            #pass
            #random.shuffle(children)
            #children.sort(reverse=True)
            sorted_children = [ tup[1] for tup in h_children ]
        else:
            sorted_children = children

        if node.state.player == 0: # MAX
            val = float('-inf')
            best_move = 0 # only used for depth 0
            for i,child in enumerate(sorted_children):
                v = self.minimax(child, curr_depth + 1, alpha, beta)
                if v > val:
                    val = v
                    best_move = child.move
                #val = max(val,  \
                #    self.minimax(child, curr_depth + 1, alpha, beta))
                #printerr("Move "+str(i)+" : value = "+str(val))
                alpha = max(alpha, val)
                if beta <= alpha:
                    break # prune
            node.heur = val
            self.state_table[hash(self.statestr(state))] = node.heur
            if curr_depth == 0:
                self.best_move = best_move
            return val   

        else: # MIN
            val = float('inf')
            best_move = 0
            for i,child in enumerate(sorted_children):
                v = self.minimax(child, curr_depth + 1, alpha, beta)
                if v < val:
                    val = v
                    best_move = child.move
                beta = min(beta, val)
                if beta <= alpha:
                    break # prune
            node.heur = val
            self.state_table[hash(self.statestr(state))] = node.heur
            return val

class MinimaxNode(Node):
    def __init__(self, root, heur=0):
        super(MinimaxNode, self).__init__(root)
        self.heur = heur 
    # sorting for move ordering
    def __lt__(self, other):
        return heuristic(self.state) < heuristic(other.state)        

def dist(p1,p2):
    # points are (x,y) tuples
   
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) # euclidean
    #return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])  # manhattan dist

def heuristic(state):
    #printerr("COMPUTING HEUR ------- ")

    scoreA = state.player_scores.get(0)
    scoreB = state.player_scores.get(1)
    fpoints = state.fish_scores
    num_fish = len(fpoints)
    print("len(fpoints): ",len(fpoints))
    hookA = state.hook_positions.get(0) # (x,y) tuples
    hookB = state.hook_positions.get(1)

    fish_pos = state.fish_positions
    #print("fish_pos: ",fish_pos)
    s = 0
    t1 = 0
    t2 = 0
    x1, x2 = []
    # compute sum of fish_points*distance to fishes for player A
    #printerr("SUM LOOP : ")
    for i, (fish, fpos) in enumerate(fish_pos.items()):
        fpoint = fpoints.get(fish) # (x,y) tuple
    #if hookA[0] < hookB[0] and hookA[0] < 10 and t1 == 0:
    #    x1.append = hookA[0] + 20 
    #if hookA[0] > hookB[0] and hookA[0] >= 10 and t2 == 0:
    #    x2.append = hookA[0] - 20
        dista = dist(hookA, fpos)
        distb = dist(hookB, fpos)  
        
        s -= fpoint * dista**2    
        #printerr("fpos = " + str(fpos))
        #printerr("hookA = " + str(hookA))
        #printerr("hookB = " + str(hookB))
        #printerr("fpoint = " + str(fpoint)) 
        #printerr("------")

        # case 1
        '''
        if hookA[0] < hookB[0] and fpos[0] < hookB[0]:
            if fpos[0] < hookA[0] and hookB[0]-fpos[0] > 15:
                relative_fpos = (19 + fpos[0], fpos[1]) 
                distb = dist(hookB, relative_fpos)
        # case 2
        if hookA[0] < hookB[0] and fpos[0] > hookB[0]:
            if fpos[0] - hookA[0] > 15:
                relative_fpos = (-(19-fpos[0]), fpos[1]) 
                #printerr(str(relative_fpos))
                dista = dist(hookA, relative_fpos)
        # case 3
        if hookA[0] > hookB[0] and fpos[0] < hookA[0]:
            if fpos[0] < hookB[0] and hookA[0]-fpos[0] > 15:
                relative_fpos = (19 + fpos[0], fpos[1]) 
                #printerr(str(relative_fpos))
                dista = dist(hookA, relative_fpos)
        # case 4
        if hookA[0] > hookB[0] and fpos[0] > hookA[0]:
            if fpos[0] - hookB[0] > 15:
                relative_fpos = (-(19-fpos[0]), fpos[1]) 
                #printerr(str(relative_fpos))
                distb = dist(hookB, relative_fpos)

        '''

        #printerr("dista = " + str(dista))
        #printerr("distb = " + str(distb))
        #printerr("-----------")
        #s +=  fpoint * distb - fpoint * dista \
        #s -= fpoint * dista**2 \
        #    + n_our * fpoint - n_other * fpoint
        #if n_our == 0:
        #    s -= 1000
    return (scoreA**5 - scoreB**3) + s

