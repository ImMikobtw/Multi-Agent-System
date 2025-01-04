import pygame
import pygame_gui
from multiprocessing import Queue

pygame.init()

chat_width, chat_height = 400, 600
chat_screen = pygame.display.set_mode((chat_width, chat_height), pygame.RESIZABLE)
pygame.display.set_caption('Chat Log')

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

def run_chat(chat_queue):
    global chat_screen, chat_textbox, chat_input
    clock = pygame.time.Clock()
    running = True
    width, height = chat_width, chat_height

    while running:
        time_delta = clock.tick(60) / 1000.0  # лимит 60 фпс бейбики

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                chat_screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                chat_textbox.set_relative_position((0, 0))
                chat_textbox.set_dimensions((width, height - 40))
                chat_input.set_relative_position((0, height - 40))
                chat_input.set_dimensions((width, 40))

            chat_manager.process_events(event)

        chat_screen.fill((0, 0, 0))
        chat_manager.update(time_delta)

        while not chat_queue.empty():
            new_message = chat_queue.get()
            chat_textbox.html_text += f"<br>{new_message}"
            chat_textbox.rebuild()

        chat_manager.draw_ui(chat_screen)
        pygame.display.update(chat_screen.get_rect())

    pygame.quit()
