import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Função para carregar dados de um arquivo CSV e pegar amostra a cada 100 passos
def load_data(file_name):
    df = pd.read_csv(file_name)
    return df.iloc[::50, :]  # Seleciona uma amostra a cada 100 linhas

# Carregar dados dos três arquivos CSV
fixed_time_data = load_data('traffic_data.csv')
qlearning_data = load_data('Qlearning.csv')
dqn_data = load_data('Dqn.csv')

# Função para ajustar uma linha aos dados
def fit_line(x, y):
    coef = np.polyfit(x, y, 1)
    poly1d_fn = np.poly1d(coef)
    return poly1d_fn

# Gráfico 1: system_total_stopped vs. step
plt.figure()
plt.plot(fixed_time_data['step'], fixed_time_data['system_total_stopped'], label='Fixed Time', color='blue', alpha=0.6)
plt.plot(qlearning_data['step'], qlearning_data['system_total_stopped'], label='Q-learning', color='green', alpha=0.6)
plt.plot(dqn_data['step'], dqn_data['system_total_stopped'], label='DQN', color='red', alpha=0.6)

# Ajuste linear
plt.plot(fixed_time_data['step'], fit_line(fixed_time_data['step'], fixed_time_data['system_total_stopped'])(fixed_time_data['step']), color='blue', linestyle='-')
plt.plot(qlearning_data['step'], fit_line(qlearning_data['step'], qlearning_data['system_total_stopped'])(qlearning_data['step']), color='green', linestyle='-')
plt.plot(dqn_data['step'], fit_line(dqn_data['step'], dqn_data['system_total_stopped'])(dqn_data['step']), color='red', linestyle='-')

plt.title('Total de Paradas vs. Step')
plt.xlabel('Step')
plt.ylabel('Total de Paradas')
plt.legend()
plt.grid(True)
plt.show()

# Gráfico 2: system_total_waiting_time vs. step
plt.figure()
plt.plot(fixed_time_data['step'], fixed_time_data['system_total_waiting_time'], label='Fixed Time', color='blue', alpha=0.6)
plt.plot(qlearning_data['step'], qlearning_data['system_total_waiting_time'], label='Q-learning', color='green', alpha=0.6)
plt.plot(dqn_data['step'], dqn_data['system_total_waiting_time'], label='DQN', color='red', alpha=0.6)

# Ajuste linear
plt.plot(fixed_time_data['step'], fit_line(fixed_time_data['step'], fixed_time_data['system_total_waiting_time'])(fixed_time_data['step']), color='blue', linestyle='-')
plt.plot(qlearning_data['step'], fit_line(qlearning_data['step'], qlearning_data['system_total_waiting_time'])(qlearning_data['step']), color='green', linestyle='-')
plt.plot(dqn_data['step'], fit_line(dqn_data['step'], dqn_data['system_total_waiting_time'])(dqn_data['step']), color='red', linestyle='-')

plt.title('Tempo de Espera Total vs. Step')
plt.xlabel('Step')
plt.ylabel('Tempo de Espera Total')
plt.legend()
plt.grid(True)
plt.show()

# Gráfico 3: system_mean_speed vs. step
plt.figure()
plt.plot(fixed_time_data['step'], fixed_time_data['system_mean_speed'], label='Fixed Time', color='blue', alpha=0.6)
plt.plot(qlearning_data['step'], qlearning_data['system_mean_speed'], label='Q-learning', color='green', alpha=0.6)
plt.plot(dqn_data['step'], dqn_data['system_mean_speed'], label='DQN', color='red', alpha=0.6)

# Ajuste linear
plt.plot(fixed_time_data['step'], fit_line(fixed_time_data['step'], fixed_time_data['system_mean_speed'])(fixed_time_data['step']), color='blue', linestyle='-')
plt.plot(qlearning_data['step'], fit_line(qlearning_data['step'], qlearning_data['system_mean_speed'])(qlearning_data['step']), color='green', linestyle='-')
plt.plot(dqn_data['step'], fit_line(dqn_data['step'], dqn_data['system_mean_speed'])(dqn_data['step']), color='red', linestyle='-')

plt.title('Velocidade Média vs. Step')
plt.xlabel('Step')
plt.ylabel('Velocidade Média')
plt.legend()
plt.grid(True)
plt.show()
