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
        self.add_log_info(1, "City is starting...")

        status, generals_action = self.listen_procedure()

        self.add_log_info(8, "Concluding result...")
        general_consensus = self.conclude_result(status)

        self.add_log_info(8, f"Generals' action: {generals_action}")
        self.add_log_info(8, f"Generals Consensus: {general_consensus}")

        self.add_log_info(9, "Done")

        return generals_action, general_consensus

    def add_log_info(self, step, message):
        logging.info(f"City-{step}-{message}")

    def listen_procedure(self):
        status = []
        generals_action = []

        for i in range(self.number_loyal_general):
            message, address = self.node_socket.listen()

            general = message.split("~")[0]
            general = "Supreme General" if general == "supreme_general" else f"General {general.split('_')[1]}"

            action = int(message.split("~")[1].split("=")[1])
            status.append(action)

            action = "RETREAT" if action == Order.RETREAT else "ATTACK"
            message = f"{general}: {action}"
            generals_action.append(f"{general}: {action}")

            self.add_log_info(7, message)

        return status, generals_action

    def conclude_result(self, status):
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

        if attack_counter == result_list_length and is_satified:
            general_consensus = "ATTACK"
        elif retreat_counter == result_list_length and is_satified:
            general_consensus = "RETREAT"
        elif (attack_counter == result_list_length or retreat_counter == result_list_length) and is_satified == False:
            general_consensus = "UNCERTAIN VALIDTY"

        return general_consensus


def thread_exception_handler(args):
    logging.error("Uncaught exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


def main(city_port: int, number_loyal_general: int, number_general: int):
    threading.excepthook = thread_exception_handler
    try:
        logging.debug(f"city_port: {city_port}")
        city = City(my_port=city_port, number_loyal_general=number_loyal_general, number_general=number_general)
        return city.start()

    except Exception:
        logging.exception("Caught Error")
        raise