# Подключение требуемых библиотек
import krpc
import time
import math

# Устанавливаем соединение с KSP и получаем объекты для управления кораблем
conn = krpc.connect(name='flight')
vessel = conn.space_center.active_vessel
ap = vessel.auto_pilot
control = vessel.control

# Подготовка потоков данных для мониторинга времени, высоты и параметров орбиты
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

# Подготовка потоков данных для мониторинга топлива в первой ступени.
start = vessel.resources_in_decouple_stage(stage=4, cumulative=False)
start_fuel = conn.add_stream(start.amount, 'SolidFuel')

# Настройка управления и активация первой ступени
control.throttle = 0.75
control.sas = True
print('Запуск')
control.activate_next_stage()
time.sleep(3)

# Ожидание расходования топлива и подготовка ко второй ступени
while start_fuel() > 0:
    time.sleep(1)

control.throttle = 1
control.sas_mode = conn.space_center.SASMode.prograde
time.sleep(1)
print('Вторая ступень')
control.activate_next_stage()

# Мониторинг топлива второй ступени и выполнение её работы
f2 = vessel.resources_in_decouple_stage(stage=3, cumulative=False)
f2_fuel = conn.add_stream(f2.amount, 'LiquidFuel')
while f2_fuel() > 1:
    time.sleep(0.1)
print('Третья ступень')
control.activate_next_stage()

# Мониторинг топлива третьей ступени и выполнение её работы
f3 = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
f3_fuel = conn.add_stream(f3.amount, 'LiquidFuel')
while f3_fuel() > 1:
    time.sleep(0.1)
control.activate_next_stage()

# Дождаться достижения апоцентра высотой 500000 метров
while apoapsis() < 500000:
    time.sleep(0.1)
control.throttle = 0
time.sleep(3)

# Расчет дельты-V и создание узла маневра
print('Расчет маневра')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu*((2./r)-(1./a1)))
v2 = math.sqrt(mu*((2./r)-(1./a2)))
delta_v = v2 - v1
node = control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# Расчет времени и параметров сгорания топлива
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# Расчет времени начала сгорания
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2)
lead_time = 5
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
time.sleep(1)
control.throttle = 0
print('Ожидание маневра')
while time_to_apoapsis() - (burn_time/2) > 0:
    time.sleep(0.1)

print('Начало маневра')
control.sas_mode = conn.space_center.SASMode.maneuver
control.throttle = 1

# Ожидание завершения сгорания топлива и завершение маневра
time.sleep(burn_time)
node.remove()
print('Маневр выполнен')
control.sas_mode = conn.space_center.SASMode.prograde
control.throttle = 0
time.sleep(3)

# Активация последних ступеней для отделения спутника
control.activate_next_stage()
time.sleep(2)
print('Раскрытие солнечных панелей')
control.toggle_action_group(1) # Раскрытие солнечных панелей
time.sleep(5)
print('Отделение спутника')
control.activate_next_stage()
time.sleep(5)
control.sas_mode = conn.space_center.SASMode.normal
time.sleep(2)
control.throttle = 0.3
time.sleep(2)
control.throttle = 1
control.sas_mode = conn.space_center.SASMode.retrograde