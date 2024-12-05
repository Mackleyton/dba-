import numpy as np
import matplotlib.pyplot as plt


# Variables iniciales.
lamb = 1/300
num_onu = 15                # Cantidad de ONUs
ancho_banda_total = 2488.0  # Según ancho de banda por cable GPON 2.488 Gb/s de downstream
lat_min = 20.0              # Latencia mínima
lat_max = 100.0             # Latencia máxima
utility = np.zeros(num_onu, dtype=int)
tasa_exito = np.zeros(num_onu, dtype=int)
package = 15000 #largo de un paquete de datos en bits
distancias = np.random.randint(5, 40, size=num_onu)

mu = np.log(200**2 / np.sqrt(20**2 + 200**2))
sigma = np.sqrt(np.log(1 + (20**2 / 200**2)))

def dba():
    demandas_onu = np.random.lognormal(mu, sigma, num_onu)
    posicion_max = np.argmax(demandas_onu)  # Para saber cuál ONU es la que tiene mayor demanda
    demanda_total = np.sum(demandas_onu)

    if demanda_total > ancho_banda_total: 
        variacion = np.random.uniform(0.7, 1.3, num_onu)  # Variable para variar las asignaciones
        asignaciones = (demandas_onu / demanda_total) * ancho_banda_total * variacion
        asignaciones = (asignaciones / np.sum(asignaciones)) * ancho_banda_total
    else:
        asignaciones = demandas_onu
    asignaciones = np.minimum(asignaciones, demandas_onu)

    # Manejo de latencias del sistema
    latencias = (demandas_onu / asignaciones) * lat_min + 1 + np.random.uniform(0.1, 1.0, num_onu) # calculo de latencias por procesamiento, cola, uso de algortimo, y adicion de retransmision
    latencias = latencias + distancias/200000 # considera latencia por distancia
    # Manejo de utilidad de cada ONU dependiendo de la mayor demanda
    utility[posicion_max] += 1  # Sumar 1 al índice de mayor demanda

    # Manejo de la pérdida de paquetes
    paquetes_transmitidos = asignaciones / package
    paquetes_demandados = demandas_onu / package
    perdidas_paquetes = ((paquetes_demandados - paquetes_transmitidos) / paquetes_demandados) *100
    return latencias, perdidas_paquetes

def schedule_a(val, t_a):
    # Se agrega el nuevo elemento de calendarización
    t_a.append(val)
    t_a.sort()

def InputEvent(t_a):
    a = np.random.exponential(lamb)
    schedule_a(t_a[0] + a, t_a)
    latencias, perdidas_paquetes = dba()
    i = 0
    for lat in latencias:
        if lat <= lat_max:
            tasa_exito[i] += 1
        i +=1
    t_a.pop(0)
    return latencias, perdidas_paquetes

def metricas(promedios_latencias,promedios_perdida):
    for onu in range(num_onu):
        plt.plot(promedios_latencias[:, onu], label=f'ONU {onu + 1}')
    plt.xlabel('Legadas (10^5)')
    plt.ylabel('Latencia Promedio (ms)')
    plt.title('Latencia Promedio de cada ONU por Llegadas/10')
    plt.legend(loc='right')
    plt.show()
    for onu in range(num_onu):
        plt.plot(promedios_perdida[:, onu], label=f'ONU {onu + 1}')
    plt.xlabel('Llegadas (10^5)')
    plt.ylabel('Pérdida Promedio de Paquetes (%)')
    plt.title('Pérdida Promedio de Paquetes de cada ONU por Llegadas/10')
    plt.legend(loc='right')
    plt.show()

def simulacion():
    llegadas = 0
    t_a = []
    t_a.append(np.random.exponential(lamb))
    latencias_totales = np.zeros(num_onu)
    perdidas_totales = np.zeros(num_onu)
    promedios_latencias = []
    promedios_perdida = []
    while llegadas < 10**6:
        latencias,perdida = InputEvent(t_a)
        latencias_totales += latencias
        perdidas_totales += perdida
        llegadas += 1
        if llegadas % 10**5 == 0:
            promedio_latencia = latencias_totales / 10**5
            promedios_latencias.append(promedio_latencia.copy())
            latencias_totales = np.zeros(num_onu)
            promedio_perdida = perdidas_totales / 10**5
            promedios_perdida.append(promedio_perdida.copy())
            perdidas_totales = np.zeros(num_onu)

    promedios_latencias = np.array(promedios_latencias)
    promedio_perdida = np.array(promedios_perdida)

    print("La ONU con mayor demanda es: ",np.argmax(utility)+1)
    print("La ONU con menor demanda es: ",np.argmin(utility)+1)
    print("Se muestra la lista por máximo de demanda por iteración de cada ONU: ",utility)
    print("Se muestra la lista con las tasas de exito en cuanto a latencia de cada ONU en porcentaje: ",tasa_exito/10**4)
    metricas(promedios_latencias,promedio_perdida)


simulacion()