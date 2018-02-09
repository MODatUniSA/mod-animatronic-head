""" Parses messages received by SlackBot
"""

import re

class SlackMessageParser:
    MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
    GREETINGS = ['hi', 'hello', 'hey', 'heya', 'howdy', 'bonjour', 'buenos dias', 'hola']

    def __init__(self, bot_id):
        self._bot_id = bot_id

    def parse_message(self, slack_events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                user_id, message = type(self).parse_direct_mention(event["text"])
                if user_id == self._bot_id:
                    return message, event["channel"]
        return None, None

    @classmethod
    def parse_direct_mention(cls, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(cls.MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    @classmethod
    def is_status_command(cls, command):
        return 'status' in command.lower()

    @classmethod
    def parse_greeting(cls, command):
        for phrase in cls.GREETINGS:
            if phrase in command.lower():
                return phrase
