import subprocess
import re
import pexpect
from pathlib import Path
import os
from helix.types import GHELIX, RHELIX

class Instance:
    def __init__(self, config_path=None, port=None, verbose=True):
        self.config_path = config_path
        self.port = port
        self.instance_id = None

        self.verbose = verbose
        self.process_line = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        self.helix_dir = Path(os.path.dirname(os.path.curdir)).resolve()
        os.makedirs(os.path.join(self.helix_dir, self.config_path), exist_ok=True)

    def deploy(self):
        if self.verbose: print(f"{GHELIX} Deploying Helix instance")
        cmd = ['helix', 'deploy']
        if self.config_path:
            cmd.extend(['--path', self.config_path])
        if self.port:
            cmd.extend(['--port', str(self.port)])

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            text=True
        )

        output = []

        for line in process.stdout:
            line = self.process_line.sub('', line)
            output.append(line.strip())
            if self.verbose: print(line.strip())

        process.wait()

        if "error" in "\n".join(output).lower():
            raise Exception(f"{RHELIX} Failed to deploy Helix instance")

        self.instance_id = [out for out in output if out.startswith("Instance ID:")][0].split("Instance ID: ")[1].split(" (running)")[0]

        if self.verbose: print(f"{GHELIX} Deployed Helix instance: {self.instance_id}")

        return output
    
    def redeploy(self):
        if self.verbose: print(f"{GHELIX} Redeploying Helix instance: {self.instance_id}")
        cmd = ['helix', 'redeploy', '--path', self.config_path, self.instance_id]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            text=True
        )

        output = []

        for line in process.stdout:
            line = self.process_line.sub('', line)
            output.append(line.strip())
            if self.verbose: print(line.strip())

        process.wait()

        if "error" in "\n".join(output).lower():
            raise Exception(f"Failed to redeploy Helix instance")

        return output

    def start(self):
        if self.verbose: print(f"{GHELIX} Starting Helix instance: {self.instance_id}")
        cmd = ['helix', 'start', self.instance_id]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            text=True
        )

        output = []

        for line in process.stdout:
            line = self.process_line.sub('', line)
            output.append(line.strip())
            if self.verbose: print(line.strip())

        process.wait()

        if "error" in "\n".join(output).lower():
            raise Exception(f"{RHELIX} Failed to start Helix instance")

        return output

    def stop(self):
        if self.verbose: print(f"{GHELIX} Stopping Helix instance: {self.instance_id}")
        process = subprocess.Popen(
            ['helix', 'stop', self.instance_id],
            stdout=subprocess.PIPE,
            text=True
        )

        output = []

        for line in process.stdout:
            line = self.process_line.sub('', line)
            output.append(line.strip())
            if self.verbose: print(line.strip())

        process.wait()

        if "error" in "\n".join(output).lower():
            raise Exception(f"{RHELIX} Failed to stop Helix instance")

        return output

    def delete(self):
        if self.verbose: print(f"{GHELIX} Deleting Helix instance: {self.instance_id}")
        process = pexpect.spawn(
            ' '.join(['helix', 'delete', self.instance_id]),
        )

        process.expect("Are you sure you want to delete", timeout=10)
        process.sendline("y")
        process.expect(pexpect.EOF, timeout=10)

        output = process.before.decode('utf-8').split('\n')

        for line in output[1:]:
            line = self.process_line.sub('', line)
            if self.verbose: print(line)

        if "error" in "\n".join(output).lower():
            raise Exception(f"{RHELIX} Failed to delete Helix instance")

        return output

    def status(self):
        if self.verbose: print(f"{GHELIX} Helix instance status:")
        cmd = ['helix', 'instances']
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            text=True
        )

        output = []

        for line in process.stdout:
            line = self.process_line.sub('', line)
            output.append(line.strip())
            if self.verbose: print(line.strip())

        process.wait()

        if "error" in "\n".join(output).lower():
            raise Exception(f"{RHELIX} Failed to get Helix instance status")

        return output