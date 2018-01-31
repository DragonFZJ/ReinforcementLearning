import time
import numpy as np
import requests


# np.random.seed(2)


class MissileAI:
    def __init__(self):
        near, mid, long, moon, blood = 6, 4, 3, 1, 0
        self.init_state = np.array([near, mid, long, moon, blood] * 2)  # 双方仓库导弹数目、卫星个数，血量
        self.state = self.init_state
        self.state_dim = len(self.state)  # 状态的维度是10
        self.action_dim = 2  # 动作的维度是2
        self.hit = np.array([[[0.9, 0.7], [0.75, 0.5], [0, 0], [0, 0], [0, 0]],
                             [[0.8, 0.8], [0.7, 0.7], [0.7, 0.6], [0.7, 0.8], [1, 60]],
                             [[0.7, 0.9], [0.65, 0.8], [0.6, 0.75], [0.7, 0.7], [1, 100]]])
        # hit[i,j]第i个导弹命中j个地方的概率[命中率，损毁率]
        self.jump = int(self.state_dim / 2)  # 先后手区别的位数
        self.moon_help = 1.2

    def step(self, action):
        a1 = action[0]
        t1 = action[1] + self.jump
        a2 = action[2] + self.jump
        t2 = action[3]
        moon_add1 = self.moon_help if self.state[3] > 0 else 1
        moon_add2 = self.moon_help if self.state[8] > 0 else 1
        hit_rate1, damage_rate1 = self.hit[action[0], action[1]]
        hit_rate2, damage_rate2 = self.hit[action[2], action[3]]

        ran = [np.random.rand() for _ in range(4)]
        state1 = self.state.copy()
        state2 = self.state.copy()
        reward1, reward2 = 0, 0
        for missile, store, hit_rate, damage_rate, moon_add, state, reward, ran1, ran2 in zip(
                [a1, a2], [t1, t2], [hit_rate1, hit_rate2], [damage_rate1, damage_rate2]
                , [moon_add1, moon_add2], [state1, state2], [reward1, reward2], ran[:2], ran[2:]):
            if state[missile] > 0:  # 如果有弹
                state[missile] -= 1  # 减少弹
                if ran1 < hit_rate * moon_add:  # 命中
                    if store != 4 and store != 9:  # 命中非基地
                        if ran2 < damage_rate * moon_add:  # 损伤了
                            state[store] = 0
                    else:
                        state[store] -= damage_rate
            reward = 0
        self.state = np.array([min(x, y) for x, y in zip(state1, state2)])
        if sum(self.state[:3]) + sum(self.state[self.jump:8]) == 0:  # 判断是否结束
            done = True
        else:
            done = False
        return self.state, np.array([reward1, reward2]), done, None

    def reset(self):
        self.state = self.init_state
        return self.state

    def render(self):
        pass

    def robot_action(self, mode='rand_fool', first=True):
        # rand_fool
        # base_fool
        # rand_smart
        # base_smart
        if mode == 'rand_fool':  # 随机选动作，随机发炮
            return [np.random.randint(3), np.random.randint(5)]
        elif mode == 'base_fool':  # 随机选择动作，瞄准基地
            return [np.random.randint(3), 4]
        if first:
            mystate = self.state[:self.jump].copy()
            yourstate = self.state[self.jump:].copy()
        else:
            yourstate = self.state[:self.jump].copy()
            mystate = self.state[self.jump:].copy()  # 找出我方和敌方的不同状态
        if mode == 'rand_smart':  # 选择有弹的动作，随机打击对面非空仓库和基地
            missile = np.array([i for i in range(3) if mystate[i] != 0])
            if len(missile) == 0:
                return [0, 0]
            missile = np.random.choice(missile)
            store = [i for i in range(4) if yourstate[i] != 0]
            store.append(4)
            store = np.random.choice(store)
            return [missile, store]
        elif mode == 'base_smart':  # 选择有弹的动作，打击对面基地
            missile = np.array([i for i in range(3) if mystate[i] != 0])
            if len(missile) == 0:
                return [0, 0]
            missile = np.random.choice(missile)
            return [missile, 4]