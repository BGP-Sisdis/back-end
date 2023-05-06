import logging
import pprint
import threading
import time
import random

from pprint import pformat

from node_socket import UdpSocket


class Order:
    RETREAT = 0
    ATTACK = 1


class General:

    def __init__(self, my_id: int, is_traitor: bool, my_port: int, ports: list, 
                 node_socket: UdpSocket, city_port: int, number_of_general: int):
        self.my_id = my_id
        self.city_port = city_port
        self.node_socket = node_socket
        self.my_port = my_port
        self.is_traitor = is_traitor
        self.orders = []
        self.number_of_general = number_of_general

        self.general_port_dictionary = {}
        for i in range(0, self.number_of_general):
            self.general_port_dictionary[i] = ports[i] 
        logging.debug(f"self.general_port_dictionary: {pformat(self.general_port_dictionary)}")

        self.port_general_dictionary = {}
        for key, value in self.general_port_dictionary.items():
            self.port_general_dictionary[value] = key
        logging.debug(f"self.port_general_dictionary: {pprint.pformat(self.port_general_dictionary)}")

    def start(self):
        self.add_log_info("Start listening for incoming messages...")
        for i in range(self.number_of_general - 1):
            incoming_message: list = self.listen_procedure()
            sender = incoming_message[0]
            self.add_log_info(f"Got incoming message from {sender}: {incoming_message}")

            order = int(incoming_message[1].split("=")[1])
            self.orders.append(order)
            self.add_log_info(f"Append message to a list: {pformat(self.orders)}")

            self.sending_procedure(sender, order)

        self.conclude_action(self.orders)

    def _most_common(self, lst):
        return max(set(lst), key=lst.count)

    def listen_procedure(self):
        input_value, address = self.node_socket.listen()
        logging.debug(f"input_value: {input_value}")
        logging.debug(f"address: {address}")
        incoming_message: list = input_value.split("~")
        return incoming_message

    def sending_procedure(self, sender, order):
        if sender == "supreme_general":
            self.add_log_info("Send supreme general order to other generals with threading...")
            if self.is_traitor:
                order = Order.ATTACK if order == Order.RETREAT else Order.RETREAT
            message = f"general_{self.my_id}~order={order}"
            self.add_log_info(f"message: {message}")
            for other_general_port, value in self.port_general_dictionary.items():
                if value == 0:
                    continue
                if other_general_port == self.my_port:
                    continue
                self.add_log_info("Initiate threading to send the message...")
                thread = threading.Thread(target=self.node_socket.send,
                                          args=(message, other_general_port))
                self.add_log_info("Start threading...")
                thread.start()
                self.add_log_info(f"Done sending message "
                             f"to general {self.port_general_dictionary[other_general_port]}...")
            return message

    def conclude_action(self, orders):
        self.add_log_info("Concluding action...")
        logging.debug(f"is_traitor: {self.is_traitor}")
        if self.is_traitor:
            self.add_log_info("I am a traitor...")
            return None
        else:
            order = self._most_common(orders)
            action = "ATTACK" if order else "RETREAT"
            self.add_log_info(f"action: {action}")
            message = f"general_{self.my_id}~action={order}"
            logging.debug(f"self.city_port: {self.city_port}")
            self.node_socket.send(message, self.city_port)
            self.add_log_info("Done doing my action...")
        return message
    
    def add_log_info(self, message):
        logging.info(f"General{self.my_id}-{message}")


class SupremeGeneral(General):

    def __init__(self, my_id: int, is_traitor: bool, my_port: int, ports: list, 
                 node_socket: UdpSocket, city_port: int, number_of_general: int,
                 order: Order):
        super().__init__(my_id, is_traitor, my_port, ports, node_socket, city_port, number_of_general)
        self.order = order
        logging.debug(f"city_port: {city_port}")

    def sending_procedure(self, sender, order):
        result = []
        message = f"{sender}~order="
        for i in range(1, len(self.port_general_dictionary)):
            general_port = self.general_port_dictionary[i]
            logging.debug(f"my_port: {self.my_port}")
            logging.debug(f"general_port: {general_port}")
            self.add_log_info(f"Send message to general {i} with port {general_port}")
            if self.is_traitor:
                random_order = random.randint(0,1)
                order = Order.RETREAT if random_order == 0 else Order.ATTACK
            result.append(order)
            message_send = f"{message}{order}"
            self.node_socket.send(message_send, general_port)
        self.add_log_info("Finish sending message to other generals...")
        return result

    def start(self):
        self.add_log_info("Supreme general is starting...")
        self.add_log_info("Wait until all generals are running...")
        time.sleep(0.2)
        result = self.sending_procedure("supreme_general", self.order)

        self.conclude_action(result)

    def conclude_action(self, orders):
        self.add_log_info("Concluding action...")
        if self.is_traitor:
            self.add_log_info("I am a traitor...")
            return
        elif self.order:
            self.add_log_info("ATTACK the city...")
        else:
            self.add_log_info("RETREAT from the city...")

        self.add_log_info("Send information to city...")
        message = f"supreme_general~action={self.order}"
        logging.debug(f"message: {message}")
        logging.debug(f"self.city_port: {self.city_port}")
        self.node_socket.send(message, self.city_port)
        self.add_log_info("Done sending information...")
        return message
    
    def add_log_info(self, message):
        logging.info(f"SupremeGeneral-{message}")


def thread_exception_handler(args):
    logging.error(f"Uncaught exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


def main(is_traitor: bool, node_id: int, ports: list, number_of_general: int,
         my_port: int = 0, order: Order = Order.RETREAT,
         is_supreme_general: bool = False, city_port: int = 0):
    threading.excepthook = thread_exception_handler
    try:
        if node_id > 0:
            logging.info(f"General {node_id} is running...")
        else:
            logging.info("Supreme general is running...")
        logging.debug(f"is_traitor: {is_traitor}")
        logging.debug(f"ports: {pformat(ports)}")
        logging.debug(f"my_port: {my_port}")
        logging.debug(f"order: {order}")
        logging.debug(f"is_supreme_general: {is_supreme_general}")
        logging.debug(f"city_port: {city_port}")

        if node_id == 0:
            obj = SupremeGeneral(my_id=node_id,
                                 city_port=city_port,
                                 is_traitor=is_traitor,
                                 node_socket=UdpSocket(my_port),
                                 my_port=my_port,
                                 ports=ports, order=order, 
                                 number_of_general = number_of_general)
        else:
            obj = General(my_id=node_id,
                          city_port=city_port,
                          is_traitor=is_traitor,
                          node_socket=UdpSocket(my_port),
                          my_port=my_port,
                          ports=ports, 
                          number_of_general = number_of_general)
        obj.start()
    except Exception:
        logging.exception("Caught Error")
        raise
