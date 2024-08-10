import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados
fixed_data = pd.read_csv('D:/Área de Trabalho/TCC/documentação/1/traffic_data.csv')
qlearning_data = pd.read_csv('D:/Área de Trabalho/TCC/documentação/1/Qlearning.csv')
dqn_data = pd.read_csv('D:/Área de Trabalho/TCC/documentação/1/Dqn.csv')

# Calcular as médias para cada métrica
metrics = ['system_total_waiting_time', 'system_total_stopped', 'system_mean_speed']
fixed_means = fixed_data[metrics].mean()
qlearning_means = qlearning_data[metrics].mean()
dqn_means = dqn_data[metrics].mean()

# Exibir as médias
print("Médias das métricas para cada método de controle de semáforo:")
print("\nTempo Fixo:")
print(fixed_means)
print("\nQ-learning:")
print(qlearning_means)
print("\nDQN:")
print(dqn_means)

# Plotar os gráficos comparativos
fig, axs = plt.subplots(3, 1, figsize=(10, 15))

for i, metric in enumerate(metrics):
    axs[i].bar(['Tempo Fixo', 'Q-learning', 'DQN'], [fixed_means[metric], qlearning_means[metric], dqn_means[metric]], color=['red', 'blue', 'green'])
    axs[i].set_title(f'Comparação de {metric}')
    axs[i].set_ylabel(metric)
    axs[i].set_xlabel('Método de Controle')

plt.tight_layout()
plt.show()
