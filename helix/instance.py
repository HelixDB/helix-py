import subprocess
import re
from pathlib import Path
import os
from helix.types import GHELIX, RHELIX
import sys
import atexit

class Instance:
    def __init__(self, config_path: str="helixdb-cfg", port: int=6969, redeploy: bool=False, verbose: bool=False):
        self.config_path = config_path
        self.port = str(port)
        self.instance_id = None
        self.port_ids = {}
        self.ids_running = {}

        self.verbose = verbose
        self.process_line = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # remove color codes

        cmd = ['helix', 'instances']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        output = []
        if process.stdout is not None:
            for line in process.stdout:
                line = self.process_line.sub('', line)
                output.append(line.strip())
                if self.verbose: print(line.strip(), file=sys.stderr)

        process.wait()

        if len(output) > 1 and output[0].startswith("Instance ID"):
            ports = []
            ids = []
            running = []
            for line in output:
                if line.startswith("Instance ID: "):
                    ids.append(str(line.removeprefix("Instance ID: ").removesuffix(" (running)").removesuffix(" (not running)")))
                    running.append(line.split(" ")[-1] == "(running)")
                elif line.startswith("└── Port: "):
                    ports.append(str(line.removeprefix("└── Port: ")))

            self.port_ids = dict(zip(ports, ids))
            self.ids_running = dict(zip(ids, running))

            if self.verbose: print(f"{GHELIX} Found existing ports: {self.port_ids}", file=sys.stderr)
            if self.verbose: print(f"{GHELIX} Found existing instance IDs: {self.ids_running}", file=sys.stderr)

        if self.port in self.port_ids: self.instance_id = self.port_ids.get(self.port, None)

        self.helix_dir = Path(os.path.dirname(os.path.curdir)).resolve()
        os.makedirs(os.path.join(self.helix_dir, self.config_path), exist_ok=True)

        self.deploy(redeploy=redeploy)

    def deploy(self, redeploy: bool=False):
        if self.instance_id or self.port in self.port_ids:
            if redeploy:
                return self.redeploy()
            if not self.ids_running.get(self.instance_id, False):
                if self.verbose: print(f"{GHELIX} Instance already exists - starting", file=sys.stderr)
                return self.start()
            if self.verbose:
                print(f"{GHELIX} Instance already running", file=sys.stderr)
            return

        if redeploy: raise Exception(f"{RHELIX} Instance not found")

        if self.verbose: print(f"{GHELIX} Deploying Helix instance", file=sys.stderr)

        cmd = ['helix', 'deploy']
        if self.config_path: cmd.extend(['--path', self.config_path])
        if self.port: cmd.extend(['--port', self.port])

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        output = []
        if process.stdout is not None:
            for line in process.stdout:
                line = self.process_line.sub('', line)
                output.append(line.strip())
                if self.verbose: print(line.strip(), file=sys.stderr)

        process.wait()

        if "error" in "\n".join(output).lower():
            if not self.verbose: print("\n".join(output), file=sys.stderr)
            raise Exception(f"{RHELIX} Failed to deploy Helix instance")

        self.instance_id = [out for out in output if out.startswith("Instance ID:")][0] \
            .removeprefix("Instance ID: ") \
            .removesuffix(" (running)") \
            .removesuffix(" (not running)")

        self.ids_running[self.instance_id] = True
        self.port_ids[self.port] = self.instance_id

        atexit.register(self.stop)

        if self.verbose: print(f"{GHELIX} Deployed Helix instance: {self.instance_id}")

        return '\n'.join(output)

    def redeploy(self):
        if not self.instance_id or self.instance_id not in self.ids_running:
            raise Exception(f"{RHELIX} Instance not found")

        if self.ids_running.get(self.instance_id, False):
            self.stop()

        if self.verbose: print(f"{GHELIX} Redeploying Helix instance: {self.instance_id}", file=sys.stderr)
        cmd = ['helix', 'redeploy', '--path', self.config_path, self.instance_id]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        output = []

        output = []
        if process.stdout is not None:
            for line in process.stdout:
                line = self.process_line.sub('', line)
                output.append(line.strip())
                if self.verbose: print(line.strip(), file=sys.stderr)

        process.wait()

        if "error" in "\n".join(output).lower():
            if not self.verbose: print("\n".join(output), file=sys.stderr)
            raise Exception(f"{RHELIX} Failed to redeploy Helix instance")

        self.ids_running[self.instance_id] = True

        return '\n'.join(output)

    def start(self):
        if not self.instance_id or self.instance_id not in self.ids_running:
            raise Exception(f"{RHELIX} Instance not found")

        if self.ids_running.get(self.instance_id, False):
            raise Exception(f"{GHELIX} Instance is already running")

        if self.verbose: print(f"{GHELIX} Starting Helix instance: {self.instance_id}", file=sys.stderr)
        cmd = ['helix', 'start', self.instance_id]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        output = []
        if process.stdout is not None:
            for line in process.stdout:
                line = self.process_line.sub('', line)
                output.append(line.strip())
                if self.verbose: print(line.strip(), file=sys.stderr)

        process.wait()

        if "error" in "\n".join(output).lower():
            if not self.verbose: print("\n".join(output), file=sys.stderr)
            raise Exception(f"{RHELIX} Failed to start Helix instance")

        self.ids_running[self.instance_id] = True

        return '\n'.join(output)

    def stop(self):
        if not self.instance_id or self.instance_id not in self.ids_running:
            raise Exception(f"{RHELIX} Instance ID not found")

        if not self.ids_running.get(self.instance_id, False):
            raise Exception(f"{RHELIX} Instance is not running")

        if self.verbose: print(f"{GHELIX} Stopping Helix instance: {self.instance_id}", file=sys.stderr)
        process = subprocess.Popen(['helix', 'stop', self.instance_id], stdout=subprocess.PIPE, text=True)

        output = []
        if process.stdout is not None:
            for line in process.stdout:
                line = self.process_line.sub('', line)
                output.append(line.strip())
                if self.verbose: print(line.strip(), file=sys.stderr)

        process.wait()

        if "error" in "\n".join(output).lower():
            if not self.verbose: print("\n".join(output), file=sys.stderr)
            raise Exception(f"{RHELIX} Failed to stop Helix instance")

        self.ids_running[self.instance_id] = False

        return '\n'.join(output)

    def delete(self):
        if not self.instance_id or self.instance_id not in self.ids_running:
            raise Exception(f"{RHELIX} Instance ID not found")

        if self.verbose: print(f"{GHELIX} Deleting Helix instance: {self.instance_id}", file=sys.stderr)
        process = subprocess.run(['helix', 'delete', self.instance_id], input="y\n", text=True, capture_output=True)

        output = process.stdout.split('\n')
        output = [self.process_line.sub('', line) for line in output if not line.startswith("Are you sure you want to delete")]

        for line in output:
            if self.verbose: print(line, file=sys.stderr)

        if "error" in "\n".join(output).lower():
            if not self.verbose: print("\n".join(output), file=sys.stderr)
            raise Exception(f"{RHELIX} Failed to delete Helix instance")

        del self.port_ids[self.port]
        del self.ids_running[self.instance_id]
        self.instance_id = None

        atexit.unregister(self.stop)

        return '\n'.join(output)

    def status(self):
        if self.verbose: print(f"{GHELIX} Helix instances status:", file=sys.stderr)
        cmd = ['helix', 'instances']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        output = []

        output = []
        if process.stdout is not None:
            for line in process.stdout:
                line = self.process_line.sub('', line)
                output.append(line.strip())
                if self.verbose: print(line.strip(), file=sys.stderr)

        process.wait()

        if "error" in "\n".join(output).lower():
            if not self.verbose: print("\n".join(output), file=sys.stderr)
            raise Exception(f"{RHELIX} Failed to get Helix instance status")

        if len(output) > 1 and output[0].startswith("Instance ID"):
            ports = []
            ids = []
            running = []
            for line in output:
                if line.startswith("Instance ID: "):
                    ids.append(line.removeprefix("Instance ID: ").removesuffix(" (running)").removesuffix(" (not running)"))
                    running.append(line.split(" ")[-1] == "(running)")
                elif line.startswith("└── Port: "):
                    ports.append(str(line.removeprefix("└── Port: ")))
            self.port_ids = dict(zip(ports, ids))
            self.ids_running = dict(zip(ids, running))
        if self.verbose: print(f"{GHELIX} Ports: {self.port_ids}", file=sys.stderr)
        if self.verbose: print(f"{GHELIX} Instances Running: {self.ids_running}", file=sys.stderr)

        return '\n'.join(output)

