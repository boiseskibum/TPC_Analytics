import cv2, threading
import time

# the purpose of this class is to create a video frame reader for cv2 where it reads into a buffer in a
# separate thread so that the frames can be processed by the main application.  It is the applications
# responsibility to manage the video_cv2 and buffer
class jt_VideoFrameReader(threading.Thread):
    def __init__(self, video_cv2, lock, buffer, fps):
        super().__init__()
        self.video_cv2 = video_cv2
        self.video_lock = lock
        self.buffer = buffer
        self.running = True
        self.frame_interval = 1.0 / fps  # Calculate frame interval in seconds

    def run(self):
        while self.running:
            if self.buffer.full():
                # If the buffer is full, sleep for the frame interval
                time.sleep(self.frame_interval)
            else:
                with self.video_lock:
                    ret, frame = self.video_cv2.read()
                    if ret:
                        self.buffer.put(frame)
                    else:
                        # this means the video has reached its end
                        break

    def stop(self):
        self.running = False

if __name__ == '__main__':

    from PyQt6.QtWidgets import QApplication, QLabel
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtCore import QTimer
    import sys
    from queue import Queue  # utilized for video frame reader


    class MyApp(QApplication):
        def __init__(self, argv):
            super().__init__(argv)

            self.video1_cv2_lock = threading.Lock()

            file_path = 'jt_video_test1.mp4'
            self.video_cv2 = cv2.VideoCapture(file_path)
            self.frame_buffer = Queue(maxsize=10)  # Adjust size as needed
            self.frame_reader = jt_VideoFrameReader(self.video_cv2, self.video1_cv2_lock, self.frame_buffer, 30)
            self.frame_reader.start()

            self.window = QLabel()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(33)  # 33 ms for 30 fps

            self.window.show()

        def update_frame(self):
            if not self.frame_buffer.empty():
                frame = self.frame_buffer.get()
                #image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888).rgbSwapped()

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w

                q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

#                scaled_pixmap = QPixmap.fromImage(q_image).scaled(self.label_video1.size(), Qt.AspectRatioMode.KeepAspectRatio)
                scaled_pixmap = QPixmap.fromImage(q_image)

#                self.window.setPixmap(QPixmap.fromImage(image))
                self.window.setPixmap(scaled_pixmap)

        def closeEvent(self, event):
            self.frame_reader.stop()
            super().closeEvent(event)


    app = MyApp(sys.argv)
    ret = app.exec()
    sys.exit(ret)
