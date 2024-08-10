import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = 'resultados_simulacao.csv'
data = pd.read_csv(file_path)

# Plotting the data
plt.figure(figsize=(15, 10))

# Gráfico 1: step x system_total_stopped
plt.subplot(2, 2, 1)
plt.plot(data['step'], data['system_total_stopped'], label='Veículos Parados')
plt.xlabel('Passo (step)')
plt.ylabel('Total de Veículos Parados')
plt.title('Passo x Total de Veículos Parados')
plt.legend()

# Gráfico 2: step x system_total_waiting_time
plt.subplot(2, 2, 2)
plt.plot(data['step'], data['system_total_waiting_time'], label='Tempo Total de Espera', color='orange')
plt.xlabel('Passo (step)')
plt.ylabel('Tempo Total de Espera')
plt.title('Passo x Tempo Total de Espera')
plt.legend()

# Gráfico 3: step x system_mean_waiting_time
plt.subplot(2, 2, 3)
plt.plot(data['step'], data['system_mean_waiting_time'], label='Tempo Médio de Espera', color='green')
plt.xlabel('Passo (step)')
plt.ylabel('Tempo Médio de Espera')
plt.title('Passo x Tempo Médio de Espera')
plt.legend()

# Gráfico 4: step x system_mean_speed
plt.subplot(2, 2, 4)
plt.plot(data['step'], data['system_mean_speed'], label='Velocidade Média', color='red')
plt.xlabel('Passo (step)')
plt.ylabel('Velocidade Média')
plt.title('Passo x Velocidade Média')
plt.legend()

# Ajustar layout e salvar o gráfico
plt.tight_layout()
output_path = 'graficos_TempoFixo.png'
plt.savefig(output_path)

output_path
