from math import floor
from random import getrandbits, seed
from model.ActionType import ActionType
from model.Direction import Direction
from model.Game import Game
from model.Move import Move
from model.Trooper import Trooper
from model.TrooperStance import TrooperStance
from model.World import World

from model.TrooperType import TrooperType
from model.CellType import CellType
from model.BonusType import BonusType
from model.Unit import Unit

gotox = -1
gotoy = -1
need_request = False

########################################################
########################################################
########################################################

# Fill the array using wave method to find the shortest path to unit
def wave_forward(me, world, game, move, unit):
	#print "wave_forward: my position ", me.x, me.y  
	#print "wave_forward: unit position ", unit.x, unit.y

	w = [[0 for x in xrange(world.height)] for y in xrange(world.width)]

	for trooper in world.troopers:
		w[trooper.x][trooper.y] = -1
	w[me.x][me.y] = 1
	w[unit.x][unit.y] = 0

	ReachTheEnd = False
	iter = 2
	
	while not ReachTheEnd:
		for i in range(world.width):
			for j in range(world.height):
				if w[i][j] == iter - 1:

					if j-1 >= 0 and w[i][j-1] == 0 and world.cells[i][j-1] == CellType.FREE:
						w[i][j-1] = iter

					if i+1 < world.width and w[i+1][j] == 0 and world.cells[i+1][j] == CellType.FREE:
						w[i+1][j] = iter

					if j+1 < world.height and w[i][j+1] == 0 and world.cells[i][j+1] == CellType.FREE:
						w[i][j+1] = iter

					if i-1 >= 0 and w[i-1][j] == 0 and world.cells[i-1][j] == CellType.FREE:
						w[i-1][j] = iter

				if w[unit.x][unit.y] >= 1:
					ReachTheEnd = True
					#print "wave_forward: unit is in ", w[unit.x][unit.y]-1, " steps"
					break

			if ReachTheEnd:
				break

		iter = iter + 1
		if iter > world.width * world.height:
			break

	if not ReachTheEnd:
		#print "wave_forward: cannot reach the unit"
		w[unit.x][unit.y] = 100000

	return w



# Recursive function to find the way back in wave algorythm
def wave_back(me, world, w, x, y, iter):
	if iter == 1:
		#print "wave_back: move to ", x, y
		return (x,y)

	if getrandbits(1):
		if y-1 >= 0 and w[x][y-1] == iter:
			return wave_back(me, world, w, x, y-1, iter-1)	

		if x+1 < world.width and w[x+1][y] == iter:
			return wave_back(me, world, w, x+1, y, iter-1)

		if y+1 < world.height and w[x][y+1] == iter:
			return wave_back(me, world, w, x, y+1, iter-1)

		if x-1 >= 0 and w[x-1][y] == iter:
			return wave_back(me, world, w, x-1, y, iter-1)
	else:
		if x-1 >= 0 and w[x-1][y] == iter:
			return wave_back(me, world, w, x-1, y, iter-1)

		if y+1 < world.height and w[x][y+1] == iter:
			return wave_back(me, world, w, x, y+1, iter-1)

		if x+1 < world.width and w[x+1][y] == iter:
			return wave_back(me, world, w, x+1, y, iter-1)

		if y-1 >= 0 and w[x][y-1] == iter:
			return wave_back(me, world, w, x, y-1, iter-1)	

	#print "wave_back: error"
	return (me.x, me.y)





# What is the distance from me to unit
def get_distance(me, world, game, move, unit):
	w = wave_forward(me, world, game, move, unit)
	return w[unit.x][unit.y] - 1


# Find the next cell to move to reach the unit
def next_step(me, world, game, move, unit):	
	w = wave_forward(me, world, game, move, unit)

	if w[unit.x][unit.y] >= 100000:
		#print "next_step: cannot reach the unit"
		return (me.x, me.y)

	return wave_back(me, world, w, unit.x, unit.y, w[unit.x][unit.y] - 1)


def move_to_unit(me, world, game, move, unit):
	if (   (me.stance == TrooperStance.STANDING and me.action_points < game.standing_move_cost)
		or (me.stance == TrooperStance.KNEELING and me.action_points < game.kneeling_move_cost)	
		or (me.stance == TrooperStance.PRONE	and me.action_points < game.prone_move_cost)  ):
		move.action = ActionType.END_TURN
		#print "move_to_unit: cannot make move"
		return False

	move.action = ActionType.MOVE

	x, y = next_step(me, world, game, move, unit)

	if x > me.x and world.cells[me.x+1][me.y] == CellType.FREE:
		move.direction = Direction.EAST
		#print "move_to_unit: move east from ", me.x, me.y
		return True
	elif x < me.x and world.cells[me.x-1][me.y] == CellType.FREE:	
		move.direction = Direction.WEST
		#print "move_to_unit: move west from ", me.x, me.y
		return True
	elif y > me.y and world.cells[me.x][me.y+1] == CellType.FREE:	
		move.direction = Direction.SOUTH
		#print "move_to_unit: move south from", me.x, me.y
		return True
	elif y < me.y and world.cells[me.x][me.y-1] == CellType.FREE:	
		move.direction = Direction.NORTH
		#print "move_to_unit: move north from", me.x, me.y
		return True
	
	move.action = ActionType.END_TURN
	#print "move_to_unit: skip move"
	return False


def safe_move_to_unit(me, world, game, move, unit):
	if (   (me.stance == TrooperStance.STANDING and me.action_points < game.standing_move_cost)
		or (me.stance == TrooperStance.KNEELING and me.action_points < game.kneeling_move_cost)	
		or (me.stance == TrooperStance.PRONE	and me.action_points < game.prone_move_cost)  ):
		move.action = ActionType.END_TURN
		#print "safe_move_to_unit: cannot make move"
		return False

	move.action = ActionType.MOVE

	x, y = next_step(me, world, game, move, unit)
	cell = Unit(-1000, x, y)
	if not cell_is_safe(me, world, game, move, cell) and me.action_points < 2 * get_move_cost(me, world, game, move):
		return False

	if x > me.x and world.cells[me.x+1][me.y] == CellType.FREE:
		move.direction = Direction.EAST
		#print "safe_move_to_unit: move east from ", me.x, me.y
		return True
	elif x < me.x and world.cells[me.x-1][me.y] == CellType.FREE:	
		move.direction = Direction.WEST
		#print "safe_move_to_unit: move west from ", me.x, me.y
		return True
	elif y > me.y and world.cells[me.x][me.y+1] == CellType.FREE:	
		move.direction = Direction.SOUTH
		#print "safe_move_to_unit: move south from", me.x, me.y
		return True
	elif y < me.y and world.cells[me.x][me.y-1] == CellType.FREE:	
		move.direction = Direction.NORTH
		#print "safe_move_to_unit: move north from", me.x, me.y
		return True
	
	move.action = ActionType.END_TURN
	#print "safe_move_to_unit: skip move"
	return False



def find_free_cell(me, world, game, move, unit):	
	for i in range(min(world.width, world.height)):
		for j in [z for z in range(unit.x - i, unit.x + i) if 0<=z<world.width]:
			for k in [z for z in range(unit.y - i, unit.y + i) if 0<=z<world.height]:
				if world.cells[j][k] == CellType.FREE:
					target = Unit(-1000, j, k)
					#print "find_free_cell: original ", unit.x, ", ", unit.y
					#print "find_free_cell: target found ", j, ", ", k
					return target

	#print "find_free_cell: cannot find free cell ", unit.x, ", ", unit.y
	return unit


# Patrol the territory clockwise
def patrol(me, world, game, move):
	global gotox
	global gotoy
	global need_request

	deltax = 6
	deltay = 4

	if gotox < 0 or gotoy < 0 or me.get_distance_to(gotox, gotoy) < 3:
		#print "patrol: where to go?"
		commander = [trooper for trooper in world.troopers if trooper.teammate and trooper.type == TrooperType.COMMANDER]
		if commander:
			need_request = True
			gotox, gotoy = -1, -1
			print "patrol: made request"
			#move.action = ActionType.END_TURN			
			#return False
			#else:
		print "patrol: cycle move"
		if me.x <= world.width / 2 and me.y <= world.height / 2:
			gotox, gotoy = world.width  - deltax, deltay
			#print "patrol: new direction east"
		elif me.x >= world.width / 2 and me.y <= world.height / 2:
			gotox, gotoy =  world.width  - deltax, world.height - deltay
			#print "patrol: new direction south"
		elif me.x >= world.width / 2 and me.y >= world.height / 2:
			gotox, gotoy = deltax, world.height - deltay
			#print "patrol: new direction west"
		elif me.x <= world.width / 2 and me.y >= world.height / 2:
			gotox, gotoy = deltax, deltay
			#print "patrol: new direction north"

	print "patrol: me", me.x, me.y		
	print "patrol: direction", gotox, gotoy	

	if me.action_points >= get_move_cost(me, world, game, move):
		unit = Unit(-1000, gotox, gotoy)
		target = find_free_cell(me, world, game, move, unit)
		if safe_move_to_unit(me, world, game, move, target):
			return True

	move.action = ActionType.END_TURN
	#print "patrol: cannot move"
	return False	

########################################################

def cell_is_safe(me, world, game, move, cell):
	enemy_troopers = [trooper for trooper in world.troopers if not trooper.teammate]
	for enemy in enemy_troopers:
		if (world.is_visible(enemy.shooting_range, enemy.x, enemy.y, enemy.stance, cell.x, cell.y, me.stance)
 				and enemy.shooting_range >= enemy.get_distance_to_unit(me)):
			return False
	
	return True


def cell_is_free(me, world, game, move, cell):
	if world.cells[cell.x][cell.y] != CellType.FREE:
		return False

	my_troopers = [trooper for trooper in world.troopers if trooper.teammate]
	for my_trooper in my_troopers:
		if my_trooper.x == cell.x and my_trooper.y == cell.y:
			return False

	return True


def find_safe_cell(me, world, game, move):
	#n_of_moves = int(floor(1.0 * me.action_points / get_move_cost(me, world, game, move)))
	n_of_moves = me.action_points / get_move_cost(me, world, game, move) + 1
	safe_cells = []

	for i in [z for z in range(me.x - n_of_moves, me.x + n_of_moves) if 0<=z<world.width]:
		for j in [z for z in range(me.y - n_of_moves, me.y + n_of_moves) if 0<=z<world.height]:
			cell = Unit(-1000, i, j)
			if cell_is_safe(me, world, game, move, cell) and cell_is_free(me, world, game, move, cell):
				safe_cells.append(cell)

	if safe_cells:
		safe_cells.sort(key=lambda t: get_distance(me, world, game, move, t))
		return safe_cells[0]
	else:
		return None

def i_can_kill(me, world, game, move):
	if me.action_points < me.shoot_cost:
		return False

	troopers = [trooper for trooper in world.troopers if not trooper.teammate]
	troopers.sort(key=lambda t: t.hitpoints)
	
	for trooper in troopers:
		canSee = world.is_visible(me.shooting_range,
			me.x, me.y, me.stance,
			trooper.x, trooper.y, trooper.stance)

		if me.shooting_range >= me.get_distance_to_unit(trooper):
			canReach = True
		else:
			canReach = False

		if canSee and canReach and trooper.hitpoints <= get_damage(me, world, game, move) * floor(1.0 * me.action_points / me.shoot_cost)	:
			return True

	return False


def i_see_enemy(me, world, game, move, stance):
	if me.action_points < me.shoot_cost:
		return False

	troopers = [trooper for trooper in world.troopers if not trooper.teammate]
	troopers.sort(key=lambda t: t.hitpoints)
	
	for trooper in troopers:
		if world.is_visible(me.shooting_range, me.x, me.y, me.stance, trooper.x, trooper.y, trooper.stance):
			return True

	return False


########################################################

def start_log(me, world, game):
	
	print "-------------------------------------"

	if me.type == TrooperType.COMMANDER:
		print "Commander", world.move_index
	elif me.type == TrooperType.FIELD_MEDIC:
		print "Medic", world.move_index
	elif me.type == TrooperType.SOLDIER:
		print "Soldier", world.move_index
	elif me.type == TrooperType.SNIPER:
		print "Sniper", world.move_index
	elif me.type == TrooperType.SCOUT:
		print "Scout", world.move_index

	#print "action points: ", me.action_points 
	#print "shoot cost: ", me.shoot_cost 
	#print "standing_move_cost: ", game.standing_move_cost
	#print "hitpoints: ", me.hitpoints
	#print "maximal hitpoints: ", me.maximal_hitpoints
	#print "holding_medikit", me.holding_medikit 
	#print "holding_field_ration", me.holding_field_ration 


def get_move_cost(me, world, game, move):
	if me.stance == TrooperStance.STANDING:
		return game.standing_move_cost
	if me.stance == TrooperStance.KNEELING:
		return game.kneeling_move_cost
	if me.stance == TrooperStance.PRONE:
		return game.prone_move_cost


def get_damage(me, world, game, move):
	if me.stance == TrooperStance.STANDING:
		return me.standing_damage
	if me.stance == TrooperStance.KNEELING:
		return me.kneeling_damage
	if me.stance == TrooperStance.PRONE:
		return me.prone_damage


def get_troopertype_name(trooper):
	if trooper.type == TrooperType.COMMANDER:
		return "commander"
	if trooper.type == TrooperType.FIELD_MEDIC:
		return "medic"
	if trooper.type == TrooperType.SOLDIER:
		return "soldier"
	if trooper.type == TrooperType.SNIPER:
		return "sniper"
	if trooper.type == TrooperType.SCOUT:
		return "scout"


def shoot_weakest(me, world, game, move):
	if me.action_points < me.shoot_cost:
		move.action = ActionType.END_TURN
		#print "shoot_weakest: cannot shoot"
		return False

	troopers = [trooper for trooper in world.troopers if not trooper.teammate]
	troopers.sort(key=lambda t: t.hitpoints)
	
	for trooper in troopers:
		canSee = world.is_visible(me.shooting_range,
			me.x, me.y, me.stance,
			trooper.x, trooper.y, trooper.stance)

		if me.shooting_range >= me.get_distance_to_unit(trooper):
			canReach = True
		else:
			canReach = False

		if canSee and canReach and not trooper.teammate:
			#if use_bonus_ration(me, world, game, move, me.shoot_cost):
			#	return True			
			if stance_before_shoot(me, world, game, move):
				return True
			move.action = ActionType.SHOOT
			move.x = trooper.x
			move.y = trooper.y
			print "shoot_weakest: made shoot to", trooper.x, trooper.y
			print "shoot_weakest: target", get_troopertype_name(trooper)
			return True

	move.action = ActionType.END_TURN
	#print "shoot_weakest: skip shoot"
	return False



def use_bonus_medikit(me, world, game, move):
	if (me.action_points >= game.medikit_use_cost 
			and me.holding_medikit 
			and 0.8 * game.medikit_heal_self_bonus_hitpoints + me.hitpoints <= me.maximal_hitpoints):
		move.action = ActionType.USE_MEDIKIT
		move.direction = Direction.CURRENT_POINT
		print "use_bonus_medikit: using medikit"
		return True

	move.action = ActionType.END_TURN
	#print "use_bonus_medikit: cannot use medikit"
	return False



def use_bonus_ration(me, world, game, move, cost):
	if (me.action_points >= game.field_ration_eat_cost 
			and me.holding_field_ration 
			#and game.field_ration_bonus_action_points - game.field_ration_eat_cost >= cost
			and floor(1.0*me.action_points/cost) < floor(1.0*(me.action_points+game.field_ration_bonus_action_points - game.field_ration_eat_cost) / cost)
			and me.action_points - game.field_ration_eat_cost + game.field_ration_bonus_action_points <= me.initial_action_points
		):

		move.action = ActionType.EAT_FIELD_RATION
		move.direction = Direction.CURRENT_POINT
		print "use_bonus_ration: eat ration"
		return True

	move.action = ActionType.END_TURN
	#print "use_bonus_ration: cannot use ration"
	return False


def use_bonus_grenade(me, world, game, move):
	if (me.holding_grenade and me.action_points >= game.grenade_throw_cost):
		my_troopers = [trooper for trooper in world.troopers if trooper.teammate]
		enemy_troopers = [trooper for trooper in world.troopers if not trooper.teammate]

		max_damage = 0	
		max_trooper = None

		for x in [z for z in range(me.x - int(game.grenade_throw_range), me.x + int(game.grenade_throw_range)) if 0<=z<world.width]:
			for y in [z for z in range(me.y - int(game.grenade_throw_range), me.y + int(game.grenade_throw_range)) if 0<=z<world.height]:
				damage_to_me = False
				unit = Unit(-1000, x, y)

				if me.get_distance_to_unit(unit) > game.grenade_throw_range:	
					continue				

				for my_trooper in my_troopers:
					if my_trooper.get_distance_to_unit(unit) < 1.05:
						damage_to_me = True
						break

				if damage_to_me:
					continue

				damage = 0

				for enemy_trooper in enemy_troopers:
					if 0.95 < enemy_trooper.get_distance_to_unit(unit) < 1.05:
						damage = damage + game.grenade_collateral_damage
					elif enemy_trooper.get_distance_to_unit(unit) < 0.95:
						damage = damage + game.grenade_direct_damage
						max_trooper = enemy_trooper

				if damage > max_damage:
					max_damage = damage
					max_unit = unit

		if (   
			   (me.stance == TrooperStance.STANDING and 1.0 * max_damage / game.grenade_throw_cost * me.shoot_cost / me.standing_damage > 1.0)
			or (me.stance == TrooperStance.KNEELING and 1.0 * max_damage / game.grenade_throw_cost * me.shoot_cost / me.kneeling_damage > 1.0)
			or (me.stance == TrooperStance.PRONE	and 1.0 * max_damage / game.grenade_throw_cost * me.shoot_cost / me.prone_damage	> 1.0)	
			or (max_trooper and not world.is_visible(me.shooting_range, me.x, me.y, me.stance, max_trooper.x, max_trooper.y, max_trooper.stance))
			):
			print "use_bonus_grenade: damage = ", max_damage
			print "use_bonus_grenade: me ", me.x, me.y
			print "use_bonus_grenade: target", max_unit.x, max_unit.y		
			print "use_bonus_grenade: distance", me.get_distance_to_unit(max_unit)
			move.action = ActionType.THROW_GRENADE
			move.x = max_unit.x
			move.y = max_unit.y
			return True

	#print "use_bonus_grenade: cannot use grenade"		
	move.action = ActionType.END_TURN
	return False


def stance_before_shoot(me, world, game, move):
	if (
			me.stance == TrooperStance.STANDING
			and i_see_enemy(me, world, game, move, TrooperStance.KNEELING)
			and me.action_points >= game.stance_change_cost + me.shoot_cost
			and cell_is_safe(me, world, game, move, me)
		):
		move.action = ActionType.LOWER_STANCE
		print "stance_before_shoot: >> kneeling"
		return True

	if (
			me.stance == TrooperStance.KNEELING
			and i_see_enemy(me, world, game, move, TrooperStance.PRONE)
			and me.action_points >= game.stance_change_cost + me.shoot_cost
			and cell_is_safe(me, world, game, move, me)
		):
		move.action = ActionType.LOWER_STANCE
		print "stance_before_shoot: >> prone"
		return True

	move.action = ActionType.END_TURN
	#print "stance_before_shoot: cannot lower stance"
	return False	


def unstance(me, world, game, move):
	if (#need_request
			me.stance == TrooperStance.PRONE
			and not i_see_enemy(me, world, game, move, TrooperStance.KNEELING)
			and cell_is_safe(me, world, game, move, me)
			and me.action_points >= game.stance_change_cost + get_move_cost(me, world, game, move)
		): 
		move.action = ActionType.RAISE_STANCE
		print "unstance: >> KNEELING"
		return True

	if (#need_request
			me.stance == TrooperStance.KNEELING
			and not i_see_enemy(me, world, game, move, TrooperStance.STANDING)
			and cell_is_safe(me, world, game, move, me)
			and me.action_points >= game.stance_change_cost + get_move_cost(me, world, game, move)
		): 
		move.action = ActionType.RAISE_STANCE
		print "unstance: STANDING"
		return True

	move.action = ActionType.END_TURN
	#print "stance_before_shoot: cannot lower stance"
	return False	


def medic_heal(me, world, game, move):
	if me.type == TrooperType.FIELD_MEDIC:
		troopers = [trooper for trooper in world.troopers if trooper.teammate and trooper.type != TrooperType.FIELD_MEDIC]
		troopers.sort(key=lambda t: me.get_distance_to_unit(t))
		#print "medic_heal: len(troopers) ", len(troopers)

		if ( troopers
			 and me.get_distance_to_unit(troopers[0]) <= 1.01 
			 and troopers[0].hitpoints + 0.8 * game.field_medic_heal_bonus_hitpoints <= me.maximal_hitpoints
			 and me.action_points >= game.field_medic_heal_cost ):			
			print "medic_heal: heal nearest teammate", get_troopertype_name(troopers[0]), troopers[0].x, troopers[0].y
			move.action = ActionType.HEAL
			move.x = troopers[0].x
			move.y = troopers[0].y
			return True
		elif ( me.hitpoints + 0.8 * game.field_medic_heal_self_bonus_hitpoints <= me.maximal_hitpoints 
			   and me.action_points >= game.field_medic_heal_cost):
			move.action = ActionType.HEAL
			move.direction = Direction.CURRENT_POINT
			print "medic_heal: self heal"
			return True
		elif troopers:
			troopers.sort(key=lambda t: 5 * t.type + t.hitpoints + 5 * get_distance(me, world, game, move, t))

			#if troopers[0].hitpoints > 0.8 * troopers[0].maximal_hitpoints and shoot_weakest(me, world, game, move): 
			#	return True
			if me.get_distance_to_unit(troopers[0]) > 1.1 and move_to_unit(me, world, game, move, troopers[0]):
				print "medic_heal: move to nearest teammate", get_troopertype_name(troopers[0])
				return True
			elif shoot_weakest(me, world, game, move):
				return True
			elif me.get_distance_to_unit(troopers[0]) < 1.1:
				move.action = ActionType.END_TURN
				return True

	move.action = ActionType.END_TURN
	#print "medic: no action"
	return False


def nonmedic_heal(me, world, game, move):
	if me.holding_medikit and me.action_points >= game.medikit_use_cost: 
		troopers = [trooper for trooper in world.troopers 
							if trooper.teammate 
							   and trooper.type != me.type
							   and me.get_distance_to_unit(trooper) <= 1.1]
		
		troopers.sort(key=lambda t: t.hitpoints)

		if ( troopers
			 and troopers[0].hitpoints + 0.8 * game.medikit_bonus_hitpoints <= troopers[0].maximal_hitpoints
			  ):			
			print "nonmedic_heal: heal nearest teammate ", get_troopertype_name(troopers[0]), troopers[0].x, troopers[0].y
			move.action = ActionType.USE_MEDIKIT
			move.x = troopers[0].x
			move.y = troopers[0].y
			return True

	move.action = ActionType.END_TURN
	#print "nonmedic: no action"
	return False



def commander_request(me, world, game, move):
	global gotox
	global gotoy
	global need_request

	if me.type == TrooperType.COMMANDER:
		players = [player for player in world.players 
						  if player.name != 'zoldatoff' 
						  	 and player.name != 'MyStrategy'
						  	 and player.approximate_x >= 0
						  	 and player.approximate_y >= 0
						  	 ]	

		if players:
			min_player = players[0]
			min_distance = 10000
			for player in players:
				unit = Unit(-player.id, player.approximate_x, player.approximate_y)
				distance = get_distance(me, world, game, move, unit)
				if distance < min_distance:
					min_distance = distance
					min_player = player

			if gotox >= 0 and gotoy >= 0:
				gotox, gotoy = min_player.approximate_x, min_player.approximate_y
				need_request = False
				print "commander_request: new destination", gotox, gotoy
				return False

	if (me.type == TrooperType.COMMANDER
			and me.action_points >= game.commander_request_enemy_disposition_cost
			and need_request):
		move.action = ActionType.REQUEST_ENEMY_DISPOSITION
		need_request = False
		print "commander_request: request sent"
		return True

	move.action = ActionType.END_TURN
	#print "commander_request: no action"
	return False 


def team_building(me, world, game, move, my_type, teammate_type, distance):
	if me.type == my_type:
		troopers = [trooper for trooper in world.troopers 
					if trooper.teammate 
					   and trooper.type == teammate_type
					   and me.get_distance_to_unit(trooper) > distance]
		if troopers:
			troopers.sort(key=lambda t: get_distance(me, world, game, move, t))
			print "team_building: move to", get_troopertype_name(troopers[0])
			if safe_move_to_unit(me, world, game, move, troopers[0]):
				return True	 

	move.action = ActionType.END_TURN
	return False 


def move_to_enemy(me, world, game, move):
	troopers = [trooper for trooper in world.troopers if not trooper.teammate]

	if (troopers  
			and me.action_points >= me.shoot_cost + get_move_cost(me, world, game, move)
			and me.type != TrooperType.FIELD_MEDIC
			):
		troopers.sort(key=lambda t:me.get_distance_to_unit(t))
		print "move_to_enemy: ", get_troopertype_name(troopers[0])
		if move_to_unit(me, world, game, move, troopers[0]): 
			return True

	move.action = ActionType.END_TURN
	return False 

# def random_move(me, world, game, move, i=0):
# 	if i > 10:
# 		print "random move unavailible"
# 		return False

# 	seed()

# 	if getrandbits(1):
# 		dx = 1
# 	else:
# 		dx = -1

# 	if getrandbits(1):
# 		dy = 1
# 	else:
# 		dy = -1

# 	print "trying to make a random move"   
# 	target = Unit(-1000, me.x + dx, me.y + dy)
# 	if move_to_unit(me, world, game, move, target):
# 		print "randome move done"
# 		return True
# 	else:
# 		random_move(me, world, game, move,i+1)




########################################################

class MyStrategy:
	def move(self, me, world, game, move):
		start_log(me, world, game)

		#print "1. Use medikit"
		#if nonmedic_heal(me, world, game, move): return
		#if use_bonus_medikit(me, world, game, move): return
		if i_see_enemy(me, world, game, move, me.stance) and use_bonus_ration(me, world, game, move, 1):
			return

		if me.hitpoints < me.maximal_hitpoints / 2 and use_bonus_medikit(me, world, game, move): return

		if me.type == TrooperType.FIELD_MEDIC and nonmedic_heal(me, world, game, move): return

		#print "2. Medic: heal"
		if medic_heal(me, world, game, move): return

		if use_bonus_grenade(me, world, game, move): return

		if not cell_is_safe(me, world, game, move, me) and not i_can_kill(me, world, game, move):
			print "safecell: ----------------"
			print "safecell: cell is not safe", me.x, me.y
			safe_cell = find_safe_cell(me, world, game, move)
			#if safe_cell:
				#print "safecell: cell is safe", safe_cell.x, safe_cell.y
				#print "safecell: action_points", me.action_points
				#print "safecell: distance", get_distance(me, world, game, move, safe_cell) 
				#print "safecell: move cost", get_move_cost(me, world, game, move)
				#print "safecell: shoot cost", me.shoot_cost
			#else:
				#print "safecell: no safe cell"
			if (safe_cell 
					and me.action_points < get_distance(me, world, game, move, safe_cell) * get_move_cost(me, world, game, move) + me.shoot_cost
					#and me.action_points >= get_distance(me, world, game, move, safe_cell) * get_move_cost(me, world, game, move) 
					and move_to_unit(me, world, game, move, safe_cell)):
				print "safecell: go from", me.x, me.y
				print "safecell: go to", safe_cell.x, safe_cell.y
				return


		#print "3. Try to shoot"
		if shoot_weakest(me, world, game, move): return

		# if (me.type == TrooperType.SOLDIER
		# 		and me.hitpoints < 0.9 * me.maximal_hitpoints
		#  		and team_building(me, world, game, move, TrooperType.SOLDIER, TrooperType.COMMANDER, 0)):	
		# 	return

		

		#print "4. Use medikit"	
		if nonmedic_heal(me, world, game, move): return
		if use_bonus_medikit(me, world, game, move): return


		#print "10. Unstance"
		if unstance(me, world, game, move): return


		if (me.type == TrooperType.SOLDIER
		 		and me.hitpoints < 0.6 * me.maximal_hitpoints
		  		and team_building(me, world, game, move, TrooperType.SOLDIER, TrooperType.FIELD_MEDIC, 0)):	
			return


		#print "5. Commander request"			
		if (	me.type == TrooperType.COMMANDER
				and cell_is_safe(me, world, game, move, me) 
				and commander_request(me, world, game, move)
			): 
			return



		#print "11. Move to medikit"
		bonuses_medikit = [bonus for bonus in world.bonuses if bonus.type == BonusType.MEDIKIT]
		if bonuses_medikit and not me.holding_medikit:
			bonuses_medikit.sort(key=lambda t: get_distance(me, world, game, move, t))
			print "trying to move to nearest bonus medikit"
			if safe_move_to_unit(me, world, game, move, bonuses_medikit[0]): return

					


		#print "9. Moving to enemy"
		if me.hitpoints > 0.9 * me.maximal_hitpoints and move_to_enemy(me, world, game, move): return


		#print "6. Commander >> soldier"
		if team_building(me, world, game, move, TrooperType.COMMANDER, TrooperType.SOLDIER, 0.6 * game.commander_aura_range):	
			return

		#print "7. Sniper >> commander >> soldier"	
		if team_building(me, world, game, move, TrooperType.SNIPER, TrooperType.COMMANDER, 1.0 * game.commander_aura_range):	
			return

		if team_building(me, world, game, move, TrooperType.SNIPER, TrooperType.SOLDIER, 1.0 * game.commander_aura_range):	
			return


		#print "8. Soldier >> commander >> sniper"	
		if team_building(me, world, game, move, TrooperType.SOLDIER, TrooperType.COMMANDER, 1.6 * game.commander_aura_range):	
			return  

		if team_building(me, world, game, move, TrooperType.SOLDIER, TrooperType.SNIPER, 1.6 * game.commander_aura_range):	
			return


		#print "12. Move to ration"
		bonuses_ration = [bonus for bonus in world.bonuses if bonus.type == BonusType.FIELD_RATION]
		if bonuses_ration and not me.holding_field_ration:
			bonuses_ration.sort(key=lambda t: get_distance(me, world, game, move, t))
			print "trying to move to nearest ration"
			if safe_move_to_unit(me, world, game, move, bonuses_ration[0]): return


		#print "13. Move to grenade"
		bonuses_grenade = [bonus for bonus in world.bonuses if bonus.type == BonusType.GRENADE]
		if bonuses_grenade and not me.holding_grenade:
			bonuses_grenade.sort(key=lambda t: get_distance(me, world, game, move, t))
			print "trying to move to nearest grenade"
			if safe_move_to_unit(me, world, game, move, bonuses_grenade[0]): return
		


		#print "14. Patrol"		
		#if me.type != TrooperType.FIELD_MEDIC and patrol(me, world, game, move): return
		if patrol(me, world, game, move): return


		#print "15. End turn"
		move.action = ActionType.END_TURN
		return		