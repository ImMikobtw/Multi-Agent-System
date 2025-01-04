import pygame
import pygame_gui
from model import CrowdModel
from agent import EmptyAgent, ResearcherAgent, AnalystAgent, NotifierAgent, RecommenderAgent

pygame.init()

initial_width, initial_height = 800, 800  # окошко самой симуляции
chat_width, chat_height = 400, 600  # окошко чата

# мэйн окошко
screen = pygame.display.set_mode((initial_width, initial_height), pygame.RESIZABLE)
pygame.display.set_caption('Agent-Based Model')

# разделение окон
chat_screen = pygame.display.set_mode((chat_width, chat_height))
pygame.display.set_caption('Chat Log')

# цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
WHITE = (255, 255, 255)

# шаблончик для статы сторон
pygame.font.init()
font = pygame.font.SysFont('Arial', 20)

# гуи мессенджера
chat_manager = pygame_gui.UIManager((chat_width, chat_height))

chat_textbox = pygame_gui.elements.UITextBox(
    html_text="",
    relative_rect=pygame.Rect((0, 0), (chat_width, chat_height - 40)),
    manager=chat_manager,
)

chat_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((0, chat_height - 40), (chat_width, 40)),
    manager=chat_manager,
)


# функции рисовки агентов
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


# вижн статистики
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
def run_visualization(model):
    global screen, chat_screen, chat_manager
    clock = pygame.time.Clock()
    running = True
    width, height = initial_width, initial_height

    while running:
        time_delta = clock.tick(60) / 1000.0  # лимит в 60 фпс, у нас все равно у всех 60 герц

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
            elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_element == chat_input:
                new_message = event.text
                model.chat_log.append(new_message)
                chat_input.set_text("")

            chat_manager.process_events(event)

        screen.fill(BLACK)

        # апдейт и сами агенты
        for agent in model.schedule.agents:
            x, y = agent.pos
            x = int(x * (width / model.grid.width))
            y = int(y * (height / model.grid.height))
            draw_agent(agent, x, y)

        # вижн статистики
        draw_statistics(model)

        pygame.display.flip()

        chat_screen.fill(BLACK)
        chat_manager.update(time_delta)

        chat_text = "<br>".join(model.chat_log[-30:])  # вижн на последние 30 сообщ
        chat_textbox.html_text = chat_text
        chat_textbox.rebuild()

        chat_manager.draw_ui(chat_screen)
        pygame.display.update(chat_screen.get_rect())

        model.step()

    pygame.quit()


# юз
if __name__ == "__main__":
    model = CrowdModel()
    run_visualization(model)
    model.close_db_connections()
