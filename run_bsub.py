#!/usr/bin/env python3
import subprocess
import os

def get_input(prompt, default, cast_func=str, allow_zero=False):
    while True:
        val = input(f"{prompt} [{default}]: ").strip()
        if not val:
            return default
        try:
            value = cast_func(val)
            if not allow_zero and cast_func == int and value <= 0:
                print("Please enter a positive number or press Enter to use the default.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please try again.")

def main():
    print("=== bsub submission helper ===")

    num_cores = get_input("Number of cores", 1, int)
    mem_gb = get_input("Memory per core (GB)", 8, int)
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
