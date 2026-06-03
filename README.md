# Лабораторна робота №1 — Parallel Tasks

Тема: засоби створення та керування потоками в паралельних мультипоточних програмах.

Проєкт містить послідовні та паралельні реалізації CPU-bound, memory-bound та I/O-bound задач:

- Monte Carlo обчислення числа pi;
- факторизація великих чисел;
- підрахунок простих чисел у діапазоні;
- транспонування великої матриці, включно з `10000 x 10000`;
- рекурсивний підрахунок слів у текстових файлах.

## Використана тестова платформа

Фінальні експерименти для звіту рекомендується виконувати на Linux-сервері:

```text
CPU: 2 x Intel Xeon E5-2697A v4
RAM: 128 GB
OS: Linux
```

Сервер має більше обчислювальних ресурсів, тому краще підходить для дослідження впливу кількості worker-ів на CPU-bound задачі. Quick benchmark також можна запускати на звичайному ПК для перевірки працездатності.

## Встановлення

### Windows

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux / Proxmox / Debian

Якщо `pip` або `venv` відсутні:

```bash
apt update
apt install -y python3-pip python3-venv python3-dev build-essential
```

Після цього:

```bash
cd ~/lab1_parallel_tasks
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Окремі запуски

```bash
python src/main.py pi --iterations 1000000 --workers 4 --executor process
python src/main.py primes --limit 200000 --workers 4 --executor process
python src/main.py factorization --numbers 30 --workers 4 --executor process
python src/main.py transpose --size 10000 --workers 4
python src/main.py generate-texts --files 1000 --words-per-file 250
python src/main.py wordcount --workers 8
```

## Benchmark

Швидкий benchmark для звичайного ПК:

```bash
python run_experiments.py
```

Розширений benchmark для Linux-сервера:

```bash
export MPLBACKEND=Agg
python run_server_experiments.py
```

Після запуску автоматично створюються:

```text
results/benchmark.csv
results/plots/execution_time_by_workers.png
results/plots/speedup_by_workers.png
results/plots/execution_time_cpu.png
results/plots/speedup_cpu.png
results/plots/execution_time_memory_io.png
results/plots/speedup_memory_io.png
results/plots/execution_time_by_workers_log.png
results/plots/speedup_by_workers_log.png
```

## Примітки щодо Python

Для CPU-bound задач використовується `ProcessPoolExecutor`, оскільки в CPython є GIL. Для I/O-bound задач використовується `ThreadPoolExecutor`, оскільки потоки можуть перекривати очікування операцій файлової системи. Для memory-bound задач використовується NumPy, а прискорення обмежується пропускною здатністю пам'яті.
