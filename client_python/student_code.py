"""
@author AchiyaZigi
OOP - Ex4
Very simple GUI example for python client to communicates with the server and "play the game!"
"""
import ast
import subprocess
from ctypes.wintypes import RGB
from types import SimpleNamespace
from client import Client
import json
from pygame import gfxdraw
import pygame
from pygame import *
import math
from client_python.pokemon import pokemon
from src import *
from src.GraphAlgo import GraphAlgo
from src.Node import Node
from client_python.agent import agent


# init pygame
WIDTH, HEIGHT = 1080, 720

# default port
PORT = 6666
# server host (default localhost 127.0.0.1)
HOST = '127.0.0.1'
pygame.init()
#subprocess.Popen(["powershell.exe", "java -jar Ex4_Server_v0.0.jar 5"])

screen = display.set_mode((WIDTH, HEIGHT), depth=32, flags=RESIZABLE)
clock = pygame.time.Clock()
pygame.font.init()
screen.fill([0, 100, 210])
pygame.display.update()
client = Client()
client.start_connection(HOST, PORT)

# pokemons = client.get_pokemons()
# pokemons_obj = json.loads(pokemons, object_hook=lambda d: SimpleNamespace(**d))

# print(pokemons)

graph_json = client.get_graph()

FONT = pygame.font.SysFont('Arial', 20, bold=True)
graph_json = ast.literal_eval(graph_json)
graph = GraphAlgo()
graph = graph.load_from_json(graph_json)
# get data proportions
min_x = graph.min_x()
min_y = graph.min_y()
max_x = graph.max_x()
max_y = graph.max_y()


#
def scale(data, min_screen, max_screen, min_data, max_data):
    """
    get the scaled data with proportions min_data, max_data
    relative to min and max screen dimentions
    """
    return ((data - min_data) / (max_data - min_data)) * (max_screen - min_screen) + min_screen


# decorate scale with the correct values

def my_scale(data, x=False, y=False):
    if x:
        return scale(data, 50, screen.get_width() - 50, min_x, max_x)
    if y:
        return scale(data, 50, screen.get_height() - 50, min_y, max_y)



radius = 15

client.add_agent("{\"id\":0}")
client.add_agent("{\"id\":1}")
# client.add_agent("{\"id\":2}")
# client.add_agent("{\"id\":3}")

# this commnad starts the server - the game is running now
client.start()

"""
The code below should be improved significantly:
The GUI and the "algo" are mixed - refactoring using MVC design pattern is required.
"""

while client.is_running() == 'true':

    agent_dict = json.loads(client.get_agents())
    agent_dict = agent.build_agent(agent_dict)
    # check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)

    # refresh surface
    screen.fill([0, 100, 210])

    # draw nodes
    for node in graph.get_graph().nodes.values():
        x = my_scale(node.x(), x=True)
        y = my_scale(node.y(), y=True)
        t = (x, y)
        pygame.draw.circle(screen, RGB(40, 40, 40), t, 6)
    # draw edges
    for e in graph.get_graph().nodes.values():
        src_x = e.x()
        src_y = e.y()
        list_out = graph.get_graph().all_out_edges_of_node(e.id)
        src_x = my_scale(src_x, x=True)
        src_y = my_scale(src_y, y=True)
        for edge in list_out:
            dest_x = graph.get_graph().nodes.get(edge).x()
            dest_y = graph.get_graph().nodes.get(edge).y()
            dest_x = my_scale(dest_x, x=True)
            dest_y = my_scale(dest_y, y=True)
            pygame.draw.line(screen, RGB(0, 0, 0), (src_x, src_y), (dest_x, dest_y), 1)
            rotation = math.degrees(math.atan2(src_y - dest_y, dest_x - src_x)) + 90
            pygame.draw.polygon(screen, (120, 120, 130), (
                (dest_x + 0.5 * math.sin(math.radians(rotation)), dest_y + 0.5 * math.cos(math.radians(rotation))),
                (
                    dest_x + 15 * math.sin(math.radians(rotation - 158)),
                    dest_y + 15 * math.cos(math.radians(rotation - 158))),
                (dest_x + 15 * math.sin(math.radians(rotation + 158)),
                 dest_y + 15 * math.cos(math.radians(rotation + 158)))))

    # draw agents
    for age in agent_dict:
        pos_x = age.x()
        pos_y = age.y()
        pos_x = my_scale(pos_x , x=True)
        pos_y = my_scale(pos_y, y=True)
        pygame.draw.circle(screen, Color(122, 61, 23),
                           (pos_x,pos_y), 10)
    # draw pokemons (note: should differ (GUI wise) between the up and the down pokemons (currently they are marked in the same way).
    pokemon_dict = json.loads(client.get_pokemons())
    pokemon_dict = pokemon.build_pokemon(pokemon_dict)
    for p in pokemon_dict:
        pos_x = p.x()
        pos_y = p.y()
        pos_x = my_scale(pos_x , x=True)
        pos_y = my_scale(pos_y, y=True)
        pygame.draw.circle(screen, Color(0, 255, 255), (pos_x,pos_y), 10)


    #
    #
    # update screen changes
    display.update()

    # refresh rate
    clock.tick(60)

    # choose next edge
    for agent1 in agent_dict:
        if agent1.dest == -1:
            next_node = (agent1.src - 1) % len(graph.get_graph().nodes)
            client.choose_next_edge(
                '{"agent_id":' + str(agent1.id) + ', "next_node_id":' + str(next_node) + '}')
            ttl = client.time_to_end()
            print(ttl, client.get_info())

    client.move()
# game over:
