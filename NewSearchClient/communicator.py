import sys
from state import State

GROUPNAME = "AIStars"

class Communicator:

    domain =""
    level_name=""
    starting_state = None
    goal_state = None
    
    def ReadServerMessage(self): 
        
        #send name to server
        
        print(GROUPNAME, file=sys.stdout, flush=True)
        
        #read the level data 
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
                Communicator.domain = line
                
            elif (current_command =="#levelname"):
                Communicator.level_name = line
            
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
        print('Pre-computing distances for the level...', file=sys.stderr, flush=True)
        Communicator.starting_state = State(None, init_state_text) 
        #save goal state
        Communicator.goal_state = State(None, goal_state_text, goal_state=True)
        print('Pre-computing of distances finished succesfully!', file=sys.stderr, flush=True)
        
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