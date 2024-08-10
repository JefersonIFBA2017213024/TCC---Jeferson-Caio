import os
import sys
from typing import Callable, List, Union
import numpy as np

# Verificação e adição de caminhos de ferramentas SUMO
def verificar_sumo_home():
    if 'SUMO_HOME' in os.environ:
        ferramentas_sumo = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(ferramentas_sumo)
    else:
        sys.exit("Por favor, declare a variável de ambiente 'SUMO_HOME'.")

verificar_sumo_home()

import traci
from gymnasium import spaces

class SinalDeTransito:
    
    INTERVALO_MINIMO = 2.5

    def __init__(self, 
                 ambiente, 
                 id_sinal: List[str], 
                 tempo_delta: int, 
                 tempo_amarelo: int, 
                 verde_minimo: int, 
                 verde_maximo: int,
                 tempo_inicio: int,
                 funcao_recompensa: Union[str, Callable], 
                 conexao_sumo):
        self.id = id_sinal
        self.ambiente = ambiente
        self.tempo_delta = tempo_delta
        self.tempo_amarelo = tempo_amarelo
        self.verde_minimo = verde_minimo
        self.verde_maximo = verde_maximo
        self.fase_verde = 0
        self.is_yellow = False
        self.tempo_desde_ultima_mudanca_fase = 0
        self.tempo_proxima_acao = tempo_inicio
        self.ultima_medicao = 0.0
        self.ultima_recompensa = None
        self.funcao_recompensa = funcao_recompensa
        self.conexao_sumo = conexao_sumo

        if isinstance(self.funcao_recompensa, str):
            if self.funcao_recompensa in SinalDeTransito.funcao_recompensas.keys():
                self.funcao_recompensa = SinalDeTransito.funcao_recompensas[self.funcao_recompensa]
            else:
                raise NotImplementedError(f'Função de recompensa {self.funcao_recompensa} não implementada')

        if isinstance(self.ambiente.funcao_observacao, Callable):
            self.funcao_observacao = self.ambiente.funcao_observacao
        else:
            if self.ambiente.funcao_observacao in SinalDeTransito.funcao_observacoes.keys():
                self.funcao_observacao = SinalDeTransito.funcao_observacoes[self.ambiente.funcao_observacao]
            else:
                raise NotImplementedError(f'Função de observação {self.ambiente.funcao_observacao} não implementada')

        self.construir_fases()

        self.faixas = list(dict.fromkeys(self.conexao_sumo.trafficlight.getControlledLanes(self.id)))  # Remove duplicatas e mantém a ordem
        self.faixas_saida = [link[0][1] for link in self.conexao_sumo.trafficlight.getControlledLinks(self.id) if link]
        self.faixas_saida = list(set(self.faixas_saida))
        self.comprimento_faixas = {faixa: self.conexao_sumo.lane.getLength(faixa) for faixa in self.faixas + self.faixas_saida}

        self.observation_space = spaces.Box(low=np.zeros(self.num_fases_verdes+1+2*len(self.faixas), dtype=np.float32), 
                                            high=np.ones(self.num_fases_verdes+1+2*len(self.faixas), dtype=np.float32))
        self.discrete_observation_space = spaces.Tuple((
            spaces.Discrete(self.num_fases_verdes),                       # Fase Verde
            spaces.Discrete(2),                                           # Variável binária ativa se verde_minimo segundos já decorreram
            *(spaces.Discrete(10) for _ in range(2*len(self.faixas)))      # Densidade e densidade de veículos parados para cada faixa
        ))
        self.action_space = spaces.Discrete(self.num_fases_verdes)

    def construir_fases(self):
        fases = self.conexao_sumo.trafficlight.getAllProgramLogics(self.id)[0].phases
        if self.ambiente.ts_fixo:
            self.num_fases_verdes = len(fases) // 2  # Número de fases verdes = número de fases (verde+amarelo) dividido por 2
            return

        self.fases_verdes = []
        self.dicionario_amarelo = {}
        for fase in fases:
            estado = fase.state
            if 'y' not in estado and (estado.count('r') + estado.count('s') != len(estado)):
                self.fases_verdes.append(self.conexao_sumo.trafficlight.Phase(60, estado))
        self.num_fases_verdes = len(self.fases_verdes)
        self.todas_fases = self.fases_verdes.copy()

        for i, fase1 in enumerate(self.fases_verdes):
            for j, fase2 in enumerate(self.fases_verdes):
                if i == j: 
                    continue
                estado_amarelo = ''
                for s in range(len(fase1.state)):
                    if (fase1.state[s] == 'G' or fase1.state[s] == 'g') and (fase2.state[s] == 'r' or fase2.state[s] == 's'):
                        estado_amarelo += 'y'
                    else:
                        estado_amarelo += fase1.state[s]
                self.dicionario_amarelo[(i, j)] = len(self.todas_fases)
                self.todas_fases.append(self.conexao_sumo.trafficlight.Phase(self.tempo_amarelo, estado_amarelo))

        programas = self.conexao_sumo.trafficlight.getAllProgramLogics(self.id)
        logica = programas[0]
        logica.type = 0
        logica.phases = self.todas_fases
        self.conexao_sumo.trafficlight.setProgramLogic(self.id, logica)
        self.conexao_sumo.trafficlight.setRedYellowGreenState(self.id, self.todas_fases[0].state)

    @property
    def tempo_para_agir(self):
        return self.tempo_proxima_acao == self.ambiente.sim_step
    
    def atualizar(self):
        self.tempo_desde_ultima_mudanca_fase += 1
        if self.is_yellow and self.tempo_desde_ultima_mudanca_fase == self.tempo_amarelo:
            self.conexao_sumo.trafficlight.setRedYellowGreenState(self.id, self.todas_fases[self.fase_verde].state)
            self.is_yellow = False

    def definir_proxima_fase(self, nova_fase):
        nova_fase = int(nova_fase)
        if self.fase_verde == nova_fase or self.tempo_desde_ultima_mudanca_fase < self.tempo_amarelo + self.verde_minimo:
            self.conexao_sumo.trafficlight.setRedYellowGreenState(self.id, self.todas_fases[self.fase_verde].state)
            self.tempo_proxima_acao = self.ambiente.sim_step + self.tempo_delta
        else:
            self.conexao_sumo.trafficlight.setRedYellowGreenState(self.id, self.todas_fases[self.dicionario_amarelo[(self.fase_verde, nova_fase)]].state)
            self.fase_verde = nova_fase
            self.tempo_proxima_acao = self.ambiente.sim_step + self.tempo_delta
            self.is_yellow = True
            self.tempo_desde_ultima_mudanca_fase = 0
    
    def calcular_observacao(self):
        return self.funcao_observacao(self)
            
    def calcular_recompensa(self):
        self.ultima_recompensa = self.funcao_recompensa(self)
        return self.ultima_recompensa
    
    def _recompensa_pressao(self):
        return -self.obter_pressao()
    
    def _recompensa_velocidade_media(self):
        return self.obter_velocidade_media()

    def _recompensa_fila(self):
        return -self.obter_total_fila()

    def _recompensa_diferenca_tempo_espera(self):
        tempo_espera_ts = sum(self.obter_tempo_acumulado_espera_por_faixa()) / 100.0
        recompensa = self.ultima_medicao - tempo_espera_ts
        self.ultima_medicao = tempo_espera_ts
        return recompensa

    def _funcao_observacao_padrao(self):
        id_fase = [1 if self.fase_verde == i else 0 for i in range(self.num_fases_verdes)]  # Codificação one-hot
        verde_minimo = [0 if self.tempo_desde_ultima_mudanca_fase < self.verde_minimo + self.tempo_amarelo else 1]
        densidade = self.obter_densidade_faixas()
        fila = self.obter_fila_faixas()
        observacao = np.array(id_fase + verde_minimo + densidade + fila, dtype=np.float32)
        return observacao

    def obter_tempo_acumulado_espera_por_faixa(self):
        tempo_espera_por_faixa = []
        for faixa in self.faixas:
            lista_veiculos = self.conexao_sumo.lane.getLastStepVehicleIDs(faixa)
            tempo_espera = 0.0
            for veiculo in lista_veiculos:
                faixa_veiculo = self.conexao_sumo.vehicle.getLaneID(veiculo)
                acc = self.conexao_sumo.vehicle.getAccumulatedWaitingTime(veiculo)
                if veiculo not in self.ambiente.veiculos:
                    self.ambiente.veiculos[veiculo] = {faixa_veiculo: acc}
                else:
                    self.ambiente.veiculos[veiculo][faixa_veiculo] = acc - sum([self.ambiente.veiculos[veiculo][faixa] for faixa in self.ambiente.veiculos[veiculo].keys() if faixa != faixa_veiculo])
                tempo_espera += self.ambiente.veiculos[veiculo][faixa_veiculo]
            tempo_espera_por_faixa.append(tempo_espera)
        return tempo_espera_por_faixa

    def obter_velocidade_media(self):
        velocidade_media = 0.0
        veiculos = self._obter_lista_veiculos()
        if len(veiculos) == 0:
            return 1.0
        for veiculo in veiculos:
            velocidade_media += self.conexao_sumo.vehicle.getSpeed(veiculo) / self.conexao_sumo.vehicle.getAllowedSpeed(veiculo)
        return velocidade_media / len(veiculos)

    def obter_pressao(self):
        return sum(self.conexao_sumo.lane.getLastStepVehicleNumber(faixa) for faixa in self.faixas_saida) - sum(self.conexao_sumo.lane.getLastStepVehicleNumber(faixa) for faixa in self.faixas)

    def obter_densidade_faixas_saida(self):
        densidade_faixas = [self.conexao_sumo.lane.getLastStepVehicleNumber(faixa) / (self.comprimento_faixas[faixa] / (self.INTERVALO_MINIMO + self.conexao_sumo.lane.getLastStepLength(faixa))) for faixa in self.faixas_saida]
        return [min(1, densidade) for densidade in densidade_faixas]

    def obter_densidade_faixas(self):
        densidade_faixas = [self.conexao_sumo.lane.getLastStepVehicleNumber(faixa) / (self.comprimento_faixas[faixa] / (self.INTERVALO_MINIMO + self.conexao_sumo.lane.getLastStepLength(faixa))) for faixa in self.faixas]
        return [min(1, densidade) for densidade in densidade_faixas]

    def obter_fila_faixas(self):
        fila_faixas = [self.conexao_sumo.lane.getLastStepHaltingNumber(faixa) / (self.comprimento_faixas[faixa] / (self.INTERVALO_MINIMO + self.conexao_sumo.lane.getLastStepLength(faixa))) for faixa in self.faixas]
        return [min(1, fila) for fila in fila_faixas]

    def obter_total_fila(self):
        return sum(self.conexao_sumo.lane.getLastStepHaltingNumber(faixa) for faixa in self.faixas)

    def _obter_lista_veiculos(self):
        lista_veiculos = []
        for faixa in self.faixas:
            lista_veiculos += self.conexao_sumo.lane.getLastStepVehicleIDs(faixa)
        return lista_veiculos

    @classmethod
    def registrar_funcao_recompensa(cls, fn):
        if fn.__name__ in cls.funcao_recompensas.keys():
            raise KeyError(f'Função de recompensa {fn.__name__} já existe')

        cls.funcao_recompensas[fn.__name__] = fn

    @classmethod
    def registrar_funcao_observacao(cls, fn):
        if fn.__name__ in cls.funcao_observacoes.keys():
            raise KeyError(f'Função de observação {fn.__name__} já existe')

        cls.funcao_observacoes[fn.__name__] = fn

    funcao_recompensas = {
        'diff-waiting-time': _recompensa_diferenca_tempo_espera,
        'average-speed': _recompensa_velocidade_media,
        'queue': _recompensa_fila,
        'pressure': _recompensa_pressao
    }

    funcao_observacoes = {
        'default': _funcao_observacao_padrao
    }
