import subprocess
import os

# Replace these paths with the paths to your .ino file and the platformio.ini file.
ino_file_path = "/path/to/your/project/project.ino"
platformio_ini_path = "C:/Users/tj10c/OneDrive/Documents/Classes/Senior/Fall 2023/EE 422/TestProjectIO/TestProjectIO/platformio.ini"

# Change the target environment if needed (e.g., "esp32" or "esp8266")
target_env = "esp32"

def upload_code(ino_path, platformio_path, env):
    # Change the current working directory to the project directory
    project_dir = os.path.dirname(ino_path)
    os.chdir(project_dir)

    # Run the PlatformIO command to upload the code
    upload_command = [
        "platformio",
        "--project-dir", project_dir,
        "--environment", env,
        "run", "--target", "upload"
    ]

    try:
        subprocess.run(upload_command, check=True)
        print("Code uploaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading code: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    upload_code(ino_file_path, platformio_ini_path, target_env)
