import sys
from state import State

GROUPNAME = "AIStars"

class Communicator:

    domain =""
    level_name=""
    starting_state = None
    goal_state = None
    
    #def __init__(self):
        #pass
    
    def ReadServerMessage(self): 
        
        #send name to server
        print(GROUPNAME, file=sys.stdout, flush=True)
        
        #read the level data 
        #TODO translate this into a state 
        server_messages = sys.stdin
        
        line = server_messages.readline().rstrip()
        current_command =''
        longest_line =0
        
        colorstext=[]
        init_state_text=[]
        goal_state_text=[]
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
                init_state_text.append(line)
                longest_line = max(longest_line, len(line))
                
            elif (current_command =="#goal"):
                goal_state_text.append(line)
            else:
                print("couldn't recognise command", file=sys.stderr, flush=True)
            
            line = server_messages.readline().rstrip()
            
        #save colors
        colors = {}
        for row, line in enumerate(colorstext):
            line = line.replace(" ", "")
            color, line = line.split(":")
            for i in line.split(","): colors[i]  = color 
        State.colors= colors
        
        
        #save level to state
        State.MAX_ROW = len(init_state_text)
        State.MAX_COL = longest_line
        Communicator.starting_state = State(None, init_state_text)
        '''
        for row, line in enumerate(init_state_text):
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
        '''
        #save goal state
        Communicator.goal_state = State(None, goal_state_text, goal_state=True)
        '''
        for row, line in enumerate(goal_state_text):
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
        '''  
        
    
        #info
        '''
        print("levelname: "+ level_name, file=sys.stderr, flush=True)
        print("agents: "+ str(starting_state.agents), file=sys.stderr, flush=True)
        print("boxes: "+ str(starting_state.boxes), file=sys.stderr, flush=True)
        print("colors: "+ str(colors), file=sys.stderr, flush=True)
        print("initial state:\n"+ "\n".join(init_state_text), file=sys.stderr, flush=True)
        print("goal state:\n"+ "\n".join(goal_state_text), file=sys.stderr, flush=True)    
         '''
    def send_commands_to_server(self, commands):
        # Read server messages from stdin.
        server_messages = sys.stdin
        print("Sending these commands to server:", file=sys.stderr, flush=True)   
        for state in commands:
            msg =''
            for action in state.jointaction:
                msg += str(action).replace('[','').replace(']','') + ";"
            msg = msg[:-1]
            print(msg, file=sys.stdout, flush=True)    
            response = server_messages.readline().rstrip()
            if 'false' in response:
                print('Server responsed with "{}" to the action "{}" applied in:\n{}\n'.format(response, msg, state.parent), file=sys.stderr, flush=True)
                print('Pretending to reach:\n{}\n'.format(state), file=sys.stderr, flush=True)
                break