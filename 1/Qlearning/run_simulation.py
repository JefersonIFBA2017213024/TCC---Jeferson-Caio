import os
import sys
import xml.etree.ElementTree as ET
import subprocess

def update_probabilities(filename, increment=0.01, max_values=None):
    if max_values is None:
        max_values = {
            "flow_ns": 0.14,
            "flow_sn": 0.14,
            "flow_we": 0.14,
            "flow_ew": 0.13,
            "flow_en": 0.10,
            "flow_se": 0.10,
            "flow_ws": 0.13,
            "flow_nw": 0.13
        }

    tree = ET.parse(filename)
    root = tree.getroot()

    for flow in root.findall('flow'):
        flow_id = flow.get('id')
        if flow_id in max_values:
            current_prob = float(flow.get('probability'))
            if current_prob < max_values[flow_id]:
                new_prob = min(current_prob + increment, max_values[flow_id])
                flow.set('probability', f"{new_prob:.2f}")

    tree.write(filename)

def create_initial_routes(filename):
    routes_content = '''<routes>
    <!-- Definindo as rotas -->
    <route id="route_ns" edges="n_t t_s"/>
    <route id="route_sn" edges="s_t t_n"/>
    <route id="route_we" edges="w_t t_e"/>
    <route id="route_ew" edges="e_t t_w"/>

    <!-- Definindo rotas com curvas -->
    <route id="route_en" edges="e_t t_n"/>
    <route id="route_se" edges="s_t t_e"/>
    <route id="route_ws" edges="w_t t_s"/>
    <route id="route_nw" edges="n_t t_w"/>

    <!-- Definindo os fluxos -->
    <flow id="flow_ns" route="route_ns" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>
    <flow id="flow_sn" route="route_sn" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>
    <flow id="flow_we" route="route_we" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>
    <flow id="flow_ew" route="route_ew" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>

    <flow id="flow_en" route="route_en" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>
    <flow id="flow_se" route="route_se" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>
    <flow id="flow_ws" route="route_ws" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>
    <flow id="flow_nw" route="route_nw" begin="0" end="100000" probability="0.10" departSpeed="max" departPos="base" departLane="best"/>
</routes>'''

    with open(filename, 'w') as file:
        file.write(routes_content)

def run_ql_script():
    command = [sys.executable, 'ql_2way-single-intersection.py -r queue']
    subprocess.run(command)

# Cria o arquivo inicial com as probabilidades especificadas
create_initial_routes('single-intersection.rou.xml')

# Atualiza as probabilidades e executa o script até que todas atinjam seus valores máximos
max_values = {
    "flow_ns": 0.14,
    "flow_sn": 0.14,
    "flow_we": 0.14,
    "flow_ew": 0.13,
    "flow_en": 0.10,
    "flow_se": 0.10,
    "flow_ws": 0.13,
    "flow_nw": 0.13
}

all_reached_max = False

while not all_reached_max:
    update_probabilities('single-intersection.rou.xml')
    run_ql_script()

    # Verifica se todas as probabilidades atingiram os valores máximos
    tree = ET.parse('single-intersection.rou.xml')
    root = tree.getroot()
    all_reached_max = all(
        float(flow.get('probability')) >= max_values[flow.get('id')]
        for flow in root.findall('flow')
        if flow.get('id') in max_values
    )
