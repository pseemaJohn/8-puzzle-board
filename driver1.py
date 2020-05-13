# Program Name : driver.py
# Description : implement and compare several search algorithms \
# and collect some statistics related to their performances of 8puzzle game
# Input Parameter : <method> <board>
# <method> : bfs (Breadth-First Search) , dfs (Depth-First Search), ast (A-Star Search)
# <board> : is a sequence of 0 to 8 for eg: 0,8,7,6,5,4,3,2,1
# Output Parameter : create / write to a file called output.txt, containing the following statistics:
# path_to_goal: the sequence of moves taken to reach the goal
# cost_of_path: the number of moves taken to reach the goal
# nodes_expanded: the number of nodes that have been expanded
# search_depth: the depth within the search tree when the goal node is found
# max_search_depth:  the maximum depth of the search tree in the lifetime of the algorithm
# running_time: the total running time of the search instance, reported in seconds
# max_ram_usage: the maximum RAM usage in the lifetime of the process as measured by \
# the ru_maxrss attribute in the resource module, reported in megabytes
# if input parameter is incorrect it would prompt a msg and program will exit.
# execute as : python3 driver.py bfs 1,2,5,3,4,0,6,7,8

import math
import sys
import time
from collections import deque
import heapq
import psutil

goalState = (0, 1, 2, 3, 4, 5, 6, 7, 8)
bfsOrder = ['up', 'down', 'left', 'right']
astOrder = ['up', 'down', 'left', 'right']
dfsOrder = ['right', 'left', 'down', 'up']
dictHcost = [[0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 1, 2, 1, 2, 3, 2, 3], [2, 1, 0, 3, 2, 1, 4, 3, 2],
             [1, 2, 3, 0, 1, 2, 1, 2, 3], [2, 1, 2, 1, 0, 1, 2, 1, 2], [3, 2, 1, 2, 1, 0, 3, 2, 1],
             [2, 3, 4, 1, 2, 3, 0, 1, 2], [3, 2, 3, 2, 1, 2, 1, 0, 1], [4, 3, 2, 3, 2, 1, 2, 1, 0]]


class SearchList(object):
    def __init__(self, method='bfs'):
        self.method = method
        self.tempList = set()
        self.visitedList = list()
        if self.method == 'ast':
            self.frontierList = []
        else:
            self.frontierList = deque()
        return

    def frontieradd(self, currentnodestate):
        currentcost = 0
        for iterNode in currentnodestate.children:
            if iterNode.config not in self.tempList:
                if self.method == 'ast':
                    print("Child added at : ",self.tempList.__len__()," Cost is ",iterNode.hCost, " Action is ",iterNode.action)
                    #heapq.heappush(self.frontierList,[iterNode.hCost, iterNode.misplace+iterNode.cost,self.tempList.__len__(), iterNode]) - 64
                    #heapq.heappush(self.frontierList,[iterNode.hCost, iterNode.cost,self.tempList.__len__(), iterNode]) - 72
                    #heapq.heappush(self.frontierList,[iterNode.hCost, self.tempList.__len__(), iterNode]) - 72
                    #heapq.heappush(self.frontierList,[iterNode.hCost, iterNode.cost+iterNode.misplace,self.tempList.__len__(), iterNode])
                    heapq.heappush(self.frontierList,[iterNode.cost+iterNode.hCost,self.tempList.__len__(), iterNode])

                    #print("Value of Cost ", iterNode.cost, "Value of parent "iterNode.parent)
                    #print("Value of parent hCost:",)
                    #heapq.heappush(self.frontierList,[iterNode.hCost,iterNode.misplace+iterNode.hCost,iterNode])
                else:
                    self.frontierList.append(iterNode)
                self.tempList.add(iterNode.config)
                currentcost = iterNode.cost
        return currentcost

    def addfirst(self, arghead):
        if self.method == 'ast':
            heapq.heappush(self.frontierList, [arghead.hCost, 1, arghead])
            #heapq.heappush(self.frontierList, [arghead.hCost,arghead.misplace,1,arghead])
        else:
            self.frontierList.append(arghead)
        self.tempList.add(arghead.config)
        return

    def getpopnode(self):
        popnode = None
        if self.method == 'dfs':
            popnode = self.frontierList.pop()
        elif self.method == 'bfs':
            popnode = self.frontierList.popleft()
        elif self.method == 'ast':
            #_, _, _, popnode = heapq.heappop(self.frontierList)
            _, _, popnode = heapq.heappop(self.frontierList)
        self.visitedList.append(popnode)
        return popnode


class PuzzleState(object):
    """docstring for PuzzleState"""

    def __init__(self, config, n, parent=None, action="Initial", cost=0, order=0):
        if n * n != len(config) or n < 2:
            raise Exception("the length of config is not correct!")
        self.n = n
        self.cost = cost
        self.parent = parent
        self.action = action
        self.dimension = n
        self.config = config
        self.children = []
        self.hCost = 0
        self.misplace = order
        for i, item in enumerate(self.config):
            if item == 0:
                self.blank_row = i // self.n
                self.blank_col = i % self.n
                # break
            else:
                #if i != item:
                    #self.misplace += 1
                self.hCost = self.hCost + dictHcost[item][i]

    def display(self):
        for i in range(self.n):
            line = []
            offset = i * self.n
            for j in range(self.n):
                line.append(self.config[offset + j])
            print(line)

    def displaywhole(self):
        self.display()
        print("Cost", self.cost)
        print("Action", self.action)
        print("Blank Col", self.blank_col)
        print("Blank Row", self.blank_row)
        print("H Cost", self.hCost)
        for i, childN in enumerate(self.children):
            print("Child No", i)
            childN.display()
        print("Dimension", self.dimension)
        print("N value", self.n)
        print("Parent ", self.parent)
        if self.parent is not None:
            print("Parent HCost ", self.parent.hCost, "Cost level is ", self.parent.cost)

    def move_left(self):
        if self.blank_col == 0:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index - 1
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Left", cost=self.cost + 1, order=2)

    def move_right(self):
        if self.blank_col == self.n - 1:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index + 1
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Right", cost=self.cost + 1, order=1)

    def move_up(self):
        if self.blank_row == 0:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index - self.n
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Up", cost=self.cost + 1, order=4)

    def move_down(self):
        if self.blank_row == self.n - 1:
            return None
        else:
            blank_index = self.blank_row * self.n + self.blank_col
            target = blank_index + self.n
            new_config = list(self.config)
            new_config[blank_index], new_config[target] = new_config[target], new_config[blank_index]
            return PuzzleState(tuple(new_config), self.n, parent=self, action="Down", cost=self.cost + 1, order=3)

    def expand(self, orderlist):
        """expand the node"""
        # add child nodes in order of UDLR
        if len(self.children) == 0:
            for i in orderlist:
                namefun = getattr(self, "move_" + i)
                child = namefun()
                if child is not None:
                    self.children.append(child)

        return


class SearchAlgoImpl(object):
    """SearchAlgoImpl class provides a wrapper for different search classess"""

    def __init__(self, searchtype="bfs", maxsearchdepth=0):
        self.searchType = searchtype
        self.maxSearchDepth = maxsearchdepth
        self.goalNode = None
        self.searchList = SearchList(searchtype)
        self.searchNodeExpand = 0
        return

    # to process bfs
    def search(self):
        while self.searchList.frontierList.__len__() != 0:
            currentnodestate = self.searchList.getpopnode()
            if currentnodestate.config != goalState:
                currentnodestate.expand(globals()[self.searchType + "Order"])
                self.searchNodeExpand = self.searchNodeExpand + 1
                currentnodecost = self.searchList.frontieradd(currentnodestate)
                if self.maxSearchDepth < currentnodecost:
                    self.maxSearchDepth = currentnodecost
            else:
                self.goalNode = currentnodestate
                return currentnodestate

        return None

    def writeoutput(self, timetaken, memtaken):
        pathlist = []
        tempgoalnode = self.goalNode
        with open("output.txt", "w") as filePtr:
            filePtr.write("path_to_goal: ")
            while tempgoalnode.parent is not None:
                pathlist.insert(0, tempgoalnode.action)
                tempgoalnode = tempgoalnode.parent
            filePtr.write(str(pathlist) + "\n")
            strtowrite = "cost_of_path: " + str(len(pathlist)) + "\n"
            filePtr.write(strtowrite)
            strtowrite = "nodes_expanded: " + str(self.searchNodeExpand) + "\n"
            filePtr.write(strtowrite)
            strtowrite = "search_depth: " + str(self.goalNode.cost) + "\n"
            filePtr.write(strtowrite)
            strtowrite = "max_search_depth: " + str(self.maxSearchDepth) + "\n"
            filePtr.write(strtowrite)
            strtowrite = "running_time: " + str('{0:.8f}'.format(timetaken)) + "\n"
            filePtr.write(strtowrite)
            strtowrite = "max_ram_usage: " + str(memtaken) + "\n"
            filePtr.write(strtowrite)
        return


# validate input arguments
def validateargs(argmethod, argboard):
    # check if input in goal state
    if argboard == goalState:
        print("Board in goal state no search applicable")
        return 1

    # validate method requested
    if argmethod not in ('bfs', 'dfs', 'ast'):
        print("Incorrect method requested, value can be 'bfs' or 'dfs' or'ast'")
        return 1

    # validate board details
    # if(argboard != ['0','1','2','3','4','5','6','7','8'] ) :
    if set(argboard) != set(goalState):
        print("Incorrect board requested, value can be any order of 0,1,2,3,4,5,6,7,8")
        return 1
    return


# the first function executed on execution of the program
def startprocess():
    # check argument, if not 3 exit application
    if len(sys.argv) != 3:
        print(" Incorrect Argument provided \n python3 driver.py <method> <board>")
        return 1

    # capture the method
    method = sys.argv[1].lower()
    # capture the board
    board = tuple(map(int, sys.argv[2].split(",")))
    # validate the arguments
    if validateargs(method, board) == 1:
        return 1
    size = int(math.sqrt(len(board)))

    # Create a object of PuzzleState to create the Start State
    startstate = PuzzleState(board, size)
    # Create a object of Search Algorithm
    searchobjlocal = SearchAlgoImpl(method)

    # namefun = getattr(searchobjlocal, method+"_search")
    starttime = time.time()
    searchobjlocal.searchList.addfirst(startstate)
    searchobjlocal.search()
    endtime = time.time()
    # print("Total time taken for processing is ", (endtime - starttime))
    if searchobjlocal.goalNode is not None:
        # print("Goal found at the depth of ", searchobjlocal.goalNode.cost)
        # searchobjlocal.goalNode.display()
        searchobjlocal.writeoutput(endtime - starttime, ((psutil.Process().memory_info().rss / 1024) / 1024))

    else:
        print("Goal not found")
    return 0


# Below line checks if the control of the program is main, __name__ variable provides the name of current process
if __name__ == '__main__':
    startprocess()
