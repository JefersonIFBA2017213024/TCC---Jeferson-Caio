import os
import subprocess

def generate_routes(period):
    command = f'python "D:\\Program Files (x86)\\Eclipse\\Sumo\\tools\\randomTrips.py" -n network.net.xml -o trips.trips.xml -r routes.rou.xml -e 20000 --random --period {period}'
    subprocess.run(command, shell=True)

def train_model():
    command = 'python ql_4x4grid_pz.py'
    print(f"Executando comando: {command}")
    subprocess.run(command, shell=True)

def main():
    period = 1.5
    min_period = 1.2
    decrement = 0.1

    while period >= min_period:
        print(f"Gerando rotas com período: {period}")
        generate_routes(period)
        print("Iniciando treinamento")
        train_model()
        period -= decrement
        print(f"Treinamento concluído com período: {period + decrement}")

if __name__ == "__main__":
    main()
