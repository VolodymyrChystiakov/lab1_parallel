# Linux server commands for Lab 1

Recommended test platform used for the final report:

```text
CPU: 2 x Intel Xeon E5-2697A v4
RAM: 128 GB
OS: Linux
```

## 1. Install Python tools if needed

For Debian/Proxmox:

```bash
apt update
apt install -y python3-pip python3-venv python3-dev build-essential
```

## 2. Create virtual environment

```bash
cd ~/lab1_parallel_tasks
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For headless servers:

```bash
export MPLBACKEND=Agg
```

## 3. Check system information

```bash
lscpu
free -h
python --version
```

## 4. Quick individual checks

```bash
python src/main.py pi --iterations 1000000 --workers 4 --executor process
python src/main.py primes --limit 200000 --workers 4 --executor process
python src/main.py factorization --numbers 30 --workers 4 --executor process
python src/main.py transpose --size 10000 --workers 4
python src/main.py generate-texts --files 1000 --words-per-file 250
python src/main.py wordcount --workers 8
```

## 5. Full server benchmark and report generation

```bash
mkdir -p results

{
  echo "System info:"
  uname -a
  echo
  echo "CPU:"
  lscpu
  echo
  echo "Memory:"
  free -h
  echo
  echo "Python:"
  python --version
  echo
  echo "Server benchmark:"
  python run_server_experiments.py
  echo
  echo "Report generation:"
  python create_report.py
} 2>&1 | tee results/linux_run_log.txt
```

Generated files:

```text
results/benchmark.csv
results/plots/*.png
results/linux_run_log.txt
report/Lab1_Report.docx
```

## 6. Archive results

```bash
tar -czf lab1_results_linux.tar.gz results/ report/Lab1_Report.docx
```
