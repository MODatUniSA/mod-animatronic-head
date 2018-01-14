import types
import logging
import asyncio
import functools

class CallbackManager:
    """ Allows classes to define the callbacks that can be triggered in that class
        Creating with cbm = CallbackManager(['thing_happened'], an_object) will leave
        cbm responding to add_thing_happened_callback(), trigger_thing_happened_callback().
        an_object will respond to trigger_thing_happened_callback().
    """

    def __init__(self, callback_list, for_instance=None):
        """ Accepts a list of callbacks that this class should allow to be triggered.
            Creates dynamic methods on this instance for each callback name in the list.
            If for_instance is provided, delegate add_callback methods will be added to the instance
        """

        logger_name = '{}_callback_manager'.format(type(for_instance).__name__.lower())
        self._logger = logging.getLogger(logger_name)
        self._callback_list = callback_list
        self._for_instance = for_instance
        self._loop = asyncio.get_event_loop()
        self._callbacks = { name: [] for name in callback_list }
        self._create_all_callback_methods()

    # FUNCTION CREATION - Creates the dynamic functions and adds to this class and the caller
    # =========================================================================
    def _create_callback_methods(self, callback_name):
        # TEMPLATE FUNCTIONS - Used to generate callback functions
        def _add_callback(self, to_call):
            self._logger.debug("Adding callback for {}".format(callback_name))

            if self._check_callable(to_call):
                self._callbacks[callback_name].append(to_call)

        def _trigger_callback(self, *args, **kwargs):
            self._logger.debug("Triggering callback for {}".format(callback_name))

            for to_call in self._callbacks[callback_name]:
                wrapped_call = functools.partial(to_call, *args, **kwargs)
                self._loop.call_soon(wrapped_call)
                # to_call(*args, **kwargs)

        # Create add_callback method on this instance and delegate on caller (if provided)
        add_cb_name = "add_{}_callback".format(callback_name)
        setattr(self, add_cb_name, types.MethodType(_add_callback, self))
        if self._for_instance is not None:
            setattr(self._for_instance, add_cb_name, getattr(self, add_cb_name))

        # Create trigger_callback method
        trigger_cb_name = "trigger_{}_callback".format(callback_name)
        setattr(self, trigger_cb_name, types.MethodType(_trigger_callback, self))

    def _create_all_callback_methods(self):
        """ For each callback name in the list, create the add and trigger methods on this instance
        """

        for callback_name in self._callback_list:
            self._create_callback_methods(callback_name)

    def _check_callable(self, to_call):
        """ Checks whether to_call is a valid callable
        """

        if not callable(to_call):
            self._logger.error("Error! Variable passed is not callable! Ignoring.")
            return False

        return True
