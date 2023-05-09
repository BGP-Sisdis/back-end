import logging
import threading

from node import Order
from node_socket import UdpSocket


class City:

    def __init__(self, my_port: int, number_loyal_general: int, number_general: int ) -> None:
        self.my_port = my_port
        self.node_socket = UdpSocket(my_port)
        self.number_loyal_general = number_loyal_general
        self.number_general = number_general

    def start(self):
        self.add_log_info("Waiting for the generals' action...")

        status = []
        generals_action = []

        for i in range(self.number_loyal_general):
            message, address = self.node_socket.listen()
            general = message.split("~")[0]
            general = "Supreme General" if general == "supreme_general" else f"General {general.split('_')[1]}"
            action = int(message.split("~")[1].split("=")[1])
            status.append(action)
            if action == Order.RETREAT:
                action = "RETREAT"
                message = f"{general} {action} from us!"
                generals_action.append(f"{general}: {action}")
            else:
                action = "ATTACK"
                message = f"{general} {action} us!"
                generals_action.append(f"{general}: {action}")
            self.add_log_info(message)

        self.add_log_info("Concluding what happen...")
        logging.debug(f"status: {status}")
        retreat_counter = 0
        attack_counter = 0
        result_list_length = len(status)

        for i in status:
            if 1 == i:
                attack_counter += 1
            else:
                retreat_counter += 1

        general_consensus = "FAILED"
        number_traitor = self.number_general - self.number_loyal_general
        is_satified = True if self.number_general >= 3*number_traitor + 1 else False

        if result_list_length < 2:
            general_consensus = "ERROR_LESS_THAN_TWO_GENERALS"
        elif attack_counter == result_list_length and is_satified:
            general_consensus = "ATTACK"
        elif retreat_counter == result_list_length and is_satified:
            general_consensus = "RETREAT"

        self.add_log_info(f"Generals' action: {generals_action}")
        self.add_log_info(f"GENERAL CONSENSUS: {general_consensus}")

        return general_consensus

    def add_log_info(self, message):
        logging.info(f"City-{message}")


def thread_exception_handler(args):
    logging.error("Uncaught exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


def main(city_port: int, number_loyal_general: int, number_general: int):
    threading.excepthook = thread_exception_handler
    try:
        logging.debug(f"city_port: {city_port}")
        logging.info("City-City is running...")
        logging.info(f"City-Number of general: {number_general}")
        logging.info(f"City-Number of loyal general: {number_loyal_general}")
        city = City(my_port=city_port, number_loyal_general=number_loyal_general, number_general=number_general)
        return city.start()

    except Exception:
        logging.exception("Caught Error")
        raise