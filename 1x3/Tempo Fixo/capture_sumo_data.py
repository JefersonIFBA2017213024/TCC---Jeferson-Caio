import numpy as np
import traci
import csv

def _get_system_info(sumo):
    vehicles = sumo.vehicle.getIDList()
    speeds = [sumo.vehicle.getSpeed(vehicle) for vehicle in vehicles]
    waiting_times = [sumo.vehicle.getWaitingTime(vehicle) for vehicle in vehicles]
    return {
        'system_total_stopped': sum(int(speed < 0.1) for speed in speeds),
        'system_total_waiting_time': sum(waiting_times),
        'system_mean_waiting_time': np.mean(waiting_times) if len(waiting_times) > 0 else 0.0,
        'system_mean_speed': np.mean(speeds) if len(speeds) > 0 else 0.0
    }

def collect_and_save_data(sumo_cfg_file, output_csv_file, steps):
    traci.start([sumo_binary, "-c", sumo_cfg_file])
    
    with open(output_csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['step', 'system_total_stopped', 'system_total_waiting_time', 'system_mean_waiting_time', 'system_mean_speed'])
        
        for step in range(steps):
            traci.simulationStep()
            system_info = _get_system_info(traci)
            writer.writerow([step, system_info['system_total_stopped'], system_info['system_total_waiting_time'], system_info['system_mean_waiting_time'], system_info['system_mean_speed']])
    
    traci.close()

if __name__ == "__main__":
    sumo_binary = "sumo-gui"  # or "sumo-gui" if you want to visualize
    sumo_cfg_file = "single-intersection.sumocfg"  # Your SUMO configuration file
    output_csv_file = "traffic_data.csv"
    steps = 144000  # Number of simulation steps

    collect_and_save_data(sumo_cfg_file, output_csv_file, steps)
