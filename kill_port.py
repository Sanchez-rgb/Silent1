import os
import signal
import subprocess

result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
lines = result.stdout.split('\n')

for line in lines:
    if ':8000' in line and 'LISTENING' in line:
        parts = line.split()
        if len(parts) >= 5:
            pid = parts[-1]
            try:
                print(f"Stopping process {pid}...")
                os.kill(int(pid), signal.SIGTERM)
                print(f"Process {pid} terminated")
            except Exception as e:
                print(f"Failed to stop process {pid}: {e}")

print("Done")
