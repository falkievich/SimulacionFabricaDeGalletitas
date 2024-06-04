import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

# Parámetros del sistema
lambda_ = 1  # Tasa de llegada de clientes (clientes por minuto)
mu1 = 1/3    # Tasa de servicio de degustación (clientes por minuto)
mu2 = 1/4    # Tasa de servicio de encuestas (clientes por minuto)
c1 = 2       # Número de estaciones de degustación
c2 = 3       # Número de computadoras/tablets

# Variables para recolección de estadísticas
num_clients_degustation = []      # Número de clientes en la cola de degustación en cada instante
num_clients_survey = []           # Número de clientes en la cola de encuestas en cada instante
waiting_times_degustation = []    # Tiempo de espera de cada cliente en la cola de degustación
waiting_times_survey = []         # Tiempo de espera de cada cliente en la cola de encuestas
total_times_system = []           # Tiempo total de cada cliente en el sistema

# Clase que representa el sistema de análisis sensorial
class Galletitas:
    def __init__(self, env, c1, c2, mu1, mu2):
        self.env = env
        self.degustation_station = simpy.Resource(env, capacity=c1)  # Estaciones de degustación
        self.survey_station = simpy.Resource(env, capacity=c2)       # Computadoras/tablets para encuestas
        self.mu1 = mu1
        self.mu2 = mu2

    # Proceso de degustación
    def degustation(self, client):
        yield self.env.timeout(random.expovariate(self.mu1))  # Tiempo de servicio de degustación

    # Proceso de llenado de encuesta
    def survey(self, client):
        yield self.env.timeout(random.expovariate(self.mu2))  # Tiempo de servicio de encuesta

# Función que simula la llegada y procesamiento de un cliente
def client(env, name, galletitas):
    arrival_time = env.now  # Tiempo de llegada del cliente

    # Cola de degustación
    with galletitas.degustation_station.request() as request:
        yield request  # Esperar hasta que una estación de degustación esté disponible
        start_service_degustation = env.now
        num_clients_degustation.append(len(galletitas.degustation_station.queue))
        yield env.process(galletitas.degustation(name))  # Tiempo de servicio de degustación
        waiting_times_degustation.append(env.now - start_service_degustation)

    # Cola de encuestas
    with galletitas.survey_station.request() as request:
        yield request  # Esperar hasta que una computadora/tablet esté disponible
        start_service_survey = env.now
        num_clients_survey.append(len(galletitas.survey_station.queue))
        yield env.process(galletitas.survey(name))  # Tiempo de servicio de encuesta
        waiting_times_survey.append(env.now - start_service_survey)

    # Tiempo total en el sistema
    total_times_system.append(env.now - arrival_time)

# Función que genera llegadas de clientes
def setup(env, lambda_, galletitas):
    i = 0
    while True:
        yield env.timeout(random.expovariate(lambda_))  # Tiempo entre llegadas de clientes
        i += 1
        env.process(client(env, f'Cliente {i}', galletitas))  # Procesar un nuevo cliente

# Inicialización del entorno de simulación
env = simpy.Environment()
galletitas = Galletitas(env, c1, c2, mu1, mu2)

# Ejecutar la simulación
env.process(setup(env, lambda_, galletitas))
env.run(until=100)  # Tiempo de simulación (en minutos)

# Calcular medidas de desempeño
avg_num_clients_degustation = np.mean(num_clients_degustation)
avg_num_clients_survey = np.mean(num_clients_survey)
avg_waiting_time_degustation = np.mean(waiting_times_degustation)
avg_waiting_time_survey = np.mean(waiting_times_survey)
avg_total_time_system = np.mean(total_times_system)

# Imprimir resultados
print("\nNúmero medio de clientes en la cola de degustación:", avg_num_clients_degustation)
print("Número medio de clientes en la cola de encuestas:", avg_num_clients_survey)
print("Tiempo medio de espera en la cola de degustación:", avg_waiting_time_degustation)
print("Tiempo medio de espera en la cola de encuestas:", avg_waiting_time_survey)
print("Tiempo medio total en el sistema:", avg_total_time_system)

# Graficar resultados a través de Gráficas de líneas
plt.figure(figsize=(12, 6))

plt.subplot(311)
plt.plot(num_clients_degustation, label='Cola de degustación')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Número de clientes')
plt.legend()

plt.subplot(312)
plt.plot(num_clients_survey, label='Cola de encuestas')
plt.xlabel('Tiempo (minutos)')
plt.ylabel('Número de clientes')
plt.legend()

plt.subplot(313)
plt.plot(total_times_system, label='Tiempo total en el sistema')
plt.xlabel('Cliente')
plt.ylabel('Tiempo (minutos)')
plt.legend()

plt.tight_layout()
plt.show()
