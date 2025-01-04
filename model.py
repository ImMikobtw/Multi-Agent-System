from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import EmptyAgent, ResearcherAgent, AnalystAgent, NotifierAgent, RecommenderAgent

class CrowdModel(Model):
    def __init__(self, width=20, height=20, N=100, chat_queue=None):
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.chat_queue = chat_queue
        self.chat_log = []  # атрибут чата

        # Create agents
        for i in range(N):
            agent = EmptyAgent(i, self)
            self.schedule.add(agent)
            self.grid.place_agent(agent, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))

        # Add other types of agents
        researcher = ResearcherAgent(N, self)
        self.schedule.add(researcher)
        self.grid.place_agent(researcher, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))

        for i in range(2):
            analyst = AnalystAgent(N + 1 + i, self)
            self.schedule.add(analyst)
            self.grid.place_agent(analyst, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))

        for i in range(2):
            notifier = NotifierAgent(N + 3 + i, self)
            self.schedule.add(notifier)
            self.grid.place_agent(notifier, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))

        recommender = RecommenderAgent(N + 5, self)
        self.schedule.add(recommender)
        self.grid.place_agent(recommender, (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)))

    def step(self):
        self.schedule.step()

    def chat_message(self, message):
        if self.chat_queue:
            self.chat_queue.put(message)
        self.chat_log.append(message)  # добавление сообщ на чат
