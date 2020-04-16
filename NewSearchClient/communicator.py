import sys
from state import State

GROUPNAME = "AIStars"

def ReadServerMessage(): 
    
    #send name to server
    print(GROUPNAME, file=sys.stdout, flush=True)
    
    #read the level data 
    #TODO translate this into a state 
    server_messages = sys.stdin
    
    line = server_messages.readline().rstrip()
    current_command =''
    longest_line =0
    
    colorstext=[]
    init_state=[]
    goal_state=[]
    while line != "#end":
        if (line[0] =="#"):
            current_command = line
        elif (current_command =="#domain"):
            domain= line
            
        elif (current_command =="#levelname"):
            level_name= line
        
        elif (current_command =="#colors"):
            colorstext.append(line)
        
        elif (current_command =="#initial"):
            init_state.append(line)
            longest_line = max(longest_line, len(line))
            
        elif (current_command =="#goal"):
            goal_state.append(line)
        else:
            print("couldn't recognise command", file=sys.stderr, flush=True)
        
        line = server_messages.readline().rstrip()
    
    #save colors
    colors = {}
    for row, line in enumerate(colorstext):
        line.replace(" ", "")
        color, line = line.split(":")
        colors[color] = line.split(",")
    
    #save level to state
    State.MAX_ROW = len(init_state)
    State.MAX_COL = longest_line
    starting_state = State()
    for row, line in enumerate(init_state):
        for col, char in enumerate(line):
            if (char == "+"):
                starting_state.walls[row][col] = True
            elif (char in "0123456789"): starting_state.agents[str(row)+":"+str(col)] = char             
            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": starting_state.boxes[str(row)+":"+str(col)] = char
            elif char == ' ':
                # Free cell.
                pass
            else:
                print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                sys.exit(1)
    
    #save goal state
    final_state = State()
    for row, line in enumerate(goal_state):
        for col, char in enumerate(line):
            if (char == "+"):
                final_state.walls[row][col] = True
            elif (char in "0123456789"): final_state.agents[str(row)+":"+str(col)] = char             
            elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": final_state.boxes[str(row)+":"+str(col)] = char
            elif char == ' ':
                # Free cell.
                pass
            else:
                print('Error, read invalid level character: {}'.format(char), file=sys.stderr, flush=True)
                sys.exit(1)
               
     

    #info
    print("levelname: "+ level_name, file=sys.stderr, flush=True)
    print("agents: "+ str(starting_state.agents), file=sys.stderr, flush=True)
    print("boxes: "+ str(starting_state.boxes), file=sys.stderr, flush=True)
    print("colors: "+ str(colors), file=sys.stderr, flush=True)
    print("initial state:\n"+ "\n".join(init_state), file=sys.stderr, flush=True)
    print("goal state:\n"+ "\n".join(goal_state), file=sys.stderr, flush=True)    
     
    return starting_state, final_state, colors