#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

# Откуда и сколько траекторий берём
DRIVER_PATH = '/Users/zoldatoff/Downloads/driver/data/'
PLOT_EXT = '.eps'


class Trip(object):
    """
    This class:
     * reads trip data from csv file
    """

    def __init__(self, driver_num=1, trip_num=1):
        print 'Driver = ' + str(driver_num) + ', trip = ' + str(trip_num)

        self.driver_num = driver_num
        self.trip_num = trip_num
        self.driver_trip = str(int(driver_num)) + '_' + str(int(trip_num))

        self.get_data()
        self.set_flags()
        self.get_kpi()

        # self.plot_trip()
        # self.plot_data()
        # self.plot_rv()

        # print self.kpi
        # self.trip_data.to_csv(self.driver_trip + '_trip_data.csv', sep='\t')

    # =========================================================================
    def get_data(self):
        """
        Reads trip data (x, y) from csv file
        """
        trip_filename = str(self.trip_num) + '.csv'
        trip_path = DRIVER_PATH + '/' + str(self.driver_num) + '/'
        self.trip_data = pd.DataFrame.from_csv(
            trip_path + trip_filename, index_col=False)
        self.trip_data.columns = ['x', 'y']

        self.trip_data['trip_num'] = self.trip_num
        self.trip_data['t'] = self.trip_data.index
        self.trip_data['v'] = self.distance(self.trip_data, 'x', 'y')
        self.trip_data['a'] = self.trip_data.v.diff()
        self.trip_data['r'] = self.radius(self.trip_data, 'x', 'y')
        self.trip_data['ang'] = self.angle(self.trip_data, 'x', 'y')

        self.trip_data['v'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.v, np.nan)

        self.trip_data['r'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.r, np.nan)

        self.trip_data['ang'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.ang, np.nan)

        self.trip_data['a'] = np.where(
            (self.trip_data.a > -1) & (self.trip_data.a < 3),
            self.trip_data.a, np.nan)

    # =========================================================================
    @staticmethod
    def turn(trip_data, turn_direction):
        df = trip_data.copy()

        if turn_direction == 'left':
            s = 1
        elif turn_direction == 'right':
            s = -1
        else:
            s = 0

        n1 = 3
        df['temp'] = df.apply(
            lambda x: 1
            if x.r < 100 and x.v > 1 and s * x.ang > 0.05
            else 0,
            axis=1)

        df['flag1'] = pd.rolling_sum(df.temp, n1) \
            .apply(lambda x: 1 if x == n1 else 0) \
            .shift(-n1/2+1)

        n2 = 6
        df['temp'] = df.apply(
            lambda x: x.ang
            if x.r < 100 and x.v > 0.1
            else - s * np.inf,
            axis=1)

        df['flag2'] = pd.rolling_sum(df.temp, n2) \
            .apply(lambda x: 1 if s * x >= np.pi / 3.0 else 0) \
            .shift(-n2/2+1)

        return np.where(df.flag1 + df.flag2 > 0, 1, 0)

    # =========================================================================
    @staticmethod
    def accel_decel(trip_data, acc_dec):
        df = trip_data.copy()

        if acc_dec == 'acc':
            s = 1
        elif acc_dec == 'dec':
            s = -1
        else:
            s = 0

        n = 3
        df['temp'] = df.a.apply(lambda x: 1 if s * x > 0.01 else 0)

        df['flag'] = pd.rolling_sum(df.temp, n) \
            .apply(lambda x: 1 if x == n else 0) \
            .shift(-n/2+1)

        return df.flag

    # =========================================================================
    def set_flags(self):
        """
        Sets flags for special parts of trip
        """
        df = self.trip_data

        df['flag_accel'] = self.accel_decel(df, 'acc')
        df['flag_decel'] = self.accel_decel(df, 'dec')

        df['flag_turn_left'] = self.turn(df, 'left')
        df['flag_turn_right'] = self.turn(df, 'right')

        df['flag_calm'] = np.where(
            df['flag_accel'] + df['flag_decel']
            + df['flag_turn_left'] + df['flag_turn_right'] == 0, 1, 0)

        df['flag_turn'] = 0
        turn_points = set()
        dff = df[(df.flag_turn_right == 1) | (df.flag_turn_left == 1)]
        for k, row in dff.iterrows():
            i = k
            while True:
                i += 1
                if df.ix[i].flag_turn == 0 and (
                        df.ix[i].flag_accel == 1
                        or df.ix[i].flag_turn_left == 1
                        or df.ix[i].flag_turn_right == 1):
                    turn_points.add(i)
                else:
                    break

            i = k
            while True:
                i -= 1
                if df.ix[i].flag_turn == 0 and (
                        df.ix[i].flag_decel == 1
                        or df.ix[i].flag_turn_left == 1
                        or df.ix[i].flag_turn_right == 1):
                    turn_points.add(i)
                else:
                    break

        df.ix[df['t'].isin(turn_points), 'flag_turn'] = 1

    # =========================================================================
    def get_kpi(self):
        df = self.trip_data
        kpi = pd.Series(None)

        kpi['driver_trip'] = self.driver_trip
        kpi['driver_num'] = self.driver_num
        kpi['trip_num'] = self.trip_num

        # vR = наибольшая скорость вхождения в поворот с радиусом 15 м.
        df_turn = df[(df.flag_turn_left == 1) | (df.flag_turn_right == 1)]
        # kpi['vR'] = df_turn[df_turn.r <= 10].v.max()
        kpi['vR'] = self.decile(df_turn[df_turn.r <= 15], 'v')

        kpi['a'] = self.decile(df[df.flag_accel == 1], 'a')

        # accel = наибольшее ускорение после прохождения поворота
        # decel = наибольшее замедление перед прохождением поворота
        # kpi['accel'] = df[(df.flag_accel == 1) & (df.flag_turn == 1)].a.max()
        # kpi['decel'] = df[(df.flag_decel == 1) & (df.flag_turn == 1)].a.max()
        kpi['accel'] = self.decile(
            df[(df.flag_accel == 1) & (df.flag_turn == 1)], 'a')
        kpi['decel'] = self.decile(
            df[(df.flag_decel == 1) & (df.flag_turn == 1)], 'a')

        # calm = доля участков пути, на которых нет ускорений и поворотов
        # в общей длине пути (только там, где скорость больше 5 м/с)
        n1 = len(df[(df.flag_calm == 1) & (df.v > 5.0)])
        n2 = len(df[df.v > 5.0])
        if n2 > 0:
            kpi['calm'] = float(n1) / float(n2)
        else:
            kpi['calm'] = 0.5

        # nerv_a = количество кратковременных нажатий на педаль газа
        # nerv_ang = количество небольших поворотов руля
        kpi['nerv_a'] = abs(df.flag_calm.diff()).sum() / \
            float(len(df[df.flag_calm == 1]))
        kpi['nerv_ang'] = abs(df[df.flag_turn == 0].ang).sum() / \
            float(len(df[df.flag_turn == 0]))

        kpi['s'] = df.v.sum()

        # part = [1 for i in range(1, 21)] \
        #     + [2 for i in range(21, 41)] \
        #     + [3 for i in range(41, 61)] \
        #     + [4 for i in range(61, 81)] \
        #     + [5 for i in range(81, 100)] \
        #     + [5 for i in range(101, 200)]
        # kpi['n'] = part[self.trip_num]

        self.kpi = kpi

    # =========================================================================
    def plot_data(self):
        """
        Draws a plot of trip data
        """

        df = self.trip_data

        fig, axes = plt.subplots(2, 2)

        # Velocity
        ax = axes[0, 0]
        df.plot(x='t', y='v', ax=ax, ls='--', color='gray')

        dfp = df[df.flag_accel == 1]
        if not dfp.empty:
            df[df.flag_accel == 1].plot(x='t', y='v', ax=ax,
                                        ls='', marker='.', color='r')

        dfp = df[df.flag_decel == 1]
        if not dfp.empty:
            df[df.flag_decel == 1].plot(x='t', y='v', ax=ax,
                                        ls='', marker='.', color='g')

        ax.set_ylabel('Velocity')
        ax.legend(['', 'acceleration', 'deceleration'])
        ax.set_xlabel('time (s)')

        # Acceleration
        ax = axes[0, 1]
        df.plot(x='t', y='a', ax=ax, ls='--', color='gray')
        df[df.flag_accel == 1].plot(x='t', y='a', ax=ax,
                                    ls='', marker='.', color='r')
        df[df.flag_decel == 1].plot(x='t', y='a', ax=ax,
                                    ls='', marker='.', color='g')
        ax.set_ylabel('Acceleration')
        ax.legend(['', 'acceleration', 'deceleration'], loc='upper left')
        ax.set_xlabel('time (s)')
        ax.set_ylim([-3, 3])

        # Radius
        ax = axes[1, 0]
        # df.plot(x='t', y='r', ax=axes[1], ls='--', color='k')
        df[df.flag_turn_left == 1].plot(x='t', y='r', ax=ax,
                                        ls='', marker='.', color='r')
        df[df.flag_turn_right == 1].plot(x='t', y='r', ax=ax,
                                         ls='', marker='.', color='b')
        ax.set_ylabel('Radius')
        ax.legend(['left', 'right'], loc='upper right')
        ax.set_xlabel('time (s)')
        ax.set_ylim([0, 100])
        ax.set_xbound(lower=0.0, upper=df.t.max())

        # Angle
        ax = axes[1, 1]
        # df.plot(x='t', y='ang', ax=ax2, ls='--', color='k')
        df[df.flag_turn_left == 1].plot(x='t', y='ang', ax=ax,
                                        ls='', marker='.', color='r')
        df[df.flag_turn_right == 1].plot(x='t', y='ang', ax=ax,
                                         ls='', marker='.', color='b')
        ax.set_ylabel('Angle')
        ax.legend(['left', 'right'], loc='upper left')
        ax.set_xlabel('time (s)')
        ax.set_ylim([-0.5, 0.5])
        ax.set_xbound(lower=0.0, upper=df.t.max())

        fig.set_size_inches(15, 10)
        fig.savefig(self.driver_trip + '_data' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_trip(self):
        """
        Сторит 2 графика:
        * график поворотов / разгонов / торможений
        * график поворотов с примыкающими к ним разгонами и торможениями
        """
        df = self.trip_data

        # График, на котором выделены повороты и
        # участки разгона / торможения

        fig, axes = plt.subplots()

        df.plot(x='x', y='y', ax=axes, color='gray')

        if not df[df.flag_accel == 1].empty:
            df[df.flag_accel == 1].plot(x='x', y='y', ax=axes, color='orange',
                                        ls='', marker='.')

        if not df[df.flag_decel == 1].empty:
            df[df.flag_decel == 1].plot(x='x', y='y', ax=axes, color='green',
                                        ls='', marker='.')

        if not df[df.flag_turn_left == 1].empty:
            df[df.flag_turn_left == 1].plot(x='x', y='y', ax=axes, color='r',
                                            ls='', marker='o')

        if not df[df.flag_turn_right == 1].empty:
            df[df.flag_turn_right == 1].plot(x='x', y='y', ax=axes, color='b',
                                             ls='', marker='o')

        df[df.index <= 10].plot(x='x', y='y', ax=axes, color='r',
                                         ls='', marker='x')

        axes.legend(['trip', 'accel', 'decel', 'left', 'right', 'start'])

        axes.autoscale()
        plt.axis('equal')

        fig.savefig(self.driver_trip + '_trip' + PLOT_EXT)
        plt.close(fig)

        # График, на котором выделены повороты =
        # замедление до поворота + поворот + ускорение после поворота

        fig, axes = plt.subplots()

        df.plot(x='x', y='y', ax=axes, color='gray')

        if not df[df.flag_turn == 1].empty:
            df[df.flag_turn == 1].plot(x='x', y='y', ax=axes, color='red',
                                       ls='', marker='.')

        axes.autoscale()
        plt.axis('equal')
        axes.legend(['trip', 'turn'])

        fig.savefig(self.driver_trip + '_turn' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    def plot_rv(self):
        """
        Строит график зависимости скорости от радиуса поворота
        Для графика выбираются только точки, размеченные как повороты
        """

        df = self.trip_data
        fig, axes = plt.subplots()

        df[df.flag_turn_left == 1].plot(
            x='r', y='v', ax=axes, ls='', marker='.', color='g')
        df[df.flag_turn_right == 1].plot(
            x='r', y='v', ax=axes, ls='', marker='.', color='b')

        axes.set_xlim([0, 100])
        axes.legend().remove()
        # sns.despine()
        fig.savefig(self.driver_trip + '_rv' + PLOT_EXT)
        plt.close(fig)

    # =========================================================================
    @staticmethod
    def distance(df, x, y):
        return np.sqrt(df.x.diff()**2 + df.y.diff()**2)

    @staticmethod
    def radius(df, x, y):
        x1, y1 = df.x.shift(-1), df.y.shift(-1)
        x2, y2 = df.x, df.y
        x3, y3 = df.x.shift(1), df.y.shift(1)

        a = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        b = np.sqrt((x3-x2)**2 + (y3-y2)**2)
        c = np.sqrt((x3-x1)**2 + (y3-y1)**2)

        s = (a + b + c) / 2.0
        R = a * b * c / 4.0 / np.sqrt(s * (s - a) * (s - b) * (s - c))
        return R

    @staticmethod
    def angle(df, x, y):
        x1, y1 = df.x.shift(1), df.y.shift(1)
        x2, y2 = df.x, df.y
        x3, y3 = df.x.shift(-1), df.y.shift(-1)

        a1 = np.arctan2(y2-y1, x2-x1)
        a2 = np.arctan2(y3-y2, x3-x2)
        ang = a2 - a1

        ang = np.where(ang > np.pi, ang - 2.0*np.pi, ang)
        ang = np.where(ang < -np.pi, ang + 2.0*np.pi, ang)

        return ang

    @staticmethod
    def decile(df, x):
        """
        Returns minimum value in upper decile
        """
        d = df[x].sort(x, inplace=False).tolist()
        l = len(d)
        if l == 0:
            return 0
        else:
            return d[int(0.9*l)]
