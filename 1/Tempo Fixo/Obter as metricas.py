import traci
import sumolib
import pandas as pd
import numpy as np

# Caminhos dos arquivos de configuração
sumo_cfg_file = "single-intersection.sumocfg"

# Iniciar SUMO
sumo_binary = sumolib.checkBinary('sumo')
traci.start([sumo_binary, "-c", sumo_cfg_file])

# Listas para armazenar os dados
steps = []
total_stopped = []
total_waiting_time = []
mean_waiting_time = []
mean_speed = []

# Função para obter informações do sistema
def get_system_info():
    vehicles = traci.vehicle.getIDList()
    speeds = [traci.vehicle.getSpeed(vehicle) for vehicle in vehicles]
    waiting_times = [traci.vehicle.getWaitingTime(vehicle) for vehicle in vehicles]
    return {
        "system_total_stopped": sum(int(speed < 0.1) for speed in speeds),
        "system_total_waiting_time": sum(waiting_times),
        "system_mean_waiting_time": 0.0 if len(vehicles) == 0 else np.mean(waiting_times),
        "system_mean_speed": 0.0 if len(vehicles) == 0 else np.mean(speeds),
    }

# Executar a simulação
step = 0
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    
    system_info = get_system_info()
    
    steps.append(step)
    total_stopped.append(system_info["system_total_stopped"])
    total_waiting_time.append(system_info["system_total_waiting_time"])
    mean_waiting_time.append(system_info["system_mean_waiting_time"])
    mean_speed.append(system_info["system_mean_speed"])
    
    step += 1

# Parar SUMO
traci.close()

# Criar DataFrame e salvar em CSV
df = pd.DataFrame({
    "step": steps,
    "system_total_stopped": total_stopped,
    "system_total_waiting_time": total_waiting_time,
    "system_mean_waiting_time": mean_waiting_time,
    "system_mean_speed": mean_speed
})

output_file = "resultados_simulacao.csv"
df.to_csv(output_file, index=False)

print(f"Resultados salvos em {output_file}")
