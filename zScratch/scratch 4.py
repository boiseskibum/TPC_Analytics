import subprocess
import sys

def list_cameras():
    if sys.platform == "win32":
        # Windows-specific command (requires pywin32)
        pass
    elif sys.platform == "darwin":
        # macOS-specific command
        result = subprocess.run(["system_profiler", "SPCameraDataType"], capture_output=True, text=True)
        return result.stdout
    elif sys.platform == "linux" or sys.platform == "linux2":
        # Linux-specific command (requires v4l2-ctl)
        result = subprocess.run(["v4l2-ctl", "--list-devices"], capture_output=True, text=True)
        return result.stdout
    else:
        return "Unsupported OS"

camera_info = list_cameras()

print(camera_info)
