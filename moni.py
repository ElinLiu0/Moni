# Author: Elin
# Date: 2024-04-25 10:31:02
# Last Modified by:   Elin
# Last Modified time: 2024-04-25 10:31:02

import psutil as pt
from typing import List
from pynvml import *
import asciichartpy
import time
from rich.console import Console
from rich.table import Table
from datetime import datetime

class Moni:
    def __init__(self):
        nvmlInit()
        self.console = Console()
        self.cpu_name: str = open("/proc/cpuinfo").readlines()[4].split(":")[1].strip()
        self.threads: int = pt.cpu_count()
        self.mem_size: int = pt.virtual_memory().total // (1024 ** 3) + 1
        self.gpus: int = nvmlDeviceGetCount()
        self.gpus_names: List[str] = [nvmlDeviceGetName(nvmlDeviceGetHandleByIndex(i)) for i in range(self.gpus)]
        self.gpus_mem_size: List[int] = [
            nvmlDeviceGetMemoryInfo(nvmlDeviceGetHandleByIndex(i)).total // (1024 ** 3) for i in range(self.gpus)
        ]

    def __call__(self):
        while True:
            self._flush_data()
            self.console.clear()
            self._render()
            time.sleep(1)

    def _render(self):
        self.console.print(f"Moni v{self.__version__()} by {self.__author__()}" + " " * 10 + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.console.print(f"CPU: {self.cpu_name}, {self.threads} THREADS")
        self.console.print(f"MEM: {self.mem_size} GB, {self.used_mem} GB has been used now")
        self.console.print("CPU Usage:")
        self.console.print(asciichartpy.plot(self.cpu_percent, {'height': 5}))
        for i in range(self.gpus):
            self.console.print(f"GPU {i}: {self.gpus_names[i]} ({self.gpus_mem_size[i]} GB), {self.gpus_mem_usage[i]} GB VRAM been used, CORE Temp {self.gpus_temperature[i]} °C")
            self.console.print(asciichartpy.plot(self.gpus_volatile_usage[i], {'height': 5}))
        self._plot_process_table()

    def _plot_process_table(self):
        process_table = Table()
        fields = ["PID", "USER", "NAME", "STATUS", "CPU_USAGE", "MEM_USAGE", "COMMAND"]
        process_table.add_column("PID")
        process_table.add_column("USER")
        process_table.add_column("NAME")
        process_table.add_column("STATUS")
        process_table.add_column("CPU_USAGE")
        process_table.add_column("MEM_USAGE")
        process_table.add_column("COMMAND")
        running_process_count:int = 0
        sleeping_process_count:int = 0
        stopped_process_count:int = 0
        zombie_process_count:int = 0
        self.process_list = sorted(self.process_list, key=lambda x: (x.cpu_percent(),x.memory_percent()), reverse=True)
        for p in self.process_list:
            status = p.status()
            if status == "running":
                running_process_count += 1
            elif status == "sleeping":
                sleeping_process_count += 1
            elif status == "stopped":
                stopped_process_count += 1
            elif status == "zombie":
                zombie_process_count += 1
        for p in self.process_list[:10]:
            try:
                process_table.add_row(str(p.pid), p.username(), p.name(), p.status(), str(round(p.cpu_percent(), 2)) + "%", str(round(p.memory_percent(), 2)) + "%", p.cmdline()[0] if p.cmdline() else "")
            except pt.NoSuchProcess:
                continue
            except pt.AccessDenied:
                continue
            except pt.ZombieProcess:
                continue
        self.console.print(f"Total Process: {len(self.process_list)}, Running: {running_process_count}, Sleeping: {sleeping_process_count}, Stopped: {stopped_process_count}, Zombie: {zombie_process_count}")
        self.console.print(f"Shows TOP10 high utilized process:")
        self.console.print(process_table)

    def _flush_data(self):
        self.used_mem: int = pt.virtual_memory().used // (1024 ** 3) + 1
        self.cpu_percent: List[float] = [pt.cpu_percent(interval=1e-1) for _ in range(self.threads)]
        self.gpus_mem_usage: List[float] = [
            round(nvmlDeviceGetMemoryInfo(nvmlDeviceGetHandleByIndex(i)).used // (1024 ** 3),2) for i in range(self.gpus)
        ]
        self.gpus_temperature: List[int] = [
            nvmlDeviceGetTemperature(nvmlDeviceGetHandleByIndex(i), NVML_TEMPERATURE_GPU) for i in range(self.gpus)
        ]
        self.gpus_volatile_usage: List[List[int]] = [
            [int(nvmlDeviceGetUtilizationRates(nvmlDeviceGetHandleByIndex(i)).gpu) for _ in range(50)] for i in range(self.gpus)
        ]
        try:
            self.process_list: List[pt.Process] = list(pt.process_iter())
        except:
            self.process_list: List[pt.Process] = []

    def __version__(self):
        return "0.0.1"
    def __author__(self):
        return "Elin"
if __name__ == "__main__":
    moni = Moni()
    moni()
