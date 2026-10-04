import os
import subprocess
from core.constants import BASE_DIR

try:
    import psutil
except ImportError:
    psutil = None

def get_gpu_usage():
    try:
        cmd = ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=1)
        if res.returncode == 0 and res.stdout.strip():
            val = res.stdout.strip().split("\n")[0]
            return f"{int(val)}%"
    except Exception:
        pass
    return "N/A"

def get_system_metrics():
    if not psutil:
        return {"cpu": "sem psutil", "gpu": "N/A", "ram": "sem psutil", "disk": "sem psutil"}

    cpu = f"{int(psutil.cpu_percent(interval=1.0))}%"
    ram = f"{int(psutil.virtual_memory().percent)}%"
    disk_drive = os.path.splitdrive(BASE_DIR)[0] or "C:"
    disk = f"{int(psutil.disk_usage(disk_drive).percent)}%"
    gpu = get_gpu_usage()

    return {"cpu": cpu, "gpu": gpu, "ram": ram, "disk": disk}