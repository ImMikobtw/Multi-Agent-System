import pygame
from model import CrowdModel
from agent import EmptyAgent, ResearcherAgent, AnalystAgent, NotifierAgent, RecommenderAgent

pygame.init()

# определяет скрин и цвета
initial_width, initial_height = 800, 800
screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
pygame.display.set_caption('Agent-Based Model')

# цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)

# шаблон для статистики
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

# рисовка агентов
def draw_agent(agent, x, y):
    if isinstance(agent, ResearcherAgent):
        pygame.draw.rect(screen, RED, (x, y, 20, 20))
    elif isinstance(agent, AnalystAgent):
        pygame.draw.polygon(screen, BLUE, [(x, y), (x + 10, y + 20), (x - 10, y + 20)])
    elif isinstance(agent, NotifierAgent):
        pygame.draw.polygon(screen, GREEN, [(x, y), (x + 10, y + 5), (x + 5, y + 10), (x - 5, y + 10), (x - 10, y + 5)])
    elif isinstance(agent, RecommenderAgent):
        pygame.draw.polygon(screen, PURPLE, [(x, y), (x + 10, y), (x + 15, y + 10), (x + 10, y + 20), (x, y + 20), (x - 5, y + 10)])
    elif isinstance(agent, EmptyAgent):
        color = agent.blink_color if agent.blink_color else WHITE
        pygame.draw.circle(screen, color, (x, y), 10)


# статистика
def draw_statistics(model):
    researcher_side = 0
    notifier_side = 0
    for agent in model.schedule.agents:
        if isinstance(agent, EmptyAgent):
            if agent.side == 'Researcher':
                researcher_side += 1
            elif agent.side == 'Notifier':
                notifier_side += 1

    text_surface = font.render(f"Researcher Side: {researcher_side}", True, WHITE)
    screen.blit(text_surface, (10, 10))
    text_surface = font.render(f"Notifier Side: {notifier_side}", True, WHITE)
    screen.blit(text_surface, (10, 30))


# функция для запуска
def run_simulation(model, chat_queue):
    global screen
    clock = pygame.time.Clock()
    running = True
    width, height = initial_width, initial_height

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        screen.fill(BLACK)

        for agent in model.schedule.agents:
            x, y = agent.pos
            x = int(x * (width / model.grid.width))
            y = int(y * (height / model.grid.height))
            draw_agent(agent, x, y)

        # статистика
        draw_statistics(model)

        pygame.display.flip()
        model.step()

        # чекает есть ли новые сообщ
        while not model.chat_queue.empty():
            chat_queue.put(model.chat_queue.get())

        clock.tick(10)  # скорость движений

    pygame.quit()


# запуск
if __name__ == "__main__":
    from multiprocessing import Queue
    chat_queue = Queue()
    model = CrowdModel(chat_queue=chat_queue)
    run_simulation(model, chat_queue)
    model.close_db_connections()
