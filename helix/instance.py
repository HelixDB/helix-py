import subprocess
import re
from pathlib import Path
import os
from helix.types import GHELIX, RHELIX
import sys
import atexit

class Instance:
    """
    A class for managing Helix instances.

    Args:
        config_path (str): The path to the configuration file.
        port (int): The port to use for the Helix server.
        redeploy (bool): Whether to redeploy the Helix instance or not.
        verbose (bool): Whether to print verbose output or not.
    """
    def __init__(self, config_path: str="helixdb-cfg", port: int=6969, redeploy: bool=False, verbose: bool=False):
        self.config_path = config_path
        self.port = str(port)
        self.instance_id = None
        self.short_id = None
        self.port_ids = {}
        self.ids_running = {}
        self.short_ids = {}

        self.verbose = verbose
        self.process_line = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # remove color codes

        cmd = ['helix', 'status']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

        output = []
        if process.stdout is not None:
            for line in process.stdout:
                line = self.process_line.sub('', line)
                output.append(line.strip())
                if self.verbose: print(line.strip(), file=sys.stderr)

        process.wait()

        if len(output) > 1 and output[0][4:].startswith("Instance ID"):
            ports = []
            ids = []
            running = []
            s_ids = []
            for line in output:
                if line[4:].startswith("Instance ID: "):
                    ids.append(str(line[4:].removeprefix("Instance ID: ").removesuffix(" (running)").removesuffix(" (not running)")))
                    running.append(line.split(" ")[-1] == "(running)")
                elif line.startswith("└── Short ID: "):
                    s_ids.append(str(line.removeprefix("└── Short ID: ")))
                elif line.startswith("└── Port: "):
                    ports.append(str(line.removeprefix("└── Port: ")))

            self.port_ids = dict(zip(ports, ids))
            self.ids_running = dict(zip(ids, running))
            self.short_ids = dict(zip(ports, s_ids))

            if self.verbose: print(f"{GHELIX} Found existing ports: {self.port_ids}", file=sys.stderr)
            if self.verbose: print(f"{GHELIX} Found existing instance IDs: {self.ids_running}", file=sys.stderr)
            if self.verbose: print(f"{GHELIX} Found existing short IDs: {self.short_ids}", file=sys.stderr)

        if self.port in self.port_ids:
            self.instance_id = self.port_ids.get(self.port, None)
            self.short_id = self.short_ids.get(self.port, None)

        self.helix_dir = Path(os.path.dirname(os.path.curdir)).resolve()
        os.makedirs(os.path.join(self.helix_dir, self.config_path), exist_ok=True)

        self.deploy(redeploy=redeploy)

    def deploy(self, redeploy: bool=False, remote: bool=False):
        """
        Deploy the Helix instance.

        Args:
            redeploy (bool): Whether to redeploy the Helix instance or not.
        """
        if self.short_id and self.instance_id:
            if self.ids_running.get(self.instance_id, False):
                if redeploy:
                    if self.verbose: print(f"{GHELIX} Redeploying running instance", file=sys.stderr)
                    self.stop()
                else:
                    if self.verbose: print(f"{GHELIX} Instance already running", file=sys.stderr)
                    return
            else:
                if self.verbose: print(f"{GHELIX} Instance not running, redeploying", file=sys.stderr)
                redeploy = True
        else:
            if self.verbose: print(f"{GHELIX} No instance found, deploying", file=sys.stderr)
            redeploy = False

        cmd = ['helix', 'deploy']
        if self.config_path: cmd.extend(['--path', self.config_path])
        if self.port: cmd.extend(['--port', self.port])
        if redeploy and self.short_id: cmd.extend(['--cluster', self.short_id])
        if remote: cmd.extend(['--remote'])

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

        self.instance_id = [out for out in output if out[4:].startswith("Instance ID:")][0][4:] \
            .removeprefix("Instance ID: ") \
            .removesuffix(" (running)") \
            .removesuffix(" (not running)")

        self.short_id = [out for out in output if out.startswith("└── Short ID: ")][0] \
            .removeprefix("└── Short ID: ") \
            .strip(" ").strip("\n")

        self.ids_running[self.instance_id] = True
        self.port_ids[self.port] = self.instance_id

        atexit.register(self.stop)

        if self.verbose:
            if redeploy:
                print(f"{GHELIX} Redeployed Helix instance: {self.instance_id}", file=sys.stderr)
            else:
                print(f"{GHELIX} Deployed Helix instance: {self.instance_id}", file=sys.stderr)

        return '\n'.join(output)

    def stop(self):
        """
        Stop the Helix instance.
        """
        if not self.instance_id or self.instance_id not in self.ids_running:
            raise Exception(f"{RHELIX} Instance ID not found")

        if not self.ids_running.get(self.instance_id, False):
            raise Exception(f"{RHELIX} Instance is not running")

        if self.verbose: print(f"{GHELIX} Stopping Helix instance ({self.short_id}): {self.instance_id}", file=sys.stderr)
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
        """
        Delete the Helix instance.
        """
        if not self.instance_id or self.instance_id not in self.ids_running:
            raise Exception(f"{RHELIX} Instance ID not found")

        if self.verbose: print(f"{GHELIX} Deleting Helix instance ({self.short_id}): {self.instance_id}", file=sys.stderr)
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
        self.short_ids.pop(self.port, None)
        self.instance_id = None
        self.short_id = None

        atexit.unregister(self.stop)

        return '\n'.join(output)

    def status(self):
        """
        Get the status of the Helix instance.
        """
        if self.verbose: print(f"{GHELIX} Helix instances status:", file=sys.stderr)
        cmd = ['helix', 'status']
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

        if len(output) > 1 and output[0][4:].startswith("Instance ID"):
            ports = []
            ids = []
            running = []
            s_ids = []
            for line in output:
                if line[4:].startswith("Instance ID: "):
                    ids.append(line[4:].removeprefix("Instance ID: ").removesuffix(" (running)").removesuffix(" (not running)"))
                    running.append(line.split(" ")[-1] == "(running)")
                elif line.startswith("└── Short ID: "):
                    s_ids.append(str(line.removeprefix("└── Short ID: ")))
                elif line.startswith("└── Port: "):
                    ports.append(str(line.removeprefix("└── Port: ")))
            self.port_ids = dict(zip(ports, ids))
            self.ids_running = dict(zip(ids, running))
            self.short_ids = dict(zip(ports, s_ids))
        if self.verbose: print(f"{GHELIX} Ports: {self.port_ids}", file=sys.stderr)
        if self.verbose: print(f"{GHELIX} Instances Running: {self.ids_running}", file=sys.stderr)
        if self.verbose: print(f"{GHELIX} Short IDs: {self.short_ids}", file=sys.stderr)

        return '\n'.join(output)

