from math import *

from model.ActionType import ActionType
from model.Game import Game
from model.Hockeyist import Hockeyist
from model.Move import Move
from model.World import World

from model.HockeyistState import HockeyistState
from model.HockeyistType import HockeyistType

from model.Unit import Unit

def normAngle(angle):
    ret = (angle + 20.0*pi) % (2.0*pi)
    if ret <= pi:
        return ret
    else:
        return ret - 2.0*pi


def dist2segment(unit1, unit2, unit3): # unit3 is the point
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

    return sqrt(dx*dx + dy*dy)




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

        self.angle = self.me.angle

        speed = sqrt(self.me.speed_x*self.me.speed_x+self.me.speed_y*self.me.speed_y)
        if self.me.speed_y > 0.0 and self.angle > 0.0:
            self.speed = speed
        elif self.me.speed_y > 0.0 and self.angle < 0.0:
            self.speed = -speed
        elif self.me.speed_y < 0.0 and self.angle > 0.0:
            self.speed = -speed
        elif self.me.speed_y < 0.0 and self.angle < 0.0:
            self.speed = speed
        elif self.me.speed_x > 0.0 and -pi/2.0 < self.angle < pi/2.0:
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


        self.defendCircle = Unit(9998, 1.0, 1.5*self.game.stick_length,
                                 self.player.net_front, self.rink_center_y,
                                 0.0, 0.0, 0.0, 0.0)

        
        self.attackAngle = pi/2.0 - pi/6.0

        if self.goalie:
            self.attackCircle = Unit(9998, 1.0, 0.4 * self.game.world_height,
                                 self.opponentPlayer.net_front, self.rink_center_y,
                                 0.0, 0.0, 0.0, 0.0)    
            self.attackPassDistance = 0.6 * self.game.goal_net_height
        else:
            self.attackCircle = Unit(9998, 1.0, self.game.world_width,
                                 self.opponentPlayer.net_front, self.rink_center_y,
                                 0.0, 0.0, 0.0, 0.0)
            self.attackPassDistance = self.game.world_width




    def getStrategy(self):
        if self.world.puck.owner_hockeyist_id == self.me.id:
            # if self.tryPass('Forward'):
            #     return True
            # else:
            self.setStrategyAttackGate()
            return True

        elif self.me.state == HockeyistState.SWINGING:
            self.move_action = ActionType.CANCEL_STRIKE
            return True

        elif self.world.puck.owner_player_id == self.me.player_id:
            self.setStrategyDefendGate()
            return True


        elif abs(self.me.x - self.player.net_front) < abs(self.myUnits[0].x - self.player.net_front):
            self.setStrategyDefendGate()
            return True

        else:
            self.setStrategyTakePuck()
            return True


    def calcAcceleration(self, skateX, skateY):

        Tmin = 10000
        a_min = 1.0

        if self.me.get_distance_to(skateX, skateY) > self.game.world_width / 4.0:
            self.move_turn = self.me.get_angle_to(skateX, skateY)
            self.move_speed_up = 1.0
            return True

        if abs(self.me.get_angle_to(skateX, skateY)) <= pi/2.0:
            direction = 'forward'
        else:
            direction = 'back'

        for i in range(10):
            (x, y) = (self.me.x, self.me.y)
            v = self.speed
            alpha = self.angle
            a0 = 1.0 - i/10.0
            T = Tmin

            if direction == 'forward' and a0 < 0.0:
                break
            # if direction == 'back' and self.me.get_distance_to(skateX, skateY) > 100.0 and a < 0.0:
            #     break

            for j in range(100):
                aj = a0 - j*0.001
                unit = Unit(999 + i*100 + j, 0.0, 0.0, x, y, 0.0, 0.0, alpha, 0.0)
                if (x < self.game.rink_left or x > self.game.rink_right
                    or
                    y < self.game.rink_top or y > self.game.rink_bottom):
                    break

                if unit.get_distance_to(skateX, skateY) < 1.0:
                    T = j
                    break

                if aj > 0.0:
                    v += aj * self.game.hockeyist_speed_up_factor
                else:
                    v += aj * self.game.hockeyist_speed_down_factor

                v = 0.95*v  # friction

                dalpha = unit.get_angle_to(skateX, skateY)
                if v < 0.0 and dalpha < 0.0: 
                    dalpha = dalpha + pi
                elif v < 0.0 and dalpha > 0.0: 
                    dalpha = dalpha - pi

                dalpha = copysign( min(abs(dalpha), self.game.hockeyist_turn_angle_factor), dalpha )
            
                alpha = normAngle(alpha + dalpha)
                (x, y) = (x + v * cos(alpha), y + v * sin(alpha))

            if T < Tmin:
                Tmin = T
                a_min = a0

        alpha = self.me.get_angle_to(skateX, skateY)
        if T == 10000:
            #print self.me.x, self.me.y, skateX, skateY, self.angle, direction, self.speed
            self.move_turn = alpha
            self.move_speed_up = 1.0
        elif direction == 'back' and a_min < 0.0 and alpha < 0.0:
            self.move_turn = alpha + pi
            self.move_speed_up = a_min
        elif direction == 'back' and a_min < 0.0 and alpha > 0.0:
            self.move_turn = alpha - pi
            self.move_speed_up = a_min
        else:
            self.move_turn = alpha
            self.move_speed_up = a_min

        return True



    def tryPass(self, method='Forward', unit = None):
        if not unit:
            unit = self.myUnits[-1]


        puck_can_pass = True
        for opponentUnit in self.opponentUnits:
            if dist2segment(self.me, unit, opponentUnit) < self.game.stick_length:
                puck_can_pass = False


        if ((method == 'Forward'
             and
             abs(self.me.x - self.opponentPlayer.net_front) - abs(unit.x - self.opponentPlayer.net_front) > self.game.world_width/5.0
             and
             puck_can_pass
             and
             abs(unit.get_angle_to_unit(self.me)) < pi / 3.0
            )
            #or (method == 'Backward' and puck_can_pass)
            or (method == 'Strike')
            ):

            angle = self.me.get_angle_to_unit(unit)

            if abs(angle) < pi/3.0:
                self.move_pass_angle = angle

                if method == 'Forward':
                    self.move_pass_power = 0.8
                #elif method == 'Backward':
                #    self.move_pass_power = 0.6
                elif method == 'Strike':
                    self.move_pass_power = 1.0

                self.move_action = ActionType.PASS
                #print "pass " + method
                return True
            else:
                #self.move_turn = angle
                return False

        else:
            return False



    def probTakePuck(self):
        puck = self.world.puck
        puck_speed = sqrt(puck.speed_x*puck.speed_x+puck.speed_y*puck.speed_y)
        return 60.0 + max(self.me.dexterity, self.me.agility) - puck_speed * 5.0



    def setStrategyDefendGate(self):
        #print "====== defence ======"
        if self.probTakePuck() < 100 and self.tryStrikePuck():
            #print "defence: tryStrikePuck"
            return True


        distMe = self.me.get_distance_to_unit(self.world.puck)
        distOpponent = min([unit.get_distance_to_unit(self.world.puck) for unit in self.opponentUnits])

        # if puck is close - let's catch it!
        if (distMe < 0.5 * distOpponent
            and
            #self.me.get_distance_to_unit(self.defendCircle) < self.defendCircle.radius
            #and
            self.world.puck.owner_player_id != self.me.player_id
            and
            self.setStrategyTakePuck()
            ):
            #print "defence: setStrategyTakePuck"
            return True


        skateY = self.rink_center_y

        if self.position == "left":
            skateX = self.player.net_front + 3.1*self.me.radius            
        else:
            skateX = self.player.net_front - 3.1*self.me.radius


        # To stand or to move
        if self.me.get_distance_to(skateX, skateY) < 1.0*self.me.radius:
            self.move_turn = self.me.get_angle_to_unit(self.world.puck)
            #print "defence: turn to puck"
        else:
            #print "defence: skate"
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
        if self.world.puck.owner_player_id == self.me.player_id:
            return False
        elif self.me.get_distance_to_unit(self.world.puck) < self.game.stick_length:
            self.move_turn = self.me.get_angle_to_unit(self.world.puck)
            self.move_speed_up = 1.0
            self.move_action = ActionType.TAKE_PUCK
        elif abs(self.player.net_front - self.me.x) > self.game.world_width / 2.0 and self.tryStrikeOpponent():
            return True
        else:
            if self.speed == 0.0:
                n_tick = 1.0
            elif self.me.get_distance_to_unit(self.world.puck) < self.game.stick_length:
                n_tick = 1.0
            else:
                n_tick = self.me.get_distance_to_unit(self.world.puck) / self.speed

            if n_tick > 40.0: n_tick = 40.0
            if n_tick < 7.0: n_tick = 1.0

            gotoX = self.world.puck.x + self.world.puck.speed_x * n_tick

            if gotoX < self.game.rink_left or gotoX > self.game.rink_right:
                gotoX = self.me.x

            gotoY = self.world.puck.y + self.world.puck.speed_y * n_tick

            if gotoY < self.game.rink_top or gotoY > self.game.rink_bottom:
                gotoY = self.me.y

            self.calcAcceleration(gotoX, gotoY)

            self.move_action = ActionType.TAKE_PUCK

            return True


    def setStrategyAttackGate(self):

        # if the position is good or i am swinging >> let's strike!
        if (
            (self.me.get_distance_to_unit(self.attackCircle) < self.attackCircle.radius
            and abs(self.me.get_angle_to_unit(self.attackCircle)) < self.attackAngle)
            or self.me.state == HockeyistState.SWINGING
            ):
            strikeX = self.opponentPlayer.net_front
            if self.me.y < self.rink_center_y:
                strikeY1 = self.opponentPlayer.net_bottom - self.world.puck.radius
                strikeY2 = self.opponentPlayer.net_bottom - 2.0*self.world.puck.radius
            else:
                strikeY1 = self.opponentPlayer.net_top + self.world.puck.radius
                strikeY2 = self.opponentPlayer.net_top + 2.0*self.world.puck.radius

            unit1 = Unit(890, 0.0, 0.0, strikeX, strikeY1, 0.0, 0.0, 0.0, 0.0)
            unit2 = Unit(891, 0.0, 0.0, strikeX, strikeY2, 0.0, 0.0, 0.0, 0.0)
            dist1 =min( [dist2segment(self.me, unit1, opponent) for opponent in self.opponentUnits] )
            dist2 =min( [dist2segment(self.me, unit2, opponent) for opponent in self.opponentUnits] )

            if dist1 < dist2:
                #print "trystrike2 " + str(dist1) + " " + str(dist2)
                self.tryStrike(strikeX, strikeY2)
            else:
                #print "trystrike1 " + str(dist1) + " " + str(dist2)
                self.tryStrike(strikeX, strikeY1)
            
            return True

        if abs(self.me.x - self.opponentPlayer.net_front) > self.game.world_width / 2.0:
            if self.me.y < self.rink_center_y:
                self.trySkate(self.attackCircle.x, 0.2 * self.game.world_height) 
            else:
                self.trySkate(self.attackCircle.x, 0.8* self.game.world_height) 
        else:
            if self.me.y < self.rink_center_y:
                self.trySkate(self.attackCircle.x, self.opponentPlayer.net_bottom - self.world.puck.radius)
            else:
                self.trySkate(self.attackCircle.x, self.opponentPlayer.net_top + self.world.puck.radius)
        return True




    def tryStrike(self, strikeX, strikeY):
        PASS_ACCURACY = pi / 3.0
        STRIKE_ACCURACY = 1.0 * pi / 180.0

        angle = self.me.get_angle_to(strikeX, strikeY)

        self.move_turn = angle
        self.move_speed_up = 1.0

        danger = False
        for opponentUnit in self.opponentUnits:
            if (opponentUnit.get_distance_to_unit(self.me) < 1.1 * self.game.stick_length
                and
                abs(opponentUnit.get_angle_to_unit(self.me)) < 0.6 * self.game.stick_sector
                and
                opponentUnit.state != HockeyistState.KNOCKED_DOWN
                ):
                danger = True

            if (opponentUnit.get_distance_to_unit(self.world.puck) < 1.1 * self.game.stick_length
                and
                abs(opponentUnit.get_angle_to_unit(self.world.puck)) < 0.7 * self.game.stick_sector
                and
                opponentUnit.state != HockeyistState.KNOCKED_DOWN
                ):
                danger = True


        if abs(angle) < STRIKE_ACCURACY and self.me.get_distance_to_unit(self.attackCircle) > self.attackPassDistance:
            if self.me.swing_ticks < self.game.max_effective_swing_ticks and not danger:
                #print "swing: " + str(self.me.swing_ticks)
                self.move_action = ActionType.SWING

                return True

        if (self.me.state == HockeyistState.SWINGING or abs(angle) < STRIKE_ACCURACY):
            #print "strike puck: " + str(self.me.swing_ticks)
            self.move_action = ActionType.STRIKE

            return True

        if (abs(angle) < PASS_ACCURACY 
            #and danger
            and self.me.state != HockeyistState.SWINGING
            and self.me.get_distance_to_unit(self.attackCircle) < self.attackPassDistance
            ):
            print "strike pass"
            unit = Unit(997, 0.0, 0.0, strikeX, strikeY, 0.0, 0.0, 0.0, 0.0)
            self.tryPass('Strike', unit)
            return True

        return False



    def trySkate(self, skateX, skateY, zeroSpeed=False):
        if self.world.puck.owner_hockeyist_id == self.me.id:
            #print "trySkate: calcAcceleration1"
            self.calcAcceleration(skateX, skateY)

            #if self.speed < 0.1:
            test = Unit(661, 0.0, 0.0, 
                        self.me.x + 6.0 * self.me.radius * cos(self.me.angle + self.move_turn), 
                        self.me.y + 6.0 * self.me.radius * sin(self.me.angle + self.move_turn), 
                        0.0, 0.0, 0.0, 0.0)

            dangerUnits = [unit for unit in self.opponentUnits if unit.get_angle_to_unit(self.me) < pi / 3.0]
            if dangerUnits:
                dangerUnits.sort(key=lambda x: dist2segment(self.me, test, x))
                dist = dist2segment(self.me, test, dangerUnits[0])

                if dist < 10.0 and self.me.get_angle_to_unit(dangerUnits[0]) < 0.0:
                    self.move_turn = self.game.hockeyist_turn_angle_factor
                    print "me+puck: angle +"
                elif dist < 10.0:
                    self.move_turn = - self.game.hockeyist_turn_angle_factor
                    print "me+puck: angle -"

            return True

        elif self.tryStrikeOpponent():
            #print "trySkate: tryStrikeOpponent"
            return True

        elif zeroSpeed:
            # i don't have a puck
            # i don't have a puck

            angle = self.me.get_angle_to(skateX, skateY)
            dist = self.me.get_distance_to(skateX, skateY)

            #if dist < 10.0*self.me.radius and abs(angle) > pi/2:
            if abs(angle) > pi/2.0 and dist < self.game.world_width / 2.0:
                # going back
                if angle > 0.0:
                    self.move_turn = angle - pi
                else:
                    self.move_turn = angle + pi

                if self.speed >= 0.0:
                    self.move_speed_up = -1.0
                elif dist/self.speed > self.speed / self.game.hockeyist_speed_up_factor:
                    self.move_speed_up = self.speed / self.game.hockeyist_speed_up_factor
                else:
                    self.move_speed_up = -1.0

            else:
                # going front

                self.move_turn = angle

                if self.speed <= 0.0:
                    self.move_speed_up = 1.0
                elif dist/self.speed < self.speed / self.game.hockeyist_speed_down_factor:
                    self.move_speed_up = - self.speed / self.game.hockeyist_speed_down_factor
                else:
                    self.move_speed_up = 1.0

            #print "zeroSpeed: " + str(self.move_turn) + " " + str(self.move_speed_up)
            return True

        else:
            #print "trySkate: calcAcceleration2"
            self.calcAcceleration(skateX, skateY)
            
            if self.speed < 0.1:
                test = Unit(661, 0.0, 0.0, 
                            self.me.x + 2.0 * self.me.radius * cos(self.me.angle + self.move_turn), 
                            self.me.y + 2.0 * self.me.radius * sin(self.me.angle + self.move_turn), 
                            0.0, 0.0, 0.0, 0.0)
                
                dist = min([unit.get_distance_to_unit(test) for unit in self.opponentUnits])
                if test.x < 0 or test.x > self.game.world_width or test.y < 0 or test.y > self.game.world_height:
                    dist = 0.0

                if dist < 2.0 and self.me.get_angle_to_unit(self.attackCircle) > 0.0:
                    self.move_turn += self.game.hockeyist_turn_angle_factor
                    print "me-puck: angle +"
                elif dist < 2.0:
                    self.move_turn -= self.game.hockeyist_turn_angle_factor
                    print "me-puck: angle -"

            return True



class MyStrategy:

    def move(self, me, world, game, move):
        """
        @type me: Hockeyist
        @type world: World
        @type game: game
        @type move: Move
        """

        if world.tick == 0:
            print "me.radius = " + str(me.radius)
            print "game.stick_length = " + str(game.stick_length)
            print "world.puck.radius = " + str(world.puck.radius)
            print "game.hockeyist_speed_down_factor = " + str(game.hockeyist_speed_down_factor)
            print "game.hockeyist_speed_up_factor = " + str(game.hockeyist_speed_up_factor)
            print "game.hockeyist_turn_angle_factor = " + str(game.hockeyist_turn_angle_factor)
            print "game.world_width = " + str(game.world_width)
            print "game.world_height = " + str(game.world_height)
            print "game.goal_net_height = " + str(game.goal_net_height)

        s = Strategy(me, world, game)
        s.getStrategy()
        if s.move_turn: move.turn = s.move_turn
        if s.move_speed_up: move.speed_up = s.move_speed_up
        if s.move_action: move.action = s.move_action
        if s.move_pass_angle: move.pass_angle = s.move_pass_angle
        if s.move_pass_power: move.pass_power = s.move_pass_power

        #print "move_turn = " + str(s.move_turn)
        #print "speed_up = " + str(move.speed_up)
        return True
