""" Takes in a camera feed and uses Open CV cascades to find faces in the frames
    dlib correlation tracking adapted from https://github.com/gdiepen/face-recognition/blob/master/track%20multiple%20faces/demo%20-%20track%20multiple%20faces.py
"""

import asyncio
import time
import logging
import functools
from collections import OrderedDict

import numpy as np
import cv2
import dlib

from libs.helpers.math_helpers import center_point_ints
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
        self._locate_eyes = user_detection_config.getboolean('LOCATE_EYES')
        self._face_detection_frame_interval = user_detection_config.getint('FACE_DETECTION_FRAME_INTERVAL')
        self._min_tracking_quality = user_detection_config.getint('MIN_TRACKING_QUALITY')

        self._camera = None
        self._should_quit = False
        self._running_routine = None

        # Displaying frames for debugging
        # FIXME: See note on _display_frame()
        self._display_frames = False
        self._font = cv2.FONT_HERSHEY_SIMPLEX


        self._frame_count = 0
        self._current_face_id = 0
        self._currently_tracked_count = 0
        self._face_trackers = OrderedDict()

        # Cascades for detecting features in images
        self._face_front_cascade = cv2.CascadeClassifier('resources/cascades/haarcascade_frontalface_default.xml')
        self._face_profile_cascade = cv2.CascadeClassifier('resources/cascades/haarcascade_profileface.xml')
        self._eye_cascade = cv2.CascadeClassifier('resources/cascades/haarcascade_eye.xml')

    def run(self):
        """ Starts taking a feed from the camera and triggers the face detected callback whenever a face is found
        """

        self._camera = cv2.VideoCapture(self._camera_id)
        # Fetching and processing the camera feed is a heavy, blocking operation, so we run it in a separate thread
        # IDEA: Consider using a ProcessPool to run this in a separate process, which should mean we can offload it to a separate core
        self._running_routine = self._loop.run_in_executor(None, self._process_camera_feed)
        # self._process_camera_feed()


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
            # Scale image down to decrease processing time
            # TODO: Add resize % to config
            frame = cv2.resize(frame,(0,0),fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            self._frame_count += 1

            if captured:
                grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                self._process_frame(grayscale_frame)

                if len(self._face_trackers) != self._currently_tracked_count:
                    self._currently_tracked_count = len(self._face_trackers)
                    self._logger.info("Tracking %i Faces", self._currently_tracked_count)

                if len(self._face_trackers) > 0:
                    self._cbm.trigger_face_detected_callback(self._face_trackers, frame)

            # REVISE: Should our wait time be based on how long the frame processing took?
            # Takes at least 2x as long to process if we can't find any front on faces and need to look for profile faces
            # REVISE: Probably don't want any artificial delay between frames now that we're using correlation tracking each
            # frame and only cascade feature detection every x frames.
            time.sleep(self._frame_period_seconds)

            # HACK: Not actually processing any keypresses,
            #       but the frame capture loop won't iterate unless this waitKey command is present
            k = cv2.waitKey(30) & 0xff

    def _process_frame(self, frame):
        """ Processes a single image/frame from the camera
            If we find a front face, we try to find eyes in it. We don't try to
            find eyes in profile faces as we're much less likely to do so.
        """

        self._update_trackers(frame)

        if self._should_detect_faces_on_this_frame():
            self._detect_faces(frame)

        if self._display_frames:
            self._display_frame(frame)

    def _should_detect_faces_on_this_frame(self):
        """ We only detect faces when frame count is a multiple of our frame count interval (e.g. every 10 frames)
        """

        return (self._frame_count % self._face_detection_frame_interval) == 0

    # FIXME: cv2.imshow can only be called from the main thread, so we can't just call this from our
    #           BG thread running the frame processing. Need to pass data between BG and main thread via a Queue.
    #           Would require an async loop running in the foreground thread to process the queue
    def _display_frame(self, frame):
        """ Shows the captured frame with rectangles around any faces and eyes found
        """

        for face_index, tracker in self._face_trackers.items():
            tracked_position = tracker.get_position()

            x = int(tracked_position.left())
            y = int(tracked_position.top())
            w = int(tracked_position.width())
            h = int(tracked_position.height())

            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

            tracked_center = center_point_ints(x,y,w,h)
            cv2.putText(frame,str(face_index),tracked_center.tuple, self._font, 1, (200,255,155), 2, cv2.LINE_AA)

        cv2.imshow('Frame', frame)

    # IDEA: Consider periodically clearing out all existing trackers regadless of quality
    #       Otherwise, if unchanging background ever considered face, it won't be dropped due to always high corrolation
    def _update_trackers(self, frame):
        """ Updates all existing dlub correlation trackers
            Destroys any with insufficient quality
        """

        to_delete = []
        for face_id, tracker in self._face_trackers.items():
            tracking_quality = tracker.update(frame)

            if tracking_quality < self._min_tracking_quality:
                to_delete.append( face_id )

        for face_id in to_delete:
            self._logger.debug("Removing face_id {} from list of trackers".format(face_id))
            self._face_trackers.pop( face_id , None )

    # FEATURE DETECTION
    # =========================================================================

    def _detect_faces(self, frame):
        """ Face detection using cascades. CPU heavy operation, so we don't do this every frame.
        """

        faces = self._find_front_faces(frame)

        if len(faces) == 0:
            faces = self._find_profile_faces(frame)

        for(x,y,w,h) in faces:
            face_id = self._find_matching_tracker_face_id(x,y,w,h)

            if face_id is None:
                self._create_tracker(frame, x,y,w,h)


    def _find_matching_tracker_face_id(self, x, y, w, h):
        """ Finds an existing tracker for a face matched with these coordinates
            Considered a match if the center point of the found face is within the tracker bounds,
            and vice versa
        """

        face_center = center_point_ints(x,y,w,h)

        for face_id, tracker in self._face_trackers.items():
            tracked_position =  tracker.get_position()
            t_x = int(tracked_position.left())
            t_y = int(tracked_position.top())
            t_w = int(tracked_position.width())
            t_h = int(tracked_position.height())

            tracked_center = center_point_ints(t_x,t_y,t_w,t_h)

            if ( ( t_x <= face_center.x    <= (t_x + t_w)) and
                 ( t_y <= face_center.y    <= (t_y + t_h)) and
                 ( x   <= tracked_center.x <= (x   +   w)) and
                 ( y   <= tracked_center.y <= (y   +   h))):
                return  face_id

    def _create_tracker(self, frame, x, y, w, h):
        """ Creates a dlib correlation tracker to track the face in the argument coordinates
        """
        self._logger.debug("Creating new tracker: {}".format(self._current_face_id))

        x = int(x)
        y = int(y)
        w = int(w)
        h = int(h)

        #Create and store the tracker
        tracker = dlib.correlation_tracker()
        tracker.start_track(frame,
                            dlib.rectangle( x-10,
                                            y-20,
                                            x+w+10,
                                            y+h+20))
        self._face_trackers[self._current_face_id] = tracker

        self._current_face_id += 1

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

        if not self._locate_eyes:
            return

        (x,y,w,h) = face_coordinates
        image_face_region = image[y:y+h, x:x+w]
        return self._find_eyes(image_face_region)

    def _find_eyes(self, image):
        return self._eye_cascade.detectMultiScale(image, 1.3, 5)
