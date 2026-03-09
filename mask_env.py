# mask_env.py
import os

env_file = ".env"
example_file = ".env.example"

if not os.path.exists(env_file):
    print(f"{env_file} not found. Skipping mask.")
else:
    with open(env_file, "r") as f:
        lines = f.readlines()

    with open(example_file, "w") as f:
        for line in lines:
            if "=" in line and not line.startswith("#"):
                key, _ = line.split("=", 1)
                f.write(f"{key}=******\n")
            else:
                f.write(line)

    print(f"Updated {example_file} with masked keys.")