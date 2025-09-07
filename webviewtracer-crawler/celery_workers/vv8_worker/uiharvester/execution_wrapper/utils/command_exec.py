import subprocess

def run_command(command):
    """Run a shell command and return output and error."""
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
        stdout, stderr = process.communicate()  # Capture output and error
        if process.returncode == 0:
            return stdout.strip()  # Return the output if successful
        else:
            # print(stdout,stderr)
            return None  # Return None if the command failed
    except Exception as e:
        print(f"Error: Command failed. {e}")
        return f"Error: Command failed. {e}"
def frun_command(command):
    """Run a shell command asynchronously without waiting for it to complete."""
    try:
        process = subprocess.Popen(command, text=True)

        # You can capture the PID if needed
        return process.pid
    except Exception as e:
        return f"Error: Command failed. {e}"
def try_command(command):
    """Run a shell command and return output and error."""
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        
        # Wait for the process to complete and capture output and error
        stdout, stderr = process.communicate()
        
        # Decode the output and error to strings
        output = stdout.decode('utf-8').strip()
        error = stderr.decode('utf-8').strip()
        
        if process.returncode == 0:
            return output
        else:
            return f"Error: {error}"
    
    except Exception as e:
        f"Error: Command failed. {e}"
        return f"Exception: {e}"