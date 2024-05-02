from poke_env.environment.move_category import MoveCategory

'''
Calculates damage done by one Pokemon to another given a move
Accepts a boolean to check whether the Bot is the attacker or defender
'''

def calculate_damage(move, attacker, defender, is_bot_turn):
    # NULL Status move does no damage
    if move is None or move.category == MoveCategory.STATUS:
        return 0
    damage = move.base_power
    ratio = 1
    # Calculate corresponding attack to defense ratio
    if move.category == MoveCategory.PHYSICAL:
        ratio = calculate_physical_ratio(attacker, defender, is_bot_turn)
    elif move.category == MoveCategory.SPECIAL:
        ratio = calculate_special_ratio(attacker, defender, is_bot_turn)
    # Modify damage according to the official Pokemon damage formula
    damage *= ratio
    level_multiplier = ((2 * attacker.level) / 5 ) + 2
    damage *= level_multiplier
    damage = (damage / 50) + 2
    if move.type == attacker.type_1 or move.type == attacker.type_2:
        damage *= 1.5
    type_multiplier = defender.damage_multiplier(move)
    damage *= type_multiplier
    return damage


'''
Calculate ratio of attack stat to defense stat, scaled by level
Accepts a boolean to check whether the Bot is the attacker or defender
'''
def calculate_physical_ratio(attacker, defender, is_bot_turn):
    if is_bot_turn:
        attack = attacker.stats["atk"]
        defense = 2 * defender.base_stats["def"] + 31
        defense = ((defense * defender.level) / 100 ) + 5
        return attack / defense 
    else:
        defense = defender.stats["def"]
        attack = 2 * attacker.base_stats["atk"] + 31
        attack = ((attack * attacker.level) / 100) + 5  
        return attack / defense 
    

'''
Calculate ratio of special attack stat to special defense stat, scaled by level
Accepts a boolean to check whether the Bot is the attacker or defender
'''
def calculate_special_ratio(attacker, defender, is_bot_turn):
    if is_bot_turn:
        spatk = attacker.stats["spa"]
        spdef = 2 * defender.base_stats["spd"] + 31
        spdef = ((spdef * defender.level) / 100 ) + 5
        return spatk / spdef
    else: 
        spdef = defender.stats["spd"]
        spatk = 2 * attacker.base_stats["spa"] + 31
        spatk = ((spatk * attacker.level) / 100) + 5
        return spatk / spdef
    
'''
Helper function to identify which of the two Pokemon is faster, scaled by level
'''
def opponent_can_outspeed(my_pokemon, opponent_pokemon):
    my_speed = my_pokemon.stats["spe"]
    opponent_max_speed = 2 * opponent_pokemon.base_stats["spe"] + 31
    opponent_max_speed = ((opponent_max_speed * opponent_pokemon.level) / 100) + 5
    return opponent_max_speed > my_speed


'''
Helper function to calculate the HP stat of a Pokemon, scaled by level
'''
def calculate_total_HP(pokemon): 
    HP = pokemon.base_stats["hp"] * 2 + 31
    HP = ((HP * pokemon.level) / 100)
    HP += pokemon.level + 10
    return HP

'''
Helper function to identify the largest weakness based on type
Calculates the type multiplier for each matchup of types for the defending Pokemon
and the attacking Pokemon, and returns the largest one
'''
def get_defensive_type_multiplier(my_pokemon, opponent_pokemon):
    multiplier = 1
    first_type = opponent_pokemon.type_1
    first_multiplier = my_pokemon.damage_multiplier(first_type)
    second_type = opponent_pokemon.type_2
    if second_type is None:
        return first_multiplier
    second_multiplier = my_pokemon.damage_multiplier(second_type)
    multiplier = first_multiplier if first_multiplier > second_multiplier else second_multiplier
    return multiplier