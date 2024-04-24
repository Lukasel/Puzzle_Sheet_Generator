import json

with open('config/diagram_board_colors.json') as file:
    diagram_board_colors = json.load(file)

with open('config/config.json') as config_file:
    config = json.load(config_file)
