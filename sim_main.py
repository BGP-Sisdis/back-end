import logging
import multiprocessing
import pprint
import random
import sys
import uuid
from argparse import ArgumentParser

# RUN IN PYTHON 3.8.8
import city
import node

list_nodes = []

used_port = set()

logging.basicConfig(format='%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeProcess(multiprocessing.Process):

    def run(self):
        try:
            super().run()
        except Exception:
            logger.error(f"{self.name} has an error")


def reload_logging_config_node(filename):
    from importlib import reload
    reload(logging)
    logging.basicConfig(format='%(asctime)-4s-%(message)s',
                        datefmt='%H:%M:%S',
                        filename=f"logs/{filename}",
                        filemode='w',
                        level=logging.INFO)

def handle_exception(exc_type, exc_value, exc_traceback):
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

def main():
    parser = ArgumentParser()
    parser.add_argument("-G", type=str, dest="generals",
                        help=" A string of generals (i.e. 'l,t,l,l'), where l is loyal and t is a traitor.  "
                             "The first general is the supreme general. "
                             "This argument is designed only to accept four generals",
                        default="l,t,l,l")
    parser.add_argument("-O", type=str, dest="order",
                        help=" The order the commander gives to the other generals (O ∈ {ATTACK,RETREAT})",
                        default="RETREAT")
    args = parser.parse_args()

    logger.info("Processing args...")
    roles = [True if x.strip() == "t" else False for x in args.generals.split(',')]
    order: str = args.order
    logger.debug(f"roles: {pprint.pformat(roles)}")
    logger.debug(f"order: {order}")
    logger.info("Done processing args...")

    execution(roles, order, str(uuid.uuid4()))


def execution(roles, order, session_id):
    """
    Execute byzantine generals problem scenario.

    Parameters
    ----------
    roles : list
        List of generals' role (default is None).
        Role is True when general is a traitor and False when general is loyal.
        Example: [False, True, False, False]

    order : string
        Supreme general command.
        Command: ATTACK or RETREAT

    """
    global used_port

    logger = logging.getLogger(__name__)

    number_of_general = len(roles)

    sys.excepthook = handle_exception

    logger.info("The main program is running...")

    logger.info("Determining the ports that will be used...")

    while True:
        starting_port = random.randint(10000, 11000)
        node_ports = [port for port in range(starting_port, starting_port + number_of_general)]

        port_set = set(node_ports)
        same_port = used_port.intersection(node_ports)
        if len(same_port) == 0:
            break

    used_port = used_port.union(port_set)

    logger.debug(f"node_ports: {node_ports}")
    logger.info("Done determining the ports that will be used...")

    logger.info("Convert order string to binary...")
    order = node.Order.RETREAT if order.upper() == "RETREAT" else node.Order.ATTACK
    logger.debug(f"order: {order}")
    logger.info("Done converting string to binary...")

    reload_logging_config_node(f"{session_id}.txt")

    logger.info("Start running multiple nodes...")
    for node_id in range(number_of_general):
        is_supreme_general = False if node_id else True
        logger.debug(f"General port: {starting_port + node_id}")
        if is_supreme_general:
            process = NodeProcess(target=node.main, args=(
                roles[node_id],
                node_id,
                node_ports,
                number_of_general,
                starting_port + node_id,
                order,
                is_supreme_general,
                starting_port + number_of_general,
            ))
        else:
            process = NodeProcess(target=node.main, args=(
                roles[node_id],
                node_id,
                node_ports,
                number_of_general,
                starting_port + node_id,
                order,
                False,
                starting_port + number_of_general,
            ))
        process.start()
        list_nodes.append(process)

    logger.info("Done running multiple nodes...")
    logger.debug(f"number of running processes: {len(list_nodes)}")

    logger.info("Running city...")
    # reload_logging_config_node(f"city.txt")
    number_loyal_general = roles.count(False)
    logger.debug(f"number_general: {number_loyal_general}")
    return city.main(starting_port+number_of_general, number_loyal_general, len(roles))

if __name__ == '__main__':
    main()
