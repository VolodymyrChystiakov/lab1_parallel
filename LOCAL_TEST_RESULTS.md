# Local and server test results

## Windows quick checks

The project was checked on Windows in a virtual environment.

Examples of successful individual runs:

```text
pi=3.14189200
workers=4; executor=process; elapsed_ms=1954.41

prime_count=17984
workers=4; executor=process; elapsed_ms=2030.13

numbers=30; total_factors=151
workers=4; executor=process; elapsed_ms=2252.84

matrix=2000x2000; checksum=756
workers=4; elapsed_ms=11.69

words=37500; directory=...\\data\\generated_texts
workers=8; elapsed_ms=80.07
```

The required matrix size was also checked:

```text
matrix=10000x10000; checksum=689
workers=4; elapsed_ms=482.77

matrix=10000x10000; checksum=689
workers=4; elapsed_ms=389.98
```

## Linux server environment

Final performance experiments are intended to be run on a stronger Linux server:

```text
CPU: 2 x Intel Xeon E5-2697A v4
RAM: 128 GB
OS: Debian 13
```

Recommended final command:

```bash
source .venv/bin/activate
export MPLBACKEND=Agg
python run_server_experiments.py
python create_report.py
```
