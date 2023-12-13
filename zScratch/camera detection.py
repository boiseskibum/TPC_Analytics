import cv2

# This function tries to open a video capture with the given index.
# If successful, it releases the capture and returns True; otherwise False.
def check_camera(index):
#    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
    cap = cv2.VideoCapture(index, cv2.CAP_MSMF)
    print(f'    cap returned value is: {cap}')
    if cap is None or not cap.isOpened():
        return False
    cap.release()
    return True

# Check the first 10 indices.
camera_indices = [i for i in range(10) if check_camera(i)]

print("Connected camera indices:", camera_indices)
