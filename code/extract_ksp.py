# Подключение требуемых библиотек
import krpc
import time

# Подключение к игре
conn = krpc.connect(name='extract')

# Получение объекта судна
vessel = conn.space_center.active_vessel

# Получение объекта полета
flight = vessel.flight()

# Инициализация словаря данных и ожидание запуска
data_dict = {}
previous_velocity = vessel.flight(vessel.orbit.body.reference_frame).speed
previous_time = conn.space_center.ut
while previous_velocity == 0 or previous_time == 0:
    previous_velocity = vessel.flight(vessel.orbit.body.reference_frame).speed
    previous_time = conn.space_center.ut
    time.sleep(1)
    print('Ожидание запуска')
time.sleep(0.5)

# Определение частоты записи (в секундах)
frequency = 0.1
try:
    while True:
        vessel = conn.space_center.active_vessel

        # Получение объекта полета
        flight = vessel.flight()

        # Получение текущего времени игры
        tick = conn.space_center.ut
        print(tick)

        # Текущая скорость
        current_velocity = vessel.flight(vessel.orbit.body.reference_frame).speed

        # Текущее ускорение
        current_acceleration = (current_velocity - previous_velocity) / (tick - previous_time)

        # Обновление предыдущей скорости и времени
        previous_velocity = current_velocity
        previous_time = tick

        # Текущая масса судна
        current_mass = vessel.mass

        # Удельная тяги на поверхности
        surface_twr = vessel.available_thrust / (vessel.mass * vessel.orbit.body.surface_gravity)

        # Максимальная тяга
        max_thrust = vessel.max_thrust

        # Максимальное ускорение
        max_acceleration = max_thrust / current_mass

        # DeltaV, TWR и SLT каждого этапа
        stage_data = []
        for i in range(vessel.control.current_stage):
            delta_v = vessel.resources_in_decouple_stage(stage=i, cumulative=False).amount('SolidFuel')
            twr = vessel.available_thrust / (vessel.mass * vessel.orbit.body.surface_gravity)
            slt = vessel.specific_impulse * vessel.orbit.body.surface_gravity
            stage_data.append((delta_v, twr, slt))

        # Плотность атмосферы
        atmosphere_density = vessel.flight().atmosphere_density

        # Атмосферное сопротивление
        atmospheric_drag = vessel.flight().drag

        # Угол атаки
        angle_of_attack = vessel.flight().angle_of_attack

        # Орбитальная скорость
        orbital_speed = vessel.flight(vessel.orbit.body.reference_frame).speed

        # Апоцентр
        apoapsis = vessel.orbit.apoapsis

        # Перицентр
        periapsis = vessel.orbit.periapsis

        # Наклон орбиты
        inclination = vessel.orbit.inclination
        current_altitude = vessel.flight().mean_altitude

        # Сохранение данных в словаре
        data_dict[tick] = {
            'Current altitude': current_altitude,
            'Current velocity': current_velocity,
            'Current acceleration': current_acceleration,
            'Current vessel mass': current_mass,
            'Surface TWR': surface_twr,
            'Max thrust': max_thrust,
            'Max acceleration': max_acceleration,
            'Atmosphere density': atmosphere_density,
            'Atmospheric drag': atmospheric_drag,
            'Angle of attack': angle_of_attack,
            'Orbital speed': orbital_speed,
            'Apoapsis': apoapsis,
            'Periapsis': periapsis,
            'Inclination': inclination
        }

        # Ожидание следующей записи
        time.sleep(frequency)
except KeyboardInterrupt: # Выход при нажатии Ctrl+C
    pass

# Запись полученных данных в файл
import json
with open('kspdata.json', 'w+') as f:
    f.write(json.dumps(data_dict))