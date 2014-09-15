from math import *

from model.ActionType import ActionType
from model.Game import Game
from model.Hockeyist import Hockeyist
from model.Move import Move
from model.World import World

from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType


def getPlayer(me, world):
    for player in world.players:
        if player.id == me.player_id:
            return player

def getNearestOpponent(me, world):
    nearestOpponent = None
    nearestOpponentRange = 1.0e8

    for hockeyist in world.hockeyists:
        if (not(hockeyist.teammate)
            and hockeyist.type != HockeyistType.GOALIE
            and hockeyist.state != HockeyistState.KNOCKED_DOWN
            and hockeyist.state != HockeyistState.RESTING
            and me.get_distance_to_unit(hockeyist) < nearestOpponentRange):
            nearestOpponent = hockeyist
            nearestOpponentRange = me.get_distance_to_unit(hockeyist)

    return nearestOpponent


def getPartner(me, world, game):

    opponentPlayer = world.get_opponent_player()
    targetX = opponentPlayer.net_front
    targetY = 0.5 * (opponentPlayer.net_bottom + opponentPlayer.net_top)

    bestPartner = None
    bestPartnerRange = 1.0e8 #me.get_distance_to(targetX, targetY)

    for hockeyist in world.hockeyists:
        if (hockeyist.teammate
            and hockeyist.type != HockeyistType.GOALIE
            and hockeyist.state == HockeyistState.ACTIVE
            and hockeyist.get_distance_to(targetX, targetY) < bestPartnerRange):
            bestPartner = hockeyist
            bestPartnerRange = hockeyist.get_distance_to(targetX, targetY)

    return bestPartner



def chooseSkate(me, world, game):
    if not(me):
        return None

    if me.state != HockeyistState.ACTIVE:
        return None

    opponentPlayer = world.get_opponent_player()
    rink_center_x = 0.5 * (game.rink_left + game.rink_right)
    rink_center_y = 0.5 * (game.rink_top + game.rink_bottom)
    min_strike_dist_x = 0.8 * (opponentPlayer.net_bottom - opponentPlayer.net_top)
    max_strike_dist_x = 2.0 * (opponentPlayer.net_bottom - opponentPlayer.net_top)
    min_strike_dist_y = 0.6 * (opponentPlayer.net_bottom - opponentPlayer.net_top)
    max_strike_dist_y = 1.3 * (opponentPlayer.net_bottom - opponentPlayer.net_top)

    if world.tick > game.tick_count:
        min_strike_dist_x = 0
        max_strike_dist_x = game.world_width
        min_strike_dist_y = 0
        max_strike_dist_y = game.world_height

    if (min_strike_dist_x < abs(me.x - opponentPlayer.net_front) < max_strike_dist_x
        and
        min_strike_dist_y < abs(me.y - rink_center_y) < max_strike_dist_y
        ):
        return None

    if abs(me.x - opponentPlayer.net_front) < min_strike_dist_x and opponentPlayer.net_front < rink_center_x:
        gotoX = opponentPlayer.net_front + min_strike_dist_x + 1
    elif abs(me.x - opponentPlayer.net_front) > min_strike_dist_x and opponentPlayer.net_front < rink_center_x:
        gotoX = opponentPlayer.net_front + max_strike_dist_x - 1
    elif abs(me.x - opponentPlayer.net_front) < min_strike_dist_x and opponentPlayer.net_front > rink_center_x:
        gotoX = opponentPlayer.net_front - min_strike_dist_x - 1
    elif abs(me.x - opponentPlayer.net_front) > min_strike_dist_x and opponentPlayer.net_front > rink_center_x:
        gotoX = opponentPlayer.net_front - max_strike_dist_x + 1
    else:
        gotoX = me.x


    if me.y < rink_center_y - max_strike_dist_y:
        gotoY = rink_center_y - max_strike_dist_y + 1
    elif rink_center_y - min_strike_dist_y < me.y < rink_center_y:
        gotoY = rink_center_y - min_strike_dist_y - 1
    elif rink_center_y < me.y < rink_center_y +  min_strike_dist_y:
        gotoY = rink_center_y + min_strike_dist_y + 1
    elif me.y > rink_center_y + max_strike_dist_y:
        gotoY = rink_center_y + max_strike_dist_y - 1
    else:
        gotoY = me.y

    return me.get_angle_to(gotoX, gotoY)



def chooseSwing(me, world, game):
    if not(me):
        return None

    if me.state != HockeyistState.ACTIVE:
        return None

    if chooseSkate(me, world, game) != None:
        return None

    opponentPlayer = world.get_opponent_player()
    rink_center_x = 0.5 * (game.rink_left + game.rink_right)
    rink_center_y = 0.5 * (game.rink_top + game.rink_bottom)

    if me.y < rink_center_y:
        swingtoY = opponentPlayer.net_bottom - world.puck.radius
    else:
        swingtoY = opponentPlayer.net_top + world.puck.radius

    if me.x < rink_center_x:
        swingtoX = opponentPlayer.net_front #+ world.puck.radius
    else:
        swingtoX = opponentPlayer.net_front #- world.puck.radius

    return me.get_angle_to(swingtoX, swingtoY)


def chooseStrike(me, world, game):
    if me.state != HockeyistState.SWINGING:
        return None

    return True


class MyStrategy:

    def move(self, me, world, game, move):
        """
        @type me: Hockeyist
        @type world: World
        @type game: Game
        @type move: Move
        """

        STRIKE_ANGLE = 1.0 * pi / 180.0

        #print world.tick

        if world.puck.owner_player_id == me.player_id:
            if world.puck.owner_hockeyist_id == me.id:
                # Try to move closer to net
                angle = chooseSkate(me, world, game)
                if angle:
                    # Is it better to make a pass?
                    partner = getPartner(me, world, game)
                    if (chooseSwing(partner, world, game)
                        and
                        me.get_distance_to_unit(partner) > 100
                        and
                        -pi/3.0 < me.get_angle_to_unit(partner) < pi/3.0
                        ):
                        move.pass_angle = me.get_angle_to_unit(partner)
                        move.pass_power = 0.9
                        move.action = ActionType.PASS
                        print "PASS"
                    else:
                        move.turn = angle
                        move.speed_up = 1.0
                    return

                # Try to swing
                angle = chooseSwing(me, world, game)
                if angle:
                    move.turn = angle
                    if (abs(angle) < STRIKE_ANGLE):
                        move.action = ActionType.SWING
                    return

                # Try to strike
                if chooseStrike(me, world, game):
                    move.action = ActionType.STRIKE
                    #print "STRIKE PUCK"
                    return


            else:
                # prepare for pass
                angle = chooseSkate(me, world, game)
                if angle:
                    move.turn = angle
                    move.speed_up = 1.0
                    return
                else: # try to strike opponent
                    nearestOpponent = getNearestOpponent(me, world)
                    if nearestOpponent:
                        if me.get_distance_to_unit(nearestOpponent) > game.stick_length:
                            move.speed_up = 1.0
                        elif abs(me.get_angle_to_unit(nearestOpponent)) < 0.5 * game.stick_sector:
                            move.action = ActionType.STRIKE
                            #print "STRIKE OPPONENT"
                        move.turn = me.get_angle_to_unit(nearestOpponent)

        else:
            partner = getPartner(me, world, game)
            if (partner == None
               or
               me.get_distance_to_unit(world.puck) < partner.get_distance_to_unit(world.puck) + 30
               or
               abs(world.puck.x - getPlayer(me, world).net_front) < game.world_width/3.0
               ):
                # Try to catch a puck
                speed = sqrt(me.speed_x*me.speed_x+me.speed_y*me.speed_y)
                if speed == 0: speed = 1.0
                n_tick = me.get_distance_to_unit(world.puck) / speed
                if n_tick > 40: n_tick = 40
                if n_tick < 7: n_tick = 0

                gotoX = world.puck.x + world.puck.speed_x * n_tick
                if gotoX < game.rink_left:  gotoX = me.x
                if gotoX > game.rink_right: gotoX = me.x

                gotoY = world.puck.y + world.puck.speed_y * n_tick
                if gotoY < game.rink_top:     gotoY = me.y
                if gotoY > game.rink_bottom:  gotoY = me.y

                move.speed_up = 1.0
                move.turn = me.get_angle_to(gotoX, gotoY)
                move.action = ActionType.TAKE_PUCK

            else:
                # prepare for pass
                angle = chooseSkate(me, world, game)
                if angle:
                    move.turn = angle
                    move.speed_up = 1.0
                    return
                else:
                    move.speed_up = -0.2
                    return
