#!/usr/bin/env python3
import subprocess
import os

MAX_CORES = 32        # Maximum number of cores
MAX_MEM_GB = 64       # Maximum memory per core in GB

def get_input(prompt, default, cast_func=str, allow_zero=False, max_value=None):
    while True:
        val = input(f"{prompt} [{default}]: ").strip()
        if not val:
            return default
        try:
            value = cast_func(val)
            if cast_func == int:
                if not allow_zero and value <= 0:
                    print("Please enter a positive number or press Enter to use the default.")
                    continue
                if max_value is not None and value > max_value:
                    print(f"Maximum allowed value is {max_value}.")
                    continue
            return value
        except ValueError:
            print("Invalid input. Please try again.")

def main():
    print("=== bsub submission helper ===")

    num_cores = get_input("Number of cores", 1, int, max_value=MAX_CORES)
    mem_gb = get_input("Memory per core (GB)", 8, int, max_value=MAX_MEM_GB)
    timeout_hours = get_input("Timeout (hours, 0 for unlimited)", 8, int, allow_zero=True)
    command = input("Command to run [xterm]: ").strip() or "xterm"

    cwd = os.getcwd()
    time_str = "" if timeout_hours == 0 else f"-W {timeout_hours}:00"

    bsub_cmd = f"bsub -cwd {cwd} -n {num_cores} -R 'rusage[mem={mem_gb*1024}]' {time_str} {command}"
    print(f"\nGenerated bsub command:\n{bsub_cmd}")

    confirm = input("\nPress Enter to submit, or type 'n' to cancel: ").strip().lower()
    if confirm in ["n", "no"]:
        print("Job submission canceled.")
    else:
        subprocess.run(bsub_cmd, shell=True)

if __name__ == "__main__":
    main()
