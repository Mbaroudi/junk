from math import *

from model.ActionType import ActionType
from model.Game import Game
from model.Hockeyist import Hockeyist
from model.Move import Move
from model.World import World

from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType

from model.Unit import Unit

def deltaAngles(angle1, angle2):
    ret = angle1 - angle2
    ret = (ret + 2.0*pi) % (2.0*pi)
    return ret

def canPass(unit1, unit2, unit3): # unit3 is the point
    px = unit2.x-unit1.x
    py = unit2.y-unit1.y

    something = px*px + py*py

    u =  ((unit3.x - unit1.x) * px + (unit3.y - unit1.y) * py) / float(something)

    if u > 1.0:
        u = 1.0
    elif u < 0.0:
        u = 0.0

    x = unit1.x + u * px
    y = unit1.y + u * py

    dx = x - unit3.x
    dy = y - unit3.y

    dist = sqrt(dx*dx + dy*dy)
    #print dist

    if dist > 2.5 * unit3.radius:
        return True
    else:
        return False




class Strategy:
    def __init__(self, me, world, game):
        #print "================ " + str(world.tick)

        self.me = me
        self.world = world
        self.game = game

        self.move_turn = None
        self.move_speed_up = None
        self.move_action = None
        self.move_pass_angle = None
        self.move_pass_power = None

        speed = sqrt(self.me.speed_x*self.me.speed_x+self.me.speed_y*self.me.speed_y)
        if self.me.speed_y > 0.0 and self.me.angle > 0.0:
            self.speed = speed
        elif self.me.speed_y > 0.0 and self.me.angle < 0.0:
            self.speed = -speed
        elif self.me.speed_y < 0.0 and self.me.angle > 0.0:
            self.speed = -speed
        elif self.me.speed_y < 0.0 and self.me.angle < 0.0:
            self.speed = speed
        elif self.me.speed_x > 0.0 and -pi/2.0 < self.me.angle < pi/2.0:
            self.speed = speed
        else:
            self.speed = -speed

        self.player = self.world.get_my_player()
        self.opponentPlayer = self.world.get_opponent_player()


        self.myUnits = [hockeyist
                         for hockeyist in self.world.hockeyists
                         if hockeyist.teammate
                            and hockeyist.id != self.me.id
                            and hockeyist.type != HockeyistType.GOALIE
                            and hockeyist.state != HockeyistState.RESTING
                         ]
        self.myUnits.sort(key=lambda x:self.me.get_distance_to_unit(x))

        goalies = [hockeyist
                         for hockeyist in self.world.hockeyists
                         if hockeyist.teammate
                            and hockeyist.type == HockeyistType.GOALIE
                        ]
        if goalies:
            self.goalie = goalies[0]
        else:
            self.goalie = None


        self.opponentUnits = [hockeyist
                         for hockeyist in self.world.hockeyists
                         if not hockeyist.teammate
                            and hockeyist.type != HockeyistType.GOALIE
                            and hockeyist.state != HockeyistState.RESTING
                         ]
        self.opponentUnits.sort(key=lambda x:self.me.get_distance_to_unit(x))

        self.rink_center_x = 0.5 * (self.game.rink_left + self.game.rink_right)
        self.rink_center_y = 0.5 * (self.game.rink_top  + self.game.rink_bottom)

        if self.player.net_front < self.rink_center_x:
            self.position = "left"
        else:
            self.position = "right"


        self.defendCircle = Unit(9998, 1.0, 1.0*self.game.goal_net_height,
                                 self.player.net_front, self.rink_center_y,
                                 0.0, 0.0, 0.0, 0.0)




    def getStrategy(self):
        if self.world.puck.owner_hockeyist_id == self.me.id:
            if self.tryPass():
                return True
            else:
                self.setStrategyAttackNet()
                return True

        elif self.me.state == HockeyistState.SWINGING:
            self.move_action = ActionType.CANCEL_STRIKE
            return True

        elif self.world.puck.owner_player_id == self.me.player_id:
            self.setStrategyDefendNet()
            return True


        elif abs(self.me.x - self.player.net_front) < abs(self.myUnits[0].x - self.player.net_front):
            self.setStrategyDefendNet()
            return True

        else:
            self.setStrategyTakePuck()
            return True


    def tryPass(self):
        unit = self.myUnits[-1]
        dist0 = sum([self.me.get_distance_to_unit(opponentUnit) for opponentUnit in self.opponentUnits])
        dist1 = sum([   unit.get_distance_to_unit(opponentUnit) for opponentUnit in self.opponentUnits])

        puck_can_pass = True
        for opponentUnit in self.opponentUnits:
            puck_can_pass = puck_can_pass and canPass(self.me, unit, opponentUnit)


        if ( #dist0 < dist1
             #and
             abs(self.me.x - self.opponentPlayer.net_front) - abs(unit.x - self.opponentPlayer.net_front) > self.game.world_width/5.0
             and
             puck_can_pass
            ):

            angle = self.me.get_angle_to_unit(unit)

            if -pi/3.0 < angle < pi/3.0:
                self.move_pass_angle = angle
                self.move_pass_power = 0.8
                self.move_action = ActionType.PASS
                print "pass"
            else:
                self.move_turn = angle


            return True

        else:
            return False


    def probTakePuck(self):
        puck = self.world.puck
        puck_speed = sqrt(puck.speed_x*puck.speed_x+puck.speed_y*puck.speed_y)
        return 60.0 + max(self.me.dexterity, self.me.agility) - puck_speed * 5.0


    def setStrategyDefendNet(self):
        if self.probTakePuck() < 100 and self.tryStrikePuck():
            return True

        # if puck is close - let's catch it!
        if (self.me.get_distance_to_unit(self.world.puck) < #2.0*self.game.stick_length
                0.4*self.me.get_distance_to_unit(self.opponentUnits[0])
            and
            self.me.get_distance_to_unit(self.defendCircle) < self.defendCircle.radius
            and
            self.world.puck.owner_player_id != self.me.player_id
            ):
            self.setStrategyTakePuck()
            return True

        if (self.me.get_distance_to_unit(self.world.puck) < 5.0*self.me.radius
            and
            self.world.puck.owner_player_id != self.me.player_id
            ):
            self.setStrategyTakePuck()
            return True


        # The best place to defend net
        # if not(self.goalie):
        #     skateY = self.rink_center_y
        # elif self.goalie.y < self.rink_center_y:
        #     skateY = self.goalie.y + 0.5*(self.player.net_bottom - self.goalie.y)
        # else:
        #     skateY = self.goalie.y - 0.5*(self.goalie.y - self.player.net_top)

        skateY = self.rink_center_y

        if self.position == "left":
            skateX = self.player.net_front + 3.1*self.me.radius
        else:
            skateX = self.player.net_front - 3.1*self.me.radius


        # To stand or to move
        if self.me.get_distance_to(skateX, skateY) < 1.0*self.me.radius:
            angle = self.me.get_angle_to_unit(self.world.puck)
            self.move_turn = angle
        else:
            self.trySkate(skateX, skateY, True)

        return True


    def tryStrikePuck(self):
        unit = self.world.puck

        if (self.me.get_distance_to_unit(unit) < self.game.stick_length
            and
            abs(self.me.get_angle_to_unit(unit)) < 0.5 * self.game.stick_sector
            ):
            self.move_action = ActionType.STRIKE
            #print "strike puck"
            return True
        else:
            return False


    def tryStrikeOpponent(self):
        unit = self.opponentUnits[0]

        if (self.me.get_distance_to_unit(unit) < self.game.stick_length
            and
            abs(self.me.get_angle_to_unit(unit)) < 0.5 * self.game.stick_sector
            and
            unit.state != HockeyistState.KNOCKED_DOWN
            ):
            self.move_action = ActionType.STRIKE
            #print "strike opponent"
            return True
        else:
            return False


    def setStrategyTakePuck(self):
        if self.tryStrikeOpponent():
            return True
        else:
            speed = self.speed

            if speed == 0.0:
                n_tick = 0
            else:
                n_tick = self.me.get_distance_to_unit(self.world.puck) / speed

            if n_tick > 40.0: n_tick = 40.0
            if n_tick < 7.0: n_tick = 0.0

            gotoX = self.world.puck.x + self.world.puck.speed_x * n_tick
            if gotoX < self.game.rink_left or gotoX > self.game.rink_right:
                gotoX = self.me.x

            gotoY = self.world.puck.y + self.world.puck.speed_y * n_tick
            if gotoY < self.game.rink_top or gotoY > self.game.rink_bottom:
                gotoY = self.me.y

            self.move_turn = self.me.get_angle_to(gotoX, gotoY)
            #self.move_speed_up = 1.0
            if abs(self.move_turn) < pi / 4.0:
                self.move_speed_up = self.me.get_distance_to(gotoX, gotoY) / 30.0 #- 15.0 / 30.0
            elif abs(self.move_turn) < pi / 2.0:
                self.move_speed_up = self.me.get_distance_to(gotoX, gotoY) / 50.0 - 50.0 / 50.0
            else:
                self.move_speed_up =  - self.me.get_distance_to(gotoX, gotoY) / 50.0 + 60.0 / 50.0

            if self.move_speed_up < - self.speed / self.game.hockeyist_speed_down_factor:
                self.move_speed_up = - self.speed / self.game.hockeyist_speed_down_factor

            self.move_action = ActionType.TAKE_PUCK

        return True


    def setStrategyAttackNet(self):

        if not(self.goalie): #self.world.tick > self.game.tick_count:
            min_strike_dist_x = 0.0
            max_strike_dist_x = self.game.world_width
            min_strike_dist_y = 0.0
            max_strike_dist_y = self.game.world_height
        else:
            min_strike_dist_x = 0.1 * self.game.world_width
            max_strike_dist_x = 0.4 * self.game.world_width
            min_strike_dist_y = 0.2 * self.game.world_height
            max_strike_dist_y = 0.4 * self.game.world_height


        # if the position is good or i am swinging >> let's strike!
        if (
            (min_strike_dist_x < abs(self.me.x - self.opponentPlayer.net_front) < max_strike_dist_x
             and
             min_strike_dist_y < abs(self.me.y - self.rink_center_y) < max_strike_dist_y
             )
            or self.me.state == HockeyistState.SWINGING
            ):
            strikeX = self.opponentPlayer.net_front
            if self.me.y < self.rink_center_y:
                strikeY = self.opponentPlayer.net_bottom - self.world.puck.radius
            else:
                strikeY = self.opponentPlayer.net_top + self.world.puck.radius
            self.tryStrike(strikeX, strikeY)
            return True


        if self.position == "right":
            if abs(self.me.x - self.opponentPlayer.net_front) < min_strike_dist_x:
                skateX = self.opponentPlayer.net_front + min_strike_dist_x + 0.5 * self.me.radius
            elif abs(self.me.x - self.opponentPlayer.net_front) > max_strike_dist_x:
                skateX = self.opponentPlayer.net_front + max_strike_dist_x - 0.5 * self.me.radius
            else:
                skateX = self.me.x
        else: #self.position == "left":
            if abs(self.me.x - self.opponentPlayer.net_front) < min_strike_dist_x:
                skateX = self.opponentPlayer.net_front - min_strike_dist_x - 0.5 * self.me.radius
            elif abs(self.me.x - self.opponentPlayer.net_front) > max_strike_dist_x:
                skateX = self.opponentPlayer.net_front - max_strike_dist_x + 0.5 * self.me.radius
            else:
                skateX = self.me.x


        if self.me.y < self.rink_center_y - max_strike_dist_y:
            skateY = self.rink_center_y - max_strike_dist_y + 0.5 * self.me.radius
        elif self.rink_center_y - min_strike_dist_y < self.me.y < self.rink_center_y:
            skateY = self.rink_center_y - min_strike_dist_y - 0.5 * self.me.radius
        elif self.rink_center_y < self.me.y < self.rink_center_y + min_strike_dist_y:
            skateY = self.rink_center_y + min_strike_dist_y + 0.5 * self.me.radius
        elif self.me.y > self.rink_center_y + max_strike_dist_y:
            skateY = self.rink_center_y + max_strike_dist_y - 0.5 * self.me.radius
        else:
            skateY = self.me.y

        self.trySkate(skateX, skateY)
        return True




    def tryStrike(self, strikeX, strikeY):
        STRIKE_ACCURACY = 1.0 * pi / 180.0

        angle = self.me.get_angle_to(strikeX, strikeY)

        self.move_turn = angle
        self.move_speed_up = 0

        if abs(angle) < STRIKE_ACCURACY:
            if (self.me.swing_ticks < self.game.max_effective_swing_ticks
                  and
                  self.me.get_distance_to_unit(self.opponentUnits[0]) > 3.0*self.me.radius
                  #and
                  #self.me.state != HockeyistState.SWINGING
                  ):
                print "swing: " + str(self.me.swing_ticks)
                self.move_action = ActionType.SWING

                return True

        if (self.me.state == HockeyistState.SWINGING or abs(angle) < STRIKE_ACCURACY):
            print "strike puck: " + str(self.me.swing_ticks)
            self.move_action = ActionType.STRIKE

            return True


    def trySkate(self, skateX, skateY, zeroSpeed=False):
        if self.world.puck.owner_hockeyist_id == self.me.id:
            # i have a puck
            dangerUnits = [opponentUnit
                           for opponentUnit in self.opponentUnits
                           if self.me.get_distance_to_unit(opponentUnit) < 3.0*self.me.radius
                              and abs(self.me.get_angle_to_unit(opponentUnit)) < pi/3.0 ]

            dangerAngles = [self.me.get_angle_to_unit(dangerUnit)
                            for dangerUnit in dangerUnits
                            if abs(self.me.get_angle_to_unit(dangerUnit)) < pi/3.0 ]

            angle = self.me.get_angle_to(skateX, skateY)


            if dangerAngles:
                res1 = sum([deltaAngles(0.0, dangerAngle) for dangerAngle in dangerAngles])
                res2 = sum([deltaAngles(-self.game.hockeyist_turn_angle_factor, dangerAngle) for dangerAngle in dangerAngles])
                res3 = sum([deltaAngles(+self.game.hockeyist_turn_angle_factor, dangerAngle) for dangerAngle in dangerAngles])
                if res2 > res1 and res2 > res3 and angle < 0.0:
                    bestAngle = angle
                elif res3 > res1 and res3 > res2 and angle > 0.0:
                    bestAngle = angle
                else:
                    bestAngle = 0.0
            else:
                bestAngle = angle


            self.move_turn = bestAngle
            self.move_speed_up = 1.0
            self.move_action = None
            return True

        elif self.tryStrikeOpponent():
            return True

        else:
            # i don't have a puck

            angle = self.me.get_angle_to(skateX, skateY)
            dist = self.me.get_distance_to(skateX, skateY)

            #if dist < 10.0*self.me.radius and abs(angle) > pi/2:
            if abs(angle) > pi/2.0:
                # going back
                if angle > 0.0:
                    self.move_turn = angle - pi
                else:
                    self.move_turn = angle + pi

                if self.speed >= 0.0:
                    self.move_speed_up = -1.0
                elif zeroSpeed and dist/self.speed > self.speed / self.game.hockeyist_speed_up_factor:
                    self.move_speed_up = self.speed / self.game.hockeyist_speed_up_factor
                else:
                    self.move_speed_up = -1.0 # TODO

            else:
                # going front

                self.move_turn = angle

                if self.speed <= 0.0:
                    self.move_speed_up = 1.0
                elif zeroSpeed and dist/self.speed < self.speed / self.game.hockeyist_speed_down_factor:
                    self.move_speed_up = - self.speed / self.game.hockeyist_speed_down_factor
                else:
                    self.move_speed_up = 1.0 # TODO


            return True



class MyStrategy:

    def move(self, me, world, game, move):
        """
        @type me: Hockeyist
        @type world: World
        @type game: game
        @type move: Move
        """

        s = Strategy(me, world, game)
        s.getStrategy()
        if s.move_turn: move.turn = s.move_turn
        if s.move_speed_up: move.speed_up = s.move_speed_up
        if s.move_action: move.action = s.move_action
        if s.move_pass_angle: move.pass_angle = s.move_pass_angle
        if s.move_pass_power: move.pass_power = s.move_pass_power
        return True
