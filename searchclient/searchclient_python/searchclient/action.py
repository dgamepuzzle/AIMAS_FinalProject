class Dir:
    N = S = E = W = None
    
    def __init__(self, name: 'str', d_row: 'int', d_col: 'int'):
        '''
        For internal use; do not instantiate.
        Use Dir.N, Dir.S, Dir.E, and Dir.W instead.
        '''
        self.name = name
        self.d_row = d_row
        self.d_col = d_col
    
    def get_inverse(self):
        name = self.name
        if name == 'N':
            name = 'S'
        elif name == 'S':
            name = 'N'
        elif name == 'E':
            name = 'W'
        else:
            name = 'E'
        d_row = self.d_row * -1
        d_col = self.d_col * -1
        return Dir(name, d_row, d_col)
    
    def copy(self):
        name = self.name
        d_row = self.d_row
        d_col = self.d_col
        return Dir(name, d_row, d_col)
            
    def __repr__(self):
        return self.name

Dir.N = Dir('N', -1,  0)
Dir.S = Dir('S',  1,  0)
Dir.E = Dir('E',  0,  1)
Dir.W = Dir('W',  0, -1)


class ActionType:
    Move = Push = Pull = None
    
    def __init__(self, name: 'str'):
        '''
        For internal use; do not instantiate.
        Use ActionType.Move, ActionType.Push, and ActionType.Pull instead.
        '''
        self.name = name
        
    def get_inverse(self):
        name = self.name
        if name == 'Push':
            name = 'Pull'
        elif name == 'Pull':
            name = 'Push'
        return ActionType(name)
    
    def __repr__(self):
        return self.name

ActionType.Move = ActionType('Move')
ActionType.Push = ActionType('Push')
ActionType.Pull = ActionType('Pull')


class Action:
    def __init__(self, action_type: 'ActionType', agent_dir: 'Dir', box_dir: 'Dir'):
        '''
        For internal use; do not instantiate.
        Iterate over ALL_ACTIONS instead.
        '''
        self.action_type = action_type
        self.agent_dir = agent_dir
        self.box_dir = box_dir
        if box_dir is not None:
            self._repr = '[{}({},{})]'.format(action_type, agent_dir, box_dir)
        else:
            self._repr = '[{}({})]'.format(action_type, agent_dir)
    
    def get_inverse(self):
        box_dir = None
        if self.box_dir is not None:
            box_dir = self.box_dir.copy()
            
        inverse = Action(
                self.action_type.get_inverse(),
                self.agent_dir.get_inverse(),
                box_dir)
        
        return inverse
    
    def __repr__(self):
        return self._repr


# Grounded actions.
ALL_ACTIONS = []
for agent_dir in (Dir.N, Dir.S, Dir.E, Dir.W):
    ALL_ACTIONS.append(Action(ActionType.Move, agent_dir, None))
    for box_dir in (Dir.N, Dir.S, Dir.E, Dir.W):
        if agent_dir.d_row + box_dir.d_row != 0 or agent_dir.d_col + box_dir.d_col != 0:
            # If not opposite directions.
            ALL_ACTIONS.append(Action(ActionType.Push, agent_dir, box_dir))
        if agent_dir is not box_dir:
            # If not same directions.
            ALL_ACTIONS.append(Action(ActionType.Pull, agent_dir, box_dir))
