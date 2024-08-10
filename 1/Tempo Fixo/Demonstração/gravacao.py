import os
import sumolib
import sumopy
from sumopy import Simulation, Sumopy

def capture_frames(output_xml, output_folder, capture_interval=10):
    sim = Simulation(output_xml, step_length=capture_interval)
    os.makedirs(output_folder, exist_ok=True)

    step = 0
    while step < sim.getMaxTime():
        sim.goto(step)
        screenshot_path = os.path.join(output_folder, f"frame_{step:04d}.png")
        sim.saveScreenshot(screenshot_path)
        step += capture_interval

# Captura frames para cada simulação
capture_frames("output_Tempo_Fixo.xml", "frames_Tempo_Fixo")
capture_frames("output_Qlearning.xml", "frames_Qlearning")
capture_frames("output_DQN.xml", "frames_DQN")
