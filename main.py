from multiprocessing import Process, Queue
from main_simulation import run_simulation
from chat_window import run_chat
from model import CrowdModel

if __name__ == "__main__":
    chat_queue = Queue()

    chat_process = Process(target=run_chat, args=(chat_queue,))
    chat_process.start()

    model = CrowdModel(chat_queue=chat_queue)
    run_simulation(model, chat_queue)

    chat_process.join()
