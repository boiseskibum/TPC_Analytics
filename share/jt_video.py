import sys, subprocess, time
import cv2
from PyQt6.QtCore import QThread
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

try:
    from . import jt_util as util
    from . import jt_config as jtc
except ImportError:
    import jt_util as util
    import jt_config as jtc

log = util.jt_logging()


# External Camera Count - since we are not interested in built-in cameras on MacOS, this routine determines the number
# of connected cameras.  I suspect this code is very finicky to changes to the OS so be fore warned.  The plan is to
# see if there is 1 or more and default to recording if so.  It should be implemented to do no harm if it shows
# a number less than this so program carefully on this!!!


def external_camera_count():
    count = 0
    models = []
    if sys.platform == "win32":
        # Windows-specific command (requires pywin32)
        log.info(f'Code not implemented to determine win32 cameras: {sys.platform}')

        pass

    elif sys.platform == "darwin":
        # macOS-specific command
        result = subprocess.run(["system_profiler", "SPCameraDataType"], capture_output=True, text=True)

        if result.stdout is not None:
#            print(f' Stdout: {result.stdout}')

            # break into list of strings
            lines = result.stdout.splitlines()
            # Using list comprehension to filter out empty or whitespace-only strings
            lines = [line for line in lines if line.strip()]
#            print(f'lines: {lines}')

            last_string = ''
            #get count and model names
            for string in lines:
                if "Model ID" in string and "FaceTime" not in string:
                    count += 1
                    model = f'{last_string.strip()} {string.strip()}'
                    models.append(model)
                last_string = string

            log.debug(f'External Camera count: {count}, Models: {models}')


    else:
        log.error(f'sys.platform does not return known platform: {sys.platform}')

    return count, models


def resize_with_aspect_ratio(img, target_width):
    height, width = img.shape[:2]
#    print(f"      w:{width}  h:{height}")
    aspect_ratio = target_width / width
    target_height = int(height * aspect_ratio)
    return cv2.resize(img, (target_width, target_height))

class JT_Video(QThread):
    def __init__(self, config_obj, video_widget = None):
        super().__init__()
        self._video_widget = video_widget
        self.config_obj = config_obj
        self._is_running = False         # used internally
        self._frames = []        # holds a group of frames that were saved, typically to play back or save later

        self.camera_index = 0           # which camera to connect to, 1 or 2
        self.display_video = True       # this toggles whether or not to display/show video while capturing
        self.save_frames = False        #this is to keep frames for saving to disk at later time, saves them in numpy array
        self.display_width = 200        #number of pixels wide for display
        self.rotate  = True             #assumes that it is portrait mode
        self.max_record_time = 15       #this is seconds
        self.error_msg = ""
        self.error = False

    #this is equivalent to starting the video camera
    def run(self):
        self._is_running = True
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.error_msg = (f"cv2.VideoCapture failed to open camera index: {self.camera_index}")
            self.error = True
            log.error(self.error_msg)
            return
        else:
            log.debug('"cv2.VideoCapture opened camera index: {self.camera_index}')

        self.w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.actual_fps = cap.get(cv2.CAP_PROP_FPS)
        self.fourcc = 'avc1'

        log.debug(f"PRE cap properties - w: {self.w}, h: {self.h}, fps: {self.actual_fps} cam_index: {self.camera_index}")

        # Set the desired frame rate (FPS)
        desired_fps = 30  # Set your desired FPS here
        cap.set(cv2.CAP_PROP_FPS, desired_fps)

        self._frames = []

        start_time = time.time()
        while cap.isOpened() and self._is_running:
            ret, frame = cap.read()
            if ret:

                # Check if the desired time has elapsed
                current_time = time.time()
                elapsed_time = current_time - start_time
                if elapsed_time >= self.max_record_time:
                    log.info(f"MAX_RECORD_TIME has been exceeded: {self.max_record_time} secs")
                    break

                # Convert the frame to RGB format and resize it
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                #this is HACK, where index is 1 is trying to deal with Iphone as camera,
                if self.camera_index == 2:   #this basically disables it for now
                    rotated_frame = rgb_frame
                else:
                    if self.rotate == True:
                        rotated_frame = cv2.rotate(rgb_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

                resized_frame = resize_with_aspect_ratio(rotated_frame, self.display_width)

                # save frames for later
                if self.save_frames == True:
                    self._frames.append(frame)

                if self.display_video == True:
                    # Display the frame in the video widget
                    image = QImage(
                        resized_frame,
                        resized_frame.shape[1],
                        resized_frame.shape[0],
                        QImage.Format.Format_RGB888,
                    )
                    pixmap = QPixmap.fromImage(image)
                    self._video_widget.setPixmap(pixmap)

#                if cv2.waitKey(1) & 0xFF == ord("q"):
#                    break

            else:
                break

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self._is_running = False

    def validate_camera(self):
        cap = cv2.VideoCapture(self.camera_index)
        if cap.isOpened():
            log.debug(f'Valid camera_index: {self.camera_index}')
            return True
        else:
            log.debug(f'Invalid camera_index: {self.camera_index}')
            return False


    def camera_offline(self):

        # Load the image from disk
        image_name = 'camera_offline.png'
        image = self.config_obj.validate_path_and_return_QImage(image_name)

        if image is not None:
            image = image.scaledToWidth(self.display_width)
            pixmap = QPixmap.fromImage(image)
            if self._video_widget:
                self._video_widget.setPixmap(pixmap)
        else:
            pixmap = None
            log.error(f'Could not find image_path for: {image_name}')

    # save video to file.  Filename must end in .mp4
    def save_video(self, filename):

        video_writer_tuple = (self.h, self.w)  # flips height and width
#        video_writer_tuple = (self.w, self.h)
        fourcc = cv2.VideoWriter_fourcc(*self.fourcc)

        print(f"   saving video- w: {self.w}, h: {self.h}, tuple: {video_writer_tuple}, actual_fps: {self.actual_fps}, num_frames: {len(self._frames)}, fourcc_str: {self.fourcc}, fourcc: {fourcc}, filename: {filename}")

        if len(self._frames) < 1:
            print(f"WARNING: No frames to save, aborting save operation!   Make sure: self.save_frames = True ")
        else:
            out = cv2.VideoWriter(filename, fourcc, self.actual_fps, video_writer_tuple)
            for frame in self._frames:
                if self.rotate == True:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
                out.write(frame)
            out.release()
            print(f"Video saved:  {filename}")


###################################################################
if __name__ == "__main__":

    class MainWindow(QWidget):
        def __init__(self, config_obj):
            super().__init__()

            self.num_cameras = 2   # 1 or 2
            self.setGeometry(100, 100, 800, 600)  # (x, y, width, height)
            self.start_button = QPushButton("Start")
            self.stop_button = QPushButton("Stop")
            self.save_button = QPushButton("Save")
            self.swap_button = QPushButton("Swap Cameras")
            self.config_obj = config_obj


            layout = QVBoxLayout()
            layout.addWidget(self.start_button)
            layout.addWidget(self.stop_button)
            layout.addWidget(self.save_button)
            layout.addWidget(self.swap_button)

            # the following are for "video buttons" to be shown
            self.video_label1 = QLabel()
            self.video_label2 = QLabel()

            horizontal_layout = QHBoxLayout()
            horizontal_layout.addWidget(self.video_label1)
            horizontal_layout.addWidget(self.video_label2)

            layout.addLayout(horizontal_layout)

            self.setLayout(layout)

            #start videos
            self.video1 = JT_Video(config_obj, self.video_label1)
            self.video1.validate_camera()
            if self.num_cameras == 2:
                self.video2 = JT_Video(config_obj, self.video_label2)
                self.video2.camera_index = 1
                self.video2.validate_camera()

            self.start_button.clicked.connect(self.start_video)
            self.stop_button.clicked.connect(self.stop_video)
            self.save_button.clicked.connect(self.save_video)
            self.swap_button.clicked.connect(self.swap_video)

        def start_video(self):
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.video1.start()
            if self.num_cameras == 2:
                self.video2.start()

        def stop_video(self):
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.video1.stop()
            if self.num_cameras == 2:
                self.video2.stop()

        def save_video(self):
            self.video1.save_video('jt_video_test1.mp4')
            if self.num_cameras == 2:
                self.video2.save_video('jt_video_test2.mp4')

        def swap_video(self):

            if self.video1.camera_index == 1:
                self.video1.camera_index = 0
                self.video2.camera_index = 1
            else:
                self.video1.camera_index = 1
                self.video2.camera_index = 0

    config_obj = jtc.JT_Config('taylor performance', None)
    log.set_logging_level("DEBUG")
    external_camera_count()
    app = QApplication(sys.argv)

    window = MainWindow(config_obj)
    window.show()
    sys.exit(app.exec())
