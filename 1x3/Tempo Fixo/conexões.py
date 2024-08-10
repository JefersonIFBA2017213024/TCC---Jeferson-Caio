import os
import subprocess

# Defina o caminho para o script randomTrips.py
random_trips_script = r"D:\Program Files (x86)\Eclipse\Sumo\tools\randomTrips.py"
network_file = "network.net.xml"  # Substitua pelo caminho do seu arquivo de rede
output_trips_file = "trips.trips.xml"  # Substitua pelo caminho de saída desejado para as viagens
output_routes_file = "routes.rou.xml"  # Substitua pelo caminho de saída desejado para as rotas

# Comando para gerar rotas usando o randomTrips.py
command = [
    "python", random_trips_script,
    "-n", network_file,
    "-o", output_trips_file,
    "-r", output_routes_file,
    "--random",
    "--period", "1.7",
    "--end", "7200",
    "--seed", "42"
]

# Executar o comando
try:
    subprocess.run(command, check=True)
    print("Rotas e viagens geradas com sucesso!")
except subprocess.CalledProcessError as e:
    print(f"Erro ao gerar rotas e viagens: {e}")
