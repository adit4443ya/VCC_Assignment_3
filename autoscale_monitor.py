import psutil
import subprocess
import time

# Configuration variables
THRESHOLD = 75.0          # CPU usage percentage to trigger scaling
MAX_SIZE = 5              # Maximum number of instances in the MIG
ZONE = "us-central1-a"    # Change as needed for your MIG
MIG_NAME = "my-instance-group"
COOLDOWN = 60             # Cooldown period in seconds after a scaling event

def get_current_mig_size():
    """Retrieve the current target size of the Managed Instance Group."""
    try:
        result = subprocess.check_output([
            "gcloud", "compute", "instance-groups", "managed", "describe", MIG_NAME,
            "--zone", ZONE,
            "--format=value(targetSize)"
        ])
        return int(result.decode("utf-8").strip())
    except subprocess.CalledProcessError as e:
        print("Error retrieving MIG size:", e)
        return None

def resize_mig(new_size):
    """Resize the Managed Instance Group to the new size using gcloud CLI."""
    try:
        print(f"Resizing MIG {MIG_NAME} to {new_size} instances...")
        subprocess.check_call([
            "gcloud", "compute", "instance-groups", "managed", "resize", MIG_NAME,
            "--size", str(new_size),
            "--zone", ZONE
        ])
        print("Resize command executed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error executing resize command:", e)

def monitor_and_scale():
    while True:
        # Measure CPU usage over an interval of 10 seconds
        cpu_usage = psutil.cpu_percent(interval=10)
        print(f"Current CPU Usage: {cpu_usage}%")

        if cpu_usage > THRESHOLD:
            print("Threshold exceeded! Checking current MIG size...")
            current_size = get_current_mig_size()
            if current_size is None:
                print("Skipping scaling due to error retrieving MIG size.")
            elif current_size >= MAX_SIZE:
                print(f"MIG is already at maximum size ({MAX_SIZE}). No scaling performed.")
            else:
                new_size = current_size + 1
                print(f"Scaling from {current_size} to {new_size} instances.")
                resize_mig(new_size)
                print(f"Cooling down for {COOLDOWN} seconds to allow scaling to take effect.")
                time.sleep(COOLDOWN)
        else:
            print("CPU usage is within limits. No scaling needed.")

        # Sleep before the next check (adjust as needed)
        time.sleep(10)

if __name__ == "__main__":
    monitor_and_scale()
