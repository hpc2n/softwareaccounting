"""
Fetches Metrics from nvidia-smi command

Config options:

sams.sampler.NvidiaSMI:
    # in seconds
    sampler_interval: 100

    # Path to nvidia-smi command
    nvidia_smi_command: /usr/bin/nvidia-smi

    # Environment variable with indexs (","-separated) of GPUs
    gpu_index_environment: SLURM_JOB_GPUS

Output:
{
    gpu_index: {
        power_draw: 0,
        power_limit: 0,
        clocks_applications_memory: 0,
        clocks_applications_graphics: 0,
        clocks_current_graphics: 0,
        clocks_current_sm: 0,
        utilization_gpu: 0,
        utilization_memory: 0 
    }
}

"""
import sams.base
import os
import re

import logging
logger = logging.getLogger(__name__)

import subprocess
import threading
import queue

COMMAND='''%s --query-gpu=index,power.draw,power.limit,clocks.applications.memory,clocks.applications.graphics,clocks.current.graphics,clocks.current.sm,utilization.gpu,utilization.memory --format=csv,nounits -l %d -i %s'''

class SMI(threading.Thread):
    def __init__(self,gpus=[],t=10,command="/usr/bin/nvidia-smi"):
        super().__init__()
        self.gpus = gpus
        self.t = t
        self.command = command
        self.queue = queue.Queue()
        self.stop_event = threading.Event()        

    def run(self):
        command = COMMAND % (self.command,self.t,",".join(self.gpus))
        try:
            process = subprocess.Popen(command.split(" "),stdout=subprocess.PIPE)
            head = process.stdout.readline()
            headers = map(lambda h: re.sub(r' \[[^\]]+\]$','',h).replace('.','_'),head.decode('ascii').replace('\n','').split(", "))
            headers = list(headers)
            for line in iter(process.stdout.readline,b''):
                if self.stopped():
                    break
                items = line.decode('ascii').replace('\n','').split(", ")                
                out = {}
                for h in headers:
                    out[h] = items[0]
                    items = items[1:]
                self.queue.put(out)
        except Exception as e:
            logger.exception(e)
        process.kill()
        logger.debug("Exiting...")
    
    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

class Sampler(sams.base.Sampler):
    def __init__(self,id,outQueue,config):
        super().__init__(id,outQueue,config)
        self.processes = {}        
        self.sampler_interval = self.config.get([self.id,"sampler_interval"],60)
        self.gpu_index_environment = self.config.get([self.id,"gpu_index_environment"],'SLURM_JOB_GPUS')
        self.nvidia_smi_command = self.config.get([self.id,"nvidia_smi_command"],'/usr/bin/nvidia-smi')

        self.smi = None
        if self.gpu_index_environment in os.environ:
            self.gpustr = os.environ[self.gpu_index_environment]            
            if self.gpustr:
                gpus=self.gpustr.split(",")
                self.smi = SMI(gpus=gpus,t=self.sampler_interval,command=self.nvidia_smi_command)
                self.smi.start()

    def do_sample(self):
        return self.smi and not self.smi.queue.empty()

    def sample(self):
        logger.debug("sample()")
        while not self.smi.queue.empty():
            data = self.smi.queue.get()
            logger.debug(data)
            index = data['index']
            del data['index']
            self.store({
                index: data
            })

    def final_data(self):
        if self.smi:
            self.smi.stop()
            self.smi.join()
        return {}
