from BattleUtilities import calculate_damage, calculate_total_HP, opponent_can_outspeed
from poke_env.environment.move import Move
from poke_env.environment.pokemon import Pokemon

'''
Represents each game state in the battle that keeps track of pokemon,
pokemon hp, opponent pokemon, opponent pokemon hp, action, previous
action, score, and parent node.
'''

class GameState: 
    def __init__(self, battle, pokemon, pokemon_HP, opponent, opponent_HP, action, previous_action, score, parent_node):
        self.battle = battle
        self.pokemon = pokemon
        self.pokemon_HP = pokemon_HP
        self.opponent = opponent
        self.opponent_HP = opponent_HP
        self.action = action
        self.previous_action = previous_action
        self.score = score
        self.parent_node = parent_node
        self.children = []


    # Generate children
    def generate_bot_moves(self):
        self.add_bot_moves()
        if not self.battle.trapped and (not isinstance(self.previous_action, Pokemon) or self.battle.active_pokemon.current_hp <= 0):
            self.add_bot_switches()
        return self.children
    
		
	# Generate child nodes for each move
    def add_bot_moves(self):
		# Add children for every legal move
        i = 0
        if self.battle.active_pokemon is self.pokemon: 
            for move in self.battle.available_moves:
                if move.current_pp > 0:
                    # Generate a child node with the move as the action
                    i = i + 1
                    self.children.append(GameState(self.battle, self.pokemon, self.pokemon_HP.copy(), self.opponent, self.opponent_HP.copy(), move, self.previous_action, self.score, self))
        else: 
            for move in self.pokemon.moves.values():
                if move.current_pp > 0: 
                    # Generate a child node with the move as the action
                    i = i + 1
                    self.children.append(GameState(self.battle, self.pokemon, self.pokemon_HP.copy(), self.opponent, self.opponent_HP.copy(), move, self.previous_action, self.score, self)) 
		
	# Generate child nodes for switches
    def add_bot_switches(self): 
        # Add children for every legal switch
        i = 0
        for switch in self.battle.team.values():
            if switch.current_hp > 0 and switch is not self.pokemon:
                i = i + 1
                self.children.append(GameState(self.battle, switch, self.pokemon_HP.copy(), self.opponent, self.opponent_HP.copy(), switch, self.previous_action, self.score, self))
        return self.children

    ''' 
    This function should add child nodes based on every move and switch the opponent can perform (that we can know about)
    This should take into account the actions that the player made, and calculate new estimated HP values
    '''
    
    def generate_opponent_moves(self): 
        self.add_opponent_moves()
        self.add_opponent_switches()
         # If there are no moves for the opponent, add a "None" action and estimate damage from the bot's attack
        if len(self.children) == 0:
            self.add_opponent_default()
        return self.children
        

	# Generates child nodes for opponent moves
    def add_opponent_moves(self):
		# Add children for every move the opponent has that we know about
        for move in self.opponent.moves.values():
            updated_current_HP = self.pokemon_HP.copy()
            updated_opponent_HP = self.opponent_HP.copy()
            # If opponent outspeeds (or I switched this turn), start by calculating how much damage opponent does
            if opponent_can_outspeed(self.pokemon, self.opponent) or isinstance(self.action, Pokemon):
                damage = calculate_damage(move, self.opponent, self.pokemon, False)
                damage_percentage = (damage / calculate_total_HP(self.pokemon)) * 100
                updated_current_HP[self.pokemon] = self.pokemon_HP[self.pokemon] - damage
                # If my pokemon survives (and attacked this turn), calculcate damage
                if isinstance(self.action, Move) and updated_current_HP[self.pokemon] > 0:
                    damage = calculate_damage(self.action, self.pokemon, self.opponent, True)
                    damage_percentage = (damage / calculate_total_HP(self.opponent)) * 100
                    updated_opponent_HP[self.opponent] = self.opponent_HP[self.opponent] - damage_percentage
            else: 
                # I attack first, calculate damage
                damage = calculate_damage(self.action, self.pokemon, self.opponent, True)
                damage_percentage = (damage / calculate_total_HP(self.opponent)) * 100
                updated_opponent_HP[self.opponent] = self.opponent_HP[self.opponent] - damage_percentage
                # If opponent survices, calculate their damage as well
                if updated_opponent_HP[self.opponent] > 0: 
                    damage = calculate_damage(move, self.opponent, self.pokemon, False)
                    damage_percentage = (damage / calculate_total_HP(self.pokemon)) * 100
                    updated_current_HP[self.pokemon] = self.pokemon_HP[self.pokemon] - damage_percentage
            self.children.append(GameState(self.battle, self.pokemon, updated_current_HP, self.opponent, updated_opponent_HP, move, self.previous_action, self.score, self))
	
	# Generate child nodes for opponent switches
    def add_opponent_switches(self):
		# Calculate all switches opponent can make
        for switch in self.battle.opponent_team.values():
            if switch is not None and switch is not self.opponent and switch.current_hp:
                self.children.append(GameState(self.battle, self.pokemon, self.pokemon_HP.copy(), switch, self.opponent_HP.copy(), switch, self.previous_action, self.score, self))
    
    # If there are no moves for the opponent, add a "None" action and estimate damage from the bot's attack
    def add_opponent_default(self):        
        updated_opponent_HP = self.opponent_HP.copy()
        if isinstance(self.action, Move):
            damage = calculate_damage(self.action, self.pokemon, self.opponent, True)
            damage_percentage = (damage / calculate_total_HP(self.opponent)) * 100
            updated_opponent_HP[self.opponent] = self.opponent_HP[self.opponent] - damage_percentage
            self.children.append(GameState(self.battle, self.pokemon, self.pokemon_HP.copy(), self.opponent, updated_opponent_HP, None, self.previous_action, self.score, self))