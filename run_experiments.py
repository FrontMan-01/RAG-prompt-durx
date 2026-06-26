import subprocess
import os
import sys

def run_cmd(cmd):
    print(f"\n========================================================")
    print(f"Executing: {sys.executable} {cmd}")
    print(f"========================================================")
    res = subprocess.run([sys.executable, cmd])
    if res.returncode != 0:
        print(f"Error: {cmd} failed with exit code {res.returncode}")
        sys.exit(res.returncode)

def main():
    scripts = [
        "eval_pipeline.py",
        "eval_pipeline_defense_1.py",
        "eval_pipeline_defense_2.py",
        "eval_pipeline_defense_3.py",
        "compile_comparison.py"
    ]
    for script in scripts:
        if not os.path.exists(script):
            print(f"Error: Script {script} not found in workspace!")
            sys.exit(1)
        run_cmd(script)
    print("\nAll experiments run and compiled successfully!")

if __name__ == "__main__":
    main()
