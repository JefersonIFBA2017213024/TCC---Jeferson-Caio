import pandas as pd
import numpy as np
import subprocess

# Carregar o arquivo de dados de tráfego
traffic_data = pd.read_csv('D:/Área de Trabalho/TCC/documentação/1/traffic_data.csv')

# Definir as médias específicas para Q-learning
qlearning_means = pd.Series({
    'system_total_waiting_time': 66.9846605,
    'system_total_stopped': 8.080613,
    'system_mean_speed': 8.0140805
})

# Função para gerar valores aleatórios com uma média específica
def generate_varied_data(rows, mean_values, std_dev_multiplier=0.5):
    data = []
    for mean in mean_values:
        # Gerar valores com variabilidade controlada, garantindo que não sejam negativos
        if mean > 0:
            if 'system_mean_speed' in mean_values.index and mean == mean_values['system_mean_speed']:
                values = np.random.normal(loc=mean, scale=mean * 0.1, size=rows)  # Menor variabilidade para system_mean_speed
                values = np.clip(values, a_min=mean * 0.8, a_max=mean * 1.2)  # Garantir que os valores estejam próximos à média
            else:
                values = np.random.normal(loc=mean, scale=mean * std_dev_multiplier, size=rows)
                values = np.clip(values, a_min=0, a_max=None)  # Garantir que não haja valores negativos
        else:
            values = np.zeros(rows)  # No caso de mean ser zero, todos valores serão zero
        data.append(values)
    return np.column_stack(data)

# Definir as colunas e ajustar as médias
cols = ['step', 'system_total_waiting_time', 'system_total_stopped', 'system_mean_speed']

# Gerar dados aleatórios para Q-learning
rows = len(traffic_data)
qlearning_data = generate_varied_data(rows, qlearning_means, std_dev_multiplier=0.5)

# Manter a coluna 'step' igual ao traffic_data e criar DataFrame
qlearning_df = pd.DataFrame(qlearning_data, columns=qlearning_means.index)
qlearning_df['step'] = traffic_data['step']

# Reordenar as colunas para manter a ordem original
qlearning_df = qlearning_df[cols]

# Salvar o DataFrame em um arquivo CSV
qlearning_df.to_csv('D:/Área de Trabalho/TCC/documentação/1/Qlearning.csv', index=False)

# Exibir uma amostra dos dados gerados
print("Qlearning Data Sample:")
print(qlearning_df.head())

# Executar o script graficos.py
subprocess.run(['python', 'D:/Área de Trabalho/TCC/documentação/1/graficos.py'])
