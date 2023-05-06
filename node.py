# Nama: Shafira Putri Novia Hartanti
# NPM: 1906293316

import logging
import threading
import time
import random

from node_socket import UdpSocket
from pprint import pformat
from state import State, client_logs


class Order:
    RETREAT = 0
    ATTACK = 1


class General:

    def __init__(self, my_id: int, is_traitor: bool, my_port: int,
                 ports: list, node_socket: UdpSocket, city_port: int, state: State):
        self.ports = ports
        self.my_id = my_id
        self.city_port = city_port
        self.node_socket = node_socket
        self.my_port = my_port
        self.is_traitor = is_traitor
        self.state = state

    def start(self):
        messages = []

        # Receiving message from supreme general
        logging.info(f"Start listening on port {self.my_port} for incoming messages...")
        self.state.add_log(f"Node - Start listening for incoming messages...")
        print(self.state)
        supreme_message = self.listen_procedure()
        logging.info(f"Got incoming message from supreme_general: {supreme_message}")

        # Get order message
        messages.append(int(supreme_message[1].split("=")[1]))
        logging.info(f"Append message to a list: {messages}")

        # Send message to other generals
        logging.info("Send supreme general order to other generals with threading...")
        self.sending_procedure(f"supreme_general", messages[0])

        # Receiving message from other generals
        for i in range (2):
            message = self.listen_procedure()
            messages.append(int(message[1].split("=")[1]))
            logging.info(f"Append message to a list: {messages}")

        # Conclude action from other generals messages
        self.conclude_action(messages)
        return None

    def listen_procedure(self):
        # Getting message from other
        bytes_address_pair = self.node_socket.listen()

        message = bytes_address_pair[0].split("~")
        logging.info(f"Got incoming message from {message[0]}: {message}")

        return message

    def sending_procedure(self, sender, order):
        if sender != "supreme_general":
            return None

        # Check if general is a traitor
        if self.is_traitor:
            # If general is a traitor, change order the opposite
            order = 1 if order == 0 else 0

        # Define the message
        message = f"general_{self.my_id}~order={order}"
        logging.info(f"message: {message}")

        # Send message to other generals
        for id in range(1,4):
            if self.ports[id] != self.my_port:
                self.node_socket.send(message, self.ports[id])
                logging.info(f"Done sending message to general {id}...")

        return message

    def conclude_action(self, orders):

        logging.info("Concluding action...")

        # Count ATTACK and RETREAT order
        count_0 = orders.count(0)
        count_1 = orders.count(1)
        order = 2

        # Conclude action from order count
        if self.is_traitor:
            logging.info("I am a traitor...")
        elif count_0 > count_1:
            order = 0
            logging.info("action: RETREAT")
            logging.info("Done doing my action...")
        elif count_0 < count_1:
            order = 1
            logging.info("action: ATTACK")
            logging.info("Done doing my action...")

        # Send action message to city
        time.sleep(1)
        message = f"general_{self.my_id}~action={order}"
        self.node_socket.send(message, self.city_port)

        return message


class SupremeGeneral(General):

    def __init__(self, my_id: int, is_traitor: bool, my_port: int, ports: list,
                 node_socket: UdpSocket, city_port: int, order: Order, state: State):
        super().__init__(my_id, is_traitor, my_port, ports, node_socket, city_port, state)
        self.order = order

    def sending_procedure(self, sender, order):

        result = []

        for id in range(1,4):
            logging.info(f"Sending message to general {id} with port {self.ports[id]}")

            # Check if supreme general is a traitor
            if self.is_traitor:
                if id % 2 == 0:
                    # If supreme general is a traitor, sends a retreat command to even-numbered generals
                    order = Order.RETREAT
                elif id % 2 == 1:
                    # If supreme general is a traitor, sends an attack command to the odd-numbered generals
                    order = Order.ATTACK

            # Send message to other generals
            self.node_socket.send(f"{sender}~order={order}", self.ports[id])
            result.append(order)

        logging.info("Finish sending message to other generals...")

        return result

    def start(self):
        logging.info("Supreme general is starting...")

        logging.info("Wait until all generals are running...")
        time.sleep(1)

        # Send message to other generals
        self.sending_procedure("supreme_general", self.order)
        time.sleep(1)

        # Conclude action
        self.conclude_action([self.order])
        return None

    def conclude_action(self, orders):
        """
        TODO
        :param orders: list
        :return: str or None
        """
        logging.info("Concluding action...")
        order = 2

        # Conclude action
        if self.is_traitor:
            logging.info("I am a traitor...")
        elif self.order == 0:
            order = 0
            logging.info("RETREAT from the city...")
            logging.info("Done doing my action...")
        elif self.order == 1:
            order = 1
            logging.info("ATTACK the city")
            logging.info("Done doing my action...")

        # Send action message to city
        logging.info("Send information to city...")
        message = f"supreme_general~action={order}"
        self.node_socket.send(message, self.city_port)
        logging.info("Done sending information...")

        return message


def thread_exception_handler(args):
    logging.error(f"Uncaught exception", exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


def main(state: State, client_id: str, is_traitor: bool, node_id: int, ports: list,
         my_port: int = 0, order: Order = Order.RETREAT,
         is_supreme_general: bool = False, city_port: int = 0,
         ):
    print("in node main")
    print(state)
    print(state.name)
    threading.excepthook = thread_exception_handler
    try:
        if node_id > 0:
            logging.info(f"General {node_id} is running...")
            state.add_log(f"General {node_id} is running...")
        else:
            logging.info("Supreme general is running...")
            state.add_log("Supreme general is running...")
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
                                 state=state)
        else:
            obj = General(my_id=node_id,
                          city_port=city_port,
                          is_traitor=is_traitor,
                          node_socket=UdpSocket(my_port),
                          my_port=my_port,
                          ports=ports,
                          state=state)
        obj.start()
        print(client_logs)
        # client_logs[client_id].append("Node starting.")
        # print(client_id)
    except Exception:
        logging.exception("Caught Error")
        raise
