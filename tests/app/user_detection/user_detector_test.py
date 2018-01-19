from asyncio.events import TimerHandle
from unittest.mock import call

import pytest

from app.user_detection.user_detector import UserDetector
from app.user_detection.camera_processor import CameraProcessor
from libs.callback_handling.callback_manager import CallbackManager

def mock_camera_processor(mocker):
    processor = mocker.MagicMock(spec=CameraProcessor)
    processor._cbm = CallbackManager(['face_detected'], processor)
    return processor

class TestRun:
    def test_run_called_on_camera_processor(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud.run()
        cp.run.assert_called()

class TestStop:
    def test_delayed_callbacks_cancelled(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        mocker.patch.object(ud, '_cancel_delayed_callbacks')
        ud.stop()
        ud._cancel_delayed_callbacks.assert_called()

    def test_stop_called_on_camera_processor(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud.stop()
        cp.stop.assert_called()

class TestHandleFaceFoundCallback:
    def test_face_detected_count_incremented(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._face_detected_count = 0
        ud._handle_face_found(None, None)
        assert ud._face_detected_count == 1

    def test_face_detected_count_at_max(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._max_face_detected_count = 2
        ud._face_detected_count = ud._max_face_detected_count
        ud._handle_face_found(None, None)
        assert ud._face_detected_count == ud._max_face_detected_count

    def _face_detected_threshold_shared_setup(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._face_detected_count = 1
        ud._activate_at_face_detected_count = 2
        return ud

    def test_face_detected_count_over_threshold_user_present(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        ud._user_present = False

        ud._handle_face_found(None, None)
        assert ud._user_present

    def test_face_detected_count_over_threshold_callback_triggered(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        mocker.patch.object(ud._cbm, 'trigger_first_user_entered_callback')
        ud._user_present = False

        ud._handle_face_found(None, None)
        ud._cbm.trigger_first_user_entered_callback.assert_called()

    def test_face_detected_count_over_threshold_user_already_present(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        mocker.patch.object(ud._cbm, 'trigger_first_user_entered_callback')
        ud._user_present = True

        ud._handle_face_found(None, None)
        ud._cbm.trigger_first_user_entered_callback.assert_not_called()

class TestHandleFaceAbsentCallback:
    def test_face_detected_count_decremented(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._face_detected_count = 1

        ud._handle_face_absent()
        assert ud._face_detected_count == 0

    def test_face_detected_count_at_min(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._face_detected_count = 0

        ud._handle_face_absent()
        assert ud._face_detected_count == 0

    def _face_detected_threshold_shared_setup(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._face_detected_count = 1
        ud._deactivate_at_face_detected_count = 0
        return ud

    def test_threshold_reached_user_present(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        ud._user_present = True

        ud._handle_face_absent()
        assert ud._user_present is False

    def test_threshold_reached_user_present_callback_triggered(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        ud._user_present = True
        mocker.patch.object(ud._cbm, 'trigger_all_users_left_callback')

        ud._handle_face_absent()
        ud._cbm.trigger_all_users_left_callback.assert_called()

    def test_threshold_reaced_user_absent_callback_not_triggered(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        ud._user_present = False
        mocker.patch.object(ud._cbm, 'trigger_all_users_left_callback')

        ud._handle_face_absent()
        ud._cbm.trigger_all_users_left_callback.assert_not_called()

    def test_user_present_threshold_not_reached_callback_queued(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        ud._face_detected_count = 2
        ud._user_present = True
        mocker.patch.object(ud, '_queue_delayed_users_left_trigger')

        ud._handle_face_absent()
        ud._queue_delayed_users_left_trigger.assert_called()

    def test_user_present_threshold_reached_callback_not_queued(self, mocker):
        ud = self._face_detected_threshold_shared_setup(mocker)
        ud._face_detected_count = 1
        ud._user_present = True
        mocker.patch.object(ud, '_queue_delayed_users_left_trigger')

        ud._handle_face_absent()
        ud._queue_delayed_users_left_trigger.assert_not_called()

class TestQueueDelayedUsersLeftTrigger:
    def test_callback_scheduled(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)

        ud._queue_delayed_users_left_trigger()
        assert type(ud._delayed_all_users_left_trigger) == TimerHandle

    def test_callback_scheduled_with(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._user_absent_timeout = 4
        mocker.patch.object(ud._loop, 'call_later')

        ud._queue_delayed_users_left_trigger()
        ud._loop.call_later.assert_called_with(ud._user_absent_timeout, ud._handle_face_absent)

class TestCancelDelayedCallbacks:
    def test_cancel_called(self, mocker):
        cp = mock_camera_processor(mocker)
        ud = UserDetector(cp)
        ud._delayed_all_users_left_trigger = mocker.MagicMock()

        ud._cancel_delayed_callbacks()
        ud._delayed_all_users_left_trigger.cancel.assert_called()
