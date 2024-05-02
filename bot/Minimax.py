from poke_env.player import Player, RandomPlayer
from BattleUtilities import get_defensive_type_multiplier, opponent_can_outspeed
from GameState import GameState
import asyncio
import time
import random

class MinimaxPlayer(Player):

    previous_action = None
    # 2 was better in performance
    max_depth = 2


    # The nodes keep track of battle states, moves are transitions between states
    def choose_move(self, battle):
        # dictionary that maps Pokemon to HP
        current_hp = {}
        for pokemon in battle.team.values():
            current_hp[pokemon] = pokemon.current_hp
        opponent_hp = {}
        for pokemon in battle.opponent_team.values():
            opponent_hp[pokemon] = pokemon.current_hp
        
        starting_node = GameState(battle, battle.active_pokemon, current_hp, battle.opponent_active_pokemon, opponent_hp, None, self.previous_action, float('-inf'), None)
        if battle.active_pokemon.current_hp <= 0:
            # pokemon fainted
            self.pick_best_switch(starting_node)
        else:
            alpha = float("-inf")
            beta = float("inf")
            self.maximizing_agent(starting_node, 0, alpha, beta)
        child_nodes = starting_node.children
        best_score = float('-inf')
        best_node = None
        for child in child_nodes:
            if child.score >= best_score: 
                best_score = child.score
                best_node = child
        if best_node == None:
            self.previous_action = None
            return self.choose_default_move()
        self.previous_action = best_node.action
        return self.create_order(best_node.action)


    def maximizing_agent(self, node, depth, alpha, beta):
        if depth == self.max_depth:
            self.score(node)
            return node.score
        elif self.is_terminal(node):
            self.score(node)
            return node.score
        best_score = float('-inf')
        moves = node.generate_bot_moves()
        for move in moves: 
            child_score = self.minimizing_agent(move, depth, alpha, beta)
            if child_score > best_score:
                best_score = child_score
                alpha = max(alpha, best_score)
            if best_score > beta:
                node.score = best_score
                return best_score
        node.score = best_score
        return best_score

    def minimizing_agent(self, node, depth, alpha, beta):
        if depth == self.max_depth:
            self.score(node)
            return node.score
        elif self.is_terminal(node):
            self.score(node)
            return node.score

        best_score = float('inf')
        moves = node.generate_opponent_moves()
        if len(moves) > 0:
            for move in moves: 
                child_score = self.maximizing_agent(move, depth + 1, alpha, beta)
                if child_score < best_score:
                    best_score = child_score
                    beta = min(beta, best_score)
                if best_score < alpha:
                    node.score = best_score
                    return best_score
        else: 
            best_score = float('-inf')
        node.score = best_score
        return best_score


    def pick_best_switch(self, node):
        switches = node.add_bot_switches()
        score = float('-inf')
        for switch in switches:
            alpha = float("-inf")
            beta = float("inf")
            child_score = self.minimizing_agent(switch, 0, alpha, beta)
            score = max(score, child_score)
        node.score = score
        return score



    # This function determines if this is an end state and we should stop
    def is_terminal(self, node):
        for pokemon in node.pokemon_HP.keys():
            if node.pokemon_HP[pokemon] > 0:
                return False
        for pokemon in node.opponent_HP.keys():
            if node.opponent_HP[pokemon]:
                return False
        return True



    def score(self, node):
        score = 0
        # Get positive points for dealing damage and knocking out opponent
        for pokemon in node.opponent_HP.keys():
            if pokemon.current_hp is not None:
                if node.opponent_HP[pokemon] <= 0 and pokemon.current_hp > 0:
                    score += 300
                else:
                    damage = pokemon.current_hp - node.opponent_HP[pokemon]
                    score += damage
        # Lose points for taking damage or getting knocked out
        for pokemon in node.pokemon_HP.keys():
            if node.pokemon_HP[pokemon] <= 0 and pokemon.current_hp > 0:
                # Only lose points if pokemon had significant amount of hp --> enable "sacking"
                if (pokemon.current_hp / pokemon.max_hp) > .2:
                    score -= 300
            else:
                damage = pokemon.current_hp - node.pokemon_HP[pokemon]
                score -= damage
        # Lose points for getting outsped by opponent
        if opponent_can_outspeed(node.pokemon, node.opponent):
           score -= 25
        # Add / Subtract points for type match-up
        type_multiplier = get_defensive_type_multiplier(node.pokemon, node.opponent)
        if type_multiplier == 4:
           score -= 50
        if type_multiplier == 2:
           score -= 25
        if type_multiplier == 0.5:
           score += 25
        if type_multiplier == 0.25:
           score += 50
        node.score = score
        return score
    
		
class MaxDamagePlayer(Player):
    def choose_move(self, battle):
        # If the player can attack, it will
        if battle.available_moves:
            # Finds the best move among available ones
            best_move = max(battle.available_moves, key=lambda move: move.base_power)
            return self.create_order(best_move)

        # If no attack is available, a random switch will be made
        else:
            return self.choose_random_move(battle)
        
		
async def main():
	start = time.time()

	# create two players
	max_damage_player = MaxDamagePlayer(battle_format="gen8randombattle",)
	minimax_player = MinimaxPlayer(battle_format="gen8randombattle",)

	# evaluate player
	await minimax_player.battle_against(max_damage_player, n_battles=10)

	print("Minimax player won %d / 10 battles against max damage player [this took %f seconds]"% (minimax_player.n_won_battles, time.time() - start))

if __name__ == "__main__":
	asyncio.get_event_loop().run_until_complete(main()) 