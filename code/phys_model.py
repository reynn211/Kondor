# Подключение требуемых библиотек
import numpy as np
import matplotlib.pyplot as plt

def rocket_altitude(stages):
    # Константы
    g_sealevel = 9.81  # Ускорение свободного падения на уровне моря (м/с^2)
    Cd = 0.5  # Коэффициент аэродинамического сопротивления
    R = 6371000.0  # Радиус Земли (м)
    T0 = 288.15  # Стандартная температура на уровне моря (K)
    L = 0.0065  # Температурный градиент (K/m)

    # Данные ракеты и ступеней
    rocket_reference_area = 1.5
    rho_air_sealevel = 1.2

    eng_masses = [3784*4, 6545, 2355]  # Масса двигателя для каждой ступени (кг)
    fuel_masses = [39160*4, 90100, 25400]  # Масса топлива для каждой ступени (кг)

    thrust_per_stage = [840000*4, 615000, 80000]  # Тяга для каждой ступени (Н)
    burnout_time = [140.0, 340.0, 240.0]  # Время до исчерпания топлива для каждой ступени (с)
    rocket_mass = 0  # Начальная масса ракеты (кг)

    # Начальные условия
    altitude = 0.0
    velocity = 0.0
    altitude_points = []
    total_time = 0

    for stage in range(stages):
    t_stage = np.arange(0, burnout_time[stage], 0.1)

    for t_step in t_stage:
        # Обновление общего времени симуляции
        total_time += t_step

        # Расчет общей массы ракеты (с учетом двигателей и топлива текущей и последующих ступеней)
        mass = rocket_mass + sum(eng_masses[stage:]) + sum(fuel_masses[stage:])

        # Получение текущей тяги
        thrust = thrust_per_stage[stage]

        # Расчет ускорения свободного падения на текущей высоте
        g = g_sealevel * (R / (R + altitude))**2
        gravity_force = -g * mass
        velocity_squared = velocity**2

        # Расчет плотности воздуха на текущей высоте
        rho_air = rho_air_sealevel * np.exp(-altitude / 8000.0)

        # Расчет аэродинамического сопротивления
        drag_force = -0.5 * rho_air * Cd * velocity_squared * rocket_reference_area

        # Расчет ускорения ракеты
        acceleration = (thrust + gravity_force + drag_force) / mass

        # Интеграция скорости и высоты по времени
        velocity += acceleration * 0.1 
        altitude += velocity * 0.1

        # Расчет и обновление расхода топлива в соответствии с временем
        fuel_burn_rate = fuel_masses[stage] / burnout_time[stage]
        fuel_masses[stage] -= fuel_burn_rate * 0.1

        # Запись высоты на текущем временном шаге
        altitude_points.append(altitude)

    return altitude_points

# Время симуляции
total_time = sum([140.0, 340.0, 240.0])
time_points = np.arange(0, total_time, 0.1)

# Количество ступеней ракеты
num_stages = 3

# Рассчитать высоту с течением времени
altitude_points = rocket_altitude(num_stages)

# Отобразить график
plt.plot(time_points, altitude_points, color='green')
plt.title('Высота от времени')
plt.xlabel('Время (с)')
plt.ylabel('Высота (м)')
plt.show()