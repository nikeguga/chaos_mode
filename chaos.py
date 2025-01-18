import threading
import time
import os
import math
import hashlib
import random
from queue import Queue

# =============================================================================
# Хаотическая подсистема 1: Логистическая карта
# =============================================================================
def logistic_map_thread(entropy_pool, queue, steps=1000):
    """
    Поток эволюции логистической карты: X_{n+1} = r * X_n * (1 - X_n).
    В конце каждого шага часть данных смешивается в общую «энтропийную копилку».
    """
    # Параметр r в хаотической области ~ (3.569..., 4.0)
    r = random.uniform(3.7, 4.0)
    # Случайное начальное значение в (0, 1)
    x = random.random()

    for step in range(steps):
        x = r * x * (1 - x)git 
        # Собираем микросекундные задержки, чтобы усилить эффект непредсказуемости
        time.sleep(random.random() / 10000.0)

        # Микс (r, x, текущее время в наносекундах)
        mix_data = f"{r:.6f}_{x:.6f}_{time.perf_counter_ns()}"
        queue.put(mix_data)  # Отправляем в очередь для централизованного смешения

# =============================================================================
# Хаотическая подсистема 2: Система Лоренца (упрощённая версия)
# =============================================================================
def lorenz_system_thread(entropy_pool, queue, steps=1000):
    """
    Поток эволюции, приблизительно описывающий хаотическую систему Лоренца:
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z
    с некоторыми случайными параметрами.
    """
    sigma = random.uniform(9.0, 11.0)
    rho   = random.uniform(27.0, 29.0)
    beta  = random.uniform(2.5, 3.0)

    # Случайные начальные условия
    x = random.random()
    y = random.random()
    z = random.random()

    dt = 0.01  # Шаг интегрирования
    for step in range(steps):
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt

        x += dx
        y += dy
        z += dz

        time.sleep(random.random() / 10000.0)

        # Отправляем часть данных в общую очередь
        mix_data = f"{sigma:.6f}_{rho:.6f}_{beta:.6f}_{x:.6f}_{y:.6f}_{z:.6f}_{time.perf_counter_ns()}"
        queue.put(mix_data)

# =============================================================================
# Хаотическая подсистема 3: Случайные блуждания + системная энтропия
# =============================================================================
def random_walk_thread(entropy_pool, queue, steps=1000):
    """
    Поток, моделирующий случайное блуждание по оси, подмешивая системную энтропию
    (например, чтение из os.urandom, время и т.д.).
    """
    position = 0.0

    for step in range(steps):
        # Часть энтропии напрямую из системного генератора
        sys_random_bytes = os.urandom(8)  # 8 байт
        sys_random_value = int.from_bytes(sys_random_bytes, byteorder='big', signed=False)
        
        # Смещение: превратим sys_random_value в случайное число и нормализуем
        shift = (sys_random_value % 100) - 50  # от -50 до +49
        position += shift * 0.001  # регулируем скорость блуждания

        time.sleep(random.random() / 10000.0)

        mix_data = f"{position:.6f}_{sys_random_value}_{time.perf_counter_ns()}"
        queue.put(mix_data)

# =============================================================================
# Функция-смешиватель (centrally mix) для сбора энтропии из очереди
# =============================================================================
def entropy_collector(queue, final_result, run_time=5):
    """
    Собирает данные из очереди в течение run_time секунд, смешивает их
    криптографическим хэш-функцией (SHA-256).
    """
    end_time = time.time() + run_time
    hasher = hashlib.sha256()

    while time.time() < end_time or not queue.empty():
        try:
            data_chunk = queue.get(timeout=0.1)
            # "Сольём" строку в хеш
            hasher.update(data_chunk.encode('utf-8'))
        except:
            pass

    # Записываем финальное значение хэша как результат
    final_hash = hasher.hexdigest()
    final_result.append(final_hash)

# =============================================================================
# Запуск системы
# =============================================================================
def run_chaotic_system(total_time=5):
    """
    Запускает три потока с различными хаотическими или случайными моделями
    и один поток-собиратель, который смешивает собранную энтропию в общий хеш.
    
    :param total_time: время работы системы (в секундах).
    :return: итоговый хеш как "случайный" результат.
    """
    # Общий пул энтропии может быть в виде структуры данных, 
    # но для наглядности используем очередь.
    queue = Queue()
    final_result = []

    # Создаём и стартуем три рабочих потока
    t1 = threading.Thread(target=logistic_map_thread, args=(None, queue, 10_000))
    t2 = threading.Thread(target=lorenz_system_thread, args=(None, queue, 10_000))
    t3 = threading.Thread(target=random_walk_thread, args=(None, queue, 10_000))
    
    # Поток-собиратель
    collector_thread = threading.Thread(target=entropy_collector, args=(queue, final_result, total_time))

    t1.start()
    t2.start()
    t3.start()
    collector_thread.start()

    # Дожидаемся завершения потока-собирателя
    collector_thread.join()

    # Останавливаем рабочие потоки (в демо-режиме жестко прерываем)
    # В реальном случае можно было бы организовать механизм сигналов остановки.
    return final_result[0] if final_result else None

# Пример использования
if __name__ == "__main__":
    print("Запуск хаотической системы для генерации 'случайности'...")
    random_hash = run_chaotic_system(total_time=5)
    print("Полученный результат (SHA-256 хеш от смешанных данных):")
    print(random_hash)
