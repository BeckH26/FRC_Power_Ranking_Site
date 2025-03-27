import os

def run_script(script_name):
    try:
        print(f"Running {script_name}")
        os.system(f"python {script_name}")
        print(f"Finished running {script_name}.\n")
    except Exception as e:
        print(f"Error while running {script_name}: {e}")

def main():
    run_script("calculate.py")
    run_script("rankingPoints.py")
    run_script("predict.py")

    print("Data up to date")

if __name__ == "__main__":
    main()
