import logging
from utils.command_exec import run_command

class FridaExecutor:
    def __init__(self, package_name, frida_script, log_file):
        self.package_name = package_name
        self.frida_script = frida_script
        self.logger = logging.getLogger('FridaExecutor')
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def run_frida_script(self):
        """Run the specified Frida script on the application."""
        self.logger.info(f"Running Frida script on package: {self.package_name}")
        output, error = run_command(f"frida -U -n {self.package_name} -l {self.frida_script}")
        if output:
            self.logger.info(f"Frida script output: {output}")
        if error:
            self.logger.error(f"Error while running Frida script: {error}")
