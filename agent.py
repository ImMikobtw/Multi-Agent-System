import sqlite3
from mesa import Agent
import math
import random
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
from utils import get_distance


class EmptyAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.knowledge = []
        self.speed = random.uniform(0.01, 0.1)
        self.pos = (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height))
        self.target_pos = self.pos
        self.blink_color = None
        self.blink_timer = 0
        self.side = None  # трекает сторону, типа за красных или зеленых
        self.connect_to_db()

    def connect_to_db(self):
        self.conn = sqlite3.connect('crowd_knowledge.db')
        self.cursor = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        self.close_db()

    def store_knowledge(self, source, content):
        self.cursor.execute('INSERT INTO knowledge (source, content) VALUES (?, ?)', (source, content))
        self.conn.commit()

    def step(self):
        if random.random() < self.speed:
            self.move()
        if self.blink_timer > 0:
            self.blink_timer -= 1
            if self.blink_timer == 0:
                self.blink_color = None

    def move(self):
        if self.pos == self.target_pos:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            self.target_pos = self.random.choice(possible_steps)

        self.pos = self.interpolate(self.pos, self.target_pos)

    def interpolate(self, start, end):
        x1, y1 = start
        x2, y2 = end
        new_x = x1 + (x2 - x1) * self.speed
        new_y = y1 + (y2 - y1) * self.speed
        if math.isclose(new_x, x2, abs_tol=0.1) and math.isclose(new_y, y2, abs_tol=0.1):
            return end
        return (new_x, new_y)

    def blink(self, color, side):
        self.blink_color = color
        self.blink_timer = 20  # блинк
        self.side = side  # апдейт стороны


class ResearcherAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.cooldown = 0
        self.speed = random.uniform(0.01, 0.1)
        self.connect_to_db()
        self.pos = (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height))
        self.target_pos = self.pos

    def connect_to_db(self):
        self.conn = sqlite3.connect('knowledge.db')
        self.cursor = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        self.close_db()

    def get_random_knowledge(self):
        self.cursor.execute('SELECT content FROM knowledge ORDER BY RANDOM() LIMIT 1')
        result = self.cursor.fetchone()
        return result[0] if result else None

    def step(self):
        if random.random() < self.speed:
            if self.cooldown == 0:
                self.speak()
                self.cooldown = 30  # кулдаун
            else:
                self.cooldown -= 1
            self.move()

    def move(self):
        if self.pos == self.target_pos:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            self.target_pos = self.random.choice(possible_steps)

        self.pos = self.interpolate(self.pos, self.target_pos)

    def speak(self):
        knowledge = self.get_random_knowledge()
        if knowledge:
            self.model.chat_message(f"Researcher: {knowledge}")
            for agent in self.model.schedule.agents:
                if isinstance(agent, EmptyAgent):
                    if get_distance(agent.pos, self.pos) < 3:
                        agent.blink('RED', 'Researcher')
                    agent.knowledge.append(knowledge)
                    agent.store_knowledge('Researcher', knowledge)
                elif isinstance(agent, AnalystAgent) or isinstance(agent, NotifierAgent):
                    agent.knowledge.append(knowledge)

    def interpolate(self, start, end):
        x1, y1 = start
        x2, y2 = end
        new_x = x1 + (x2 - x1) * self.speed
        new_y = y1 + (y2 - y1) * self.speed
        if math.isclose(new_x, x2, abs_tol=0.1) and math.isclose(new_y, y2, abs_tol=0.1):
            return end
        return (new_x, new_y)


class AnalystAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.knowledge = []
        self.speed = random.uniform(0.01, 0.1)
        self.classifier = KNeighborsClassifier(n_neighbors=3)
        self.data = []
        self.labels = []
        self.pos = (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height))
        self.target_pos = self.pos
        self.connect_to_db()

    def connect_to_db(self):
        self.conn = sqlite3.connect('analyst_knowledge.db')
        self.cursor = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        self.close_db()

    def store_knowledge(self, topic, interpretation):
        self.cursor.execute('INSERT INTO knowledge (topic, interpretation) VALUES (?, ?)', (topic, interpretation))
        self.conn.commit()

    def step(self):
        if random.random() < self.speed:
            if self.knowledge:
                self.analyze()
                self.share()
            self.move()

    def move(self):
        if self.pos == self.target_pos:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            self.target_pos = self.random.choice(possible_steps)

        self.pos = self.interpolate(self.pos, self.target_pos)

    def analyze(self):
        knowledge = self.knowledge.pop(0)
        state = np.random.rand(3)
        self.data.append(state)
        self.labels.append(knowledge)
        if len(self.data) > 5:  # треня после сбора 5 сэмплов
            self.classifier.fit(self.data, self.labels)
        if len(self.data) > 5 and self.classifier.predict([state])[0] == knowledge:
            interpretation = f"Analyzed and classified: {knowledge}"
        else:
            interpretation = f"Analyzed but misclassified: {knowledge}"
        self.store_knowledge(knowledge, interpretation)
        self.analysis = interpretation

    def share(self):
        for agent in self.model.schedule.agents:
            if isinstance(agent, NotifierAgent):
                agent.knowledge.append(self.analysis)

    def interpolate(self, start, end):
        x1, y1 = start
        x2, y2 = end
        new_x = x1 + (x2 - x1) * self.speed
        new_y = y1 + (y2 - y1) * self.speed
        if math.isclose(new_x, x2, abs_tol=0.1) and math.isclose(new_y, y2, abs_tol=0.1):
            return end
        return (new_x, new_y)


class NotifierAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.knowledge = []
        self.speed = random.uniform(0.01, 0.1)
        self.classifier = KNeighborsClassifier(n_neighbors=3)
        self.data = []
        self.labels = []
        self.pos = (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height))
        self.target_pos = self.pos
        self.connect_to_db()

    def connect_to_db(self):
        self.conn = sqlite3.connect('notifier_knowledge.db')
        self.cursor = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        self.close_db()

    def step(self):
        if random.random() < self.speed:
            if self.knowledge:
                self.notify()
            self.move()

    def move(self):
        if self.pos == self.target_pos:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            self.target_pos = self.random.choice(possible_steps)

        self.pos = self.interpolate(self.pos, self.target_pos)

    def notify(self):
        knowledge = self.knowledge.pop(0)
        state = np.random.rand(3)
        self.data.append(state)
        self.labels.append(knowledge)
        if len(self.data) > 5:  # Train after 5 samples
            self.classifier.fit(self.data, self.labels)
        if len(self.data) > 5 and self.classifier.predict([state])[0] == knowledge:
            notification = f"Notifier confirmed: {knowledge}"
        else:
            notification = f"Notifier misclassified: {knowledge}"
        self.model.chat_message(notification)
        for agent in self.model.schedule.agents:
            if isinstance(agent, EmptyAgent):
                if get_distance(agent.pos, self.pos) < 3:
                    agent.blink('GREEN', 'Notifier')
                agent.knowledge.append(notification)
                agent.store_knowledge('Notifier', notification)

    def interpolate(self, start, end):
        x1, y1 = start
        x2, y2 = end
        new_x = x1 + (x2 - x1) * self.speed
        new_y = y1 + (y2 - y1) * self.speed
        if math.isclose(new_x, x2, abs_tol=0.1) and math.isclose(new_y, y2, abs_tol=0.1):
            return end
        return (new_x, new_y)


class RecommenderAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.speed = random.uniform(0.01, 0.02)
        self.pos = (self.random.randrange(self.model.grid.width), self.random.randrange(self.model.grid.height))
        self.target_pos = self.pos
        self.classifier = KNeighborsClassifier(n_neighbors=3)
        self.data = []
        self.labels = []
        self.connect_to_db()

    def connect_to_db(self):
        self.conn = sqlite3.connect('recommender_knowledge.db')
        self.cursor = self.conn.cursor()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        self.close_db()

    def step(self):
        if random.random() < self.speed:
            self.train_or_recommend()
            self.move()

    def move(self):
        if self.pos == self.target_pos:
            possible_steps = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            self.target_pos = self.random.choice(possible_steps)

        self.pos = self.interpolate(self.pos, self.target_pos)

    def train_or_recommend(self):
        if len(self.data) > 5:  # такая же треня как и выше
            self.classifier.fit(self.data, self.labels)
            if random.random() < 0.1:  # 10% шанса на рек
                self.recommend()
        else:
            # сбор данных для трень
            state = np.random.rand(3)
            recommendation = random.choice([0, 1])  # 0 это не рек, 1 это рек
            self.data.append(state)
            self.labels.append(recommendation)

    def recommend(self):
        recommendation = "Recommending products based on recent discussions."
        self.model.chat_message(recommendation)

    def interpolate(self, start, end):
        x1, y1 = start
        x2, y2 = end
        new_x = x1 + (x2 - x1) * self.speed
        new_y = y1 + (y2 - y1) * self.speed
        if math.isclose(new_x, x2, abs_tol=0.1) and math.isclose(new_y, y2, abs_tol=0.1):
            return end
        return (new_x, new_y)
