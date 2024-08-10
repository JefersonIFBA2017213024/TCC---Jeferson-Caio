import os
import sys
import numpy as np

# Verificação e configuração do ambiente SUMO
def configurar_ambiente_sumo():
    if "SUMO_HOME" in os.environ:
        ferramentas_sumo = os.path.join(os.environ["SUMO_HOME"], "tools")
        sys.path.append(ferramentas_sumo)
    else:
        sys.exit("Por favor, declare a variável de ambiente 'SUMO_HOME'.")

configurar_ambiente_sumo()

import traci
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3.dqn.dqn import DQN
from stable_baselines3.common.env_checker import check_env

# Definindo o ambiente SUMO personalizado que herda de gym.Env
class AmbienteSumoGym(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, arquivo_rede, arquivo_rotas, nome_saida_csv, agente_simples=True, usar_gui=False, segundos_simulacao=100000):
        super(AmbienteSumoGym, self).__init__()
        self.arquivo_rede = arquivo_rede
        self.arquivo_rotas = arquivo_rotas
        self.nome_saida_csv = nome_saida_csv
        self.agente_simples = agente_simples
        self.usar_gui = usar_gui
        self.segundos_simulacao = segundos_simulacao
        self._conexao_sumo = None
        self.tempo_simulacao = 0
        self._iniciar_simulacao()

        # Definindo o espaço de ação e o espaço de observação como ginásio espera
        self.action_space = spaces.Discrete(3)  # Exemplo: 3 fases possíveis
        self.observation_space = spaces.Box(low=np.zeros(10), high=np.ones(10), dtype=np.float32)  # Exemplo: 10 variáveis de observação

    def _iniciar_simulacao(self):
        comando_sumo = [sumolib.checkBinary('sumo-gui' if self.usar_gui else 'sumo'),
                        "-n", self.arquivo_rede,
                        "-r", self.arquivo_rotas,
                        "--max-depart-delay", str(100000),
                        "--waiting-time-memory", str(1000)]
        
        traci.start(comando_sumo)
        self._conexao_sumo = traci
        self._definir_sinais_transito()

    def _definir_sinais_transito(self):
        self.sinais_transito = {}
        ids_sinais = self._conexao_sumo.trafficlight.getIDList()
        for id_sinal in ids_sinais:
            self.sinais_transito[id_sinal] = SinalDeTransitoCustomizado(self, id_sinal)

    def reset(self):
        self.tempo_simulacao = 0
        self._iniciar_simulacao()
        return self._obter_observacoes()

    def step(self, action):
        self._aplicar_acoes(action)
        traci.simulationStep()
        self.tempo_simulacao += 1
        observacoes = self._obter_observacoes()
        recompensas = self._calcular_recompensas()
        terminado = self.tempo_simulacao >= self.segundos_simulacao
        return observacoes, recompensas, terminado, {}

    def _aplicar_acoes(self, acoes):
        for id_sinal, acao in enumerate(acoes):
            self.sinais_transito[id_sinal].definir_fase(acao)

    def _obter_observacoes(self):
        observacoes = []
        for id_sinal in self.sinais_transito:
            observacoes.append(self.sinais_transito[id_sinal].calcular_observacao())
        return np.array(observacoes)

    def _calcular_recompensas(self):
        recompensas = []
        for id_sinal in self.sinais_transito:
            recompensas.append(self.sinais_transito[id_sinal].calcular_recompensa())
        return np.array(recompensas)

    def render(self, mode='human'):
        pass

    def close(self):
        traci.close()

# Definindo o sinal de trânsito customizado
class SinalDeTransitoCustomizado:
    def __init__(self, ambiente, id_sinal):
        self.ambiente = ambiente
        self.id_sinal = id_sinal
        self.fase_atual = 0
        self.tempo_desde_mudanca = 0

    def calcular_observacao(self):
        estado_fase = self.fase_atual
        densidade = self._calcular_densidade_faixas()
        fila = self._calcular_fila_faixas()
        observacao = np.array([estado_fase] + densidade + fila, dtype=np.float32)
        return observacao

    def calcular_recompensa(self):
        pressao = self._calcular_pressao()
        return -pressao

    def definir_fase(self, fase):
        self.fase_atual = fase
        self.tempo_desde_mudanca = 0
        self.ambiente._conexao_sumo.trafficlight.setPhase(self.id_sinal, fase)

    def _calcular_densidade_faixas(self):
        faixas_controladas = self.ambiente._conexao_sumo.trafficlight.getControlledLanes(self.id_sinal)
        densidade = []
        for faixa in faixas_controladas:
            num_veiculos = self.ambiente._conexao_sumo.lane.getLastStepVehicleNumber(faixa)
            comprimento_faixa = self.ambiente._conexao_sumo.lane.getLength(faixa)
            densidade.append(num_veiculos / comprimento_faixa)
        return densidade

    def _calcular_fila_faixas(self):
        faixas_controladas = self.ambiente._conexao_sumo.trafficlight.getControlledLanes(self.id_sinal)
        fila = []
        for faixa in faixas_controladas:
            num_veiculos_parados = self.ambiente._conexao_sumo.lane.getLastStepHaltingNumber(faixa)
            comprimento_faixa = self.ambiente._conexao_sumo.lane.getLength(faixa)
            fila.append(num_veiculos_parados / comprimento_faixa)
        return fila

    def _calcular_pressao(self):
        faixas_entrada = self.ambiente._conexao_sumo.trafficlight.getControlledLanes(self.id_sinal)
        faixas_saida = [link[0][1] for link in self.ambiente._conexao_sumo.trafficlight.getControlledLinks(self.id_sinal) if link]
        pressao = sum(self.ambiente._conexao_sumo.lane.getLastStepVehicleNumber(faixa) for faixa em faixas_entrada) - \
                  sum(self.ambiente._conexao_sumo.lane.getLastStepVehicleNumber(faixa) for faixa em faixas_saida)
        return pressao

# Implementação do modelo DQN utilizando a biblioteca Stable-Baselines3
def criar_modelo_dqn(ambiente, politica="MlpPolicy", taxa_aprendizado=0.001, inicio_aprendizado=0, freq_treinamento=1, intervalo_atualizacao_alvo=500, epsilon_inicial=0.05, epsilon_final=0.01, verbose=1):
    modelo_dqn = DQN(
        policy=politica,
        env=ambiente,
        learning_rate=taxa_aprendizado,
        learning_starts=inicio_aprendizado,
        train_freq=freq_treinamento,
        target_update_interval=intervalo_atualizacao_alvo,
        exploration_initial_eps=epsilon_inicial,
        exploration_final_eps=epsilon_final,
        verbose=verbose,
    )
    return modelo_dqn

if __name__ == "__main__":
    # Criação do ambiente SUMO com integração ao Gymnasium
    ambiente_sumo_gym = AmbienteSumoGym(
        arquivo_rede="single-intersection.net.xml",
        arquivo_rotas="single-intersection.rou.xml",
        nome_saida_csv="outputs/2way-single-intersection/dqn",
        agente_simples=True,
        usar_gui=False,
        segundos_simulacao=100000,
    )

    # Verificação do ambiente customizado para garantir compatibilidade com o Gym
    check_env(ambiente_sumo_gym)

    # Configuração e treinamento do modelo DQN usando Stable-Baselines3
    modelo_dqn = criar_modelo_dqn(
        ambiente=ambiente_sumo_gym,
        politica="MlpPolicy",
        taxa_aprendizado=0.001,
        inicio_aprendizado=0,
        freq_treinamento=1,
        intervalo_atualizacao_alvo=500,
        epsilon_inicial=0.05,
        epsilon_final=0.01,
        verbose=1,
    )

    modelo_dqn.learn(total_timesteps=100000)
    
    # Salvando o modelo treinado
    modelo_dqn.save("dqn_single_intersection")
