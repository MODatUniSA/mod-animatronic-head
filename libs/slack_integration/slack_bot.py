""" Slack bot for posting status messages to slack and processing messages from slack
    Makes use of the real time messaging API so we can show the current code status via the bot's slack status
    Runs self in a background thread so syncronous api calls don't block. There are async clients, but they don't seem to be as nice to use.
"""

import asyncio
import logging
import time

from slackclient import SlackClient

from libs.slack_integration.slack_message_parser import SlackMessageParser
from libs.config.device_config import DeviceConfig

# TODO: Need to ensure we have a connection before attempting to make API calls
# TODO: Probably want to push errors onto a queue so callers can tell if code running in executor has crashed.

class SlackBot:
    def __init__(self, token):
        self._logger = logging.getLogger("slack_bot")
        self._client = SlackClient(token)
        self._bot_id = None
        self._should_quit = False
        self._running_routine = None
        self._message_parser = None
        self._loop = asyncio.get_event_loop()

        config = DeviceConfig.Instance()
        slack_config = config.options['SLACK']
        self._default_channel = slack_config['DEFAULT_CHANNEL']
        self._rtm_read_delay = slack_config.getfloat('RTM_READ_DELAY')

        self._logger.debug("Slack Bot Initted! Default channel: %s. Reading every %s seconds", self._default_channel, self._rtm_read_delay)

    def run(self):
        self._logger.info("Slack Bot Starting")
        self._running_routine = self._loop.run_in_executor(None, self._perform_run)

    def stop(self):
        self._logger.info("Slack bot stopping")
        self._post_message("OK, shutting down.")
        self._set_presence('away')
        self._should_quit = True

    # INTERNAL METHODS
    # =========================================================================

    def _post_message(self, message_text, channel = None):
        """ Posts a message to slack and returns the API response
        """

        return self._client.api_call(
            "chat.postMessage",
            channel=channel or self._default_channel,
            text=message_text,
            as_user=True
        )

    def _set_presence(self, presence):
        """ Sets the bot's presence
            Possible values are away and auto
            Bot should set itself as away when exiting
            Status is generally derived from websocket connection to the RTM API,
            but it seems more reliable to set it manually.
        """

        return self._client.api_call(
            'users.setPresence',
            presence=presence
        )

    def _perform_run(self):
        """ Executes _run, wrapped in a try/except so errors aren't just squashed automatically by asyncio
        """

        # IDEA: Should we store the number of exceptions we hit here and automatically crash after a threshold hit?
        #           Could save us spamming the logs with a single repeated error
        while not self._should_quit:
            try:
                self._run()
            except RuntimeError:
                self._logger.error("Error caught in SlackBot executor", exc_info=True)

            time.sleep(1)


    def _run(self):
        self._logger.info("Slack Bot Running")
        if not self._connect():
            return

        self._bot_id = self._client.api_call("auth.test")["user_id"]
        self._message_parser = SlackMessageParser(self._bot_id)
        self._logger.debug("Bot connected with id %s", self._bot_id)
        self._set_presence('auto')
        self._post_message("I'm up!")

        while not self._should_quit:
            message = self._client.rtm_read()
            if message:
                self._logger.debug("Received Message: {}".format(message))
                command, channel = self._message_parser.parse_message(message)
                if command:
                    self._logger.info("Command: %s", command)
                    command = command.lower()
                    self._handle_command(command, channel)

            time.sleep(self._rtm_read_delay)

    def _connect(self):
        connected = self._client.rtm_connect(with_team_state=False)
        if not connected:
            self._logger.error("Unable to connect to slack")

        return connected

    def _handle_command(self, command, channel):
        """
            Executes bot command if the command is known
        """
        response = "I just want to do my own thing..."

        # Finds and executes the given command, filling in response
        greeting = self._message_parser.parse_greeting(command)
        if greeting:
            response = "{} to you!".format(greeting)
        elif self._message_parser.is_status_command(command):
            # IDEA: Would be ideal to know whether all components of the code (experience controller and user detector) are running correctly. This really only tests that the slack integration code is running. But it's a start.
            response = "I'm up and running!"
        elif command.startswith('simulate error'):
            self._logger.warning("Simulating error!", extra={'stack': True})
            self._post_message("Got it! Crashing!")
            raise RuntimeError("Simulated Error!")

        # Sends the response back to the channel
        self._post_message(response)
