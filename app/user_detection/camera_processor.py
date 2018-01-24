""" Takes in a camera feed and uses Open CV cascades to find faces in the frames
"""

import asyncio
import numpy as np
import cv2
import time
import logging
import functools

from libs.callback_handling.callback_manager import CallbackManager
from libs.config.device_config import DeviceConfig

class CameraProcessor:
    def __init__(self):
        self._logger = logging.getLogger('camera_processor')
        self._cbm = CallbackManager(['face_detected'], self)
        self._loop = asyncio.get_event_loop()
        config = DeviceConfig.Instance()
        user_detection_config = config.options['USER_DETECTION']
        self._frame_period_seconds = user_detection_config.getfloat('FRAME_PERIOD_SECONDS')
        self._camera_id = user_detection_config.getint('CAMERA_ID')

        self._camera = None
        self._should_quit = False
        self._running_routine = None

        # Cascades for detecting features in images
        self._face_front_cascade = cv2.CascadeClassifier('resources/cascades/haarcascade_frontalface_default.xml')
        self._face_profile_cascade = cv2.CascadeClassifier('resources/cascades/haarcascade_profileface.xml')
        self._eye_cascade = cv2.CascadeClassifier('resources/cascades/haarcascade_eye.xml')

    def run(self):
        """ Starts taking a feed from the camera and triggers the face detected callback whenever a face is found
        """

        self._camera = cv2.VideoCapture(self._camera_id)
        self._running_routine = self._loop.run_in_executor(None, self._process_camera_feed)

    def stop(self):
        """ Stops processing the camera and performs any required cleanup
        """

        self._running_routine.cancel()
        self._should_quit = True
        self._camera.release()
        cv2.destroyAllWindows()

    # CAMERA PROCESSING
    # =========================================================================

    def _process_camera_feed(self):
        """ Processes frames from the camera, looking for faces
        """

        while not self._should_quit:
            captured, frame = self._camera.read()

            if captured:
                # TODO: Set image size in ImageToServoPositionConverter on first frame captured

                grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                results = self._process_frame(grayscale_frame)

                self._logger.info("Faces Found: {}".format(len(results)))

                if len(results) > 0:
                    self._cbm.trigger_face_detected_callback(results)

            # REVISE: Should our wait time be based on how long the frame processing took?
            # Takes at least 2x as long to process if we can't find any front on faces and need to look for profile faces
            time.sleep(self._frame_period_seconds)

            # HACK: Not actually processing any keypresses,
            #       but the frame capture loop won't iterate unless this waitKey command is present
            k = cv2.waitKey(30) & 0xff

    def _process_frame(self, frame):
        """ Processes a single image/frame from the camera
            If we find a front face, we try to find eyes in it. We don't try to
            find eyes in profile faces as we're much less likely to do so.
        """

        ret = []
        faces = self._find_front_faces(frame)

        if len(faces) > 0:
            for face_coordinates in faces:
                ret.append({
                    'face' : face_coordinates,
                    'eyes' : self._find_eyes_in_face(frame, face_coordinates)
                })
        else:
            faces = self._find_profile_faces(frame)
            for face_coordinates in faces:
                ret.append({'face' : face_coordinates, 'eyes' : []})

        return ret

    # FIXME: cv2.imshow can only be called from the main thread, so we can't just call this from our
    #           BG thread running the frame processing. Need to pass data between BG and main thread via a Queue.
    #           Would require an async loop running in the foreground thread to process the queue
    def _display_frame(self, frame, faces, eyes):
        """ Shows the captured frame with rectangles around any faces and eyes found
        """

        for face_index, (x,y,w,h) in enumerate(faces):
            # Draw rectangle around each face
            self._logger.debug("Drawing face: {}".format(face_index))
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

            # Draw rects around eyes found in this face
            face_region = frame[y:y+h, x:x+w]
            if len(eyes[face_index]) > 0:
                self._logger.debug("Drawing eyes for face: {}".format(face_index))
                for (ex,ey,ew,eh) in eyes[face_index]:
                    cv2.rectangle(face_region,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

        cv2.imshow('Frame', frame)

    # FEATURE DETECTION
    # =========================================================================

    def _find_front_faces(self, image):
        """ Find any fronton faces in the image
        """
        return self._face_front_cascade.detectMultiScale(image, 1.3, 5)

    def _find_profile_faces(self, image):
        """ Finds side on faces in image
        """

        return self._face_profile_cascade.detectMultiScale(image, 1.3, 5)

    def _find_eyes_in_face(self, image, face_coordinates):
        """ Find any eyes within the face corodinates of the image. Used to find eyes in fronton faces
        """

        (x,y,w,h) = face_coordinates
        image_face_region = image[y:y+h, x:x+w]
        return self._find_eyes(image_face_region)

    def _find_eyes(self, image):
        return self._eye_cascade.detectMultiScale(image, 1.3, 5)
