# CODE adapted from: https://www.fullstackpython.com/blog/build-first-slack-bot-python.html

import os
import time
import re
import signal
import atexit
from slackclient import SlackClient

slack_token = '...'

# instantiate Slack client
slack_client = SlackClient(slack_token)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
should_quit = False

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
EXAMPLE_COMMAND = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
DEFAULT_CHANNEL = 'project-almostjosh'
GREETINGS = ['hi', 'hello', 'hey', 'heya', 'howdy', 'bonjour', 'buenos dias', 'hola']

def post_message(message_text, channel = None):
    return slack_client.api_call(
        "chat.postMessage",
        channel=channel or DEFAULT_CHANNEL,
        text=message_text,
        as_user=True
    )

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(EXAMPLE_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(EXAMPLE_COMMAND):
        response = "I'll be able to \"{}\" just as soon as you code it!".format(command)
    elif command.startswith('simulate error'):
        print("Simulating error!")
        post_message("Got it! Crashing Hard! Standard exit message should still be sent.")
        raise RuntimeError("Error!")
    elif any(word in command.lower() for word in GREETINGS):
        response = "{} to you!".format(command)

    # Sends the response back to the channel
    post_message(response or default_response)

def signal_handler(signal, frame):
    global should_quit
    print('Interrupt captured!')
    should_quit = True

def handle_any_exit():
    print("In atexit handler")

    # These are probably dangerous calls in an exit handler, as they require connection, etc
    slack_client.api_call(
        'users.setPresence',
        presence='away'
    )

    post_message('Hasta La Vista!')

    print("atexit handler done")

signal.signal(signal.SIGINT, signal_handler)

atexit.register(handle_any_exit)

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        slack_client.api_call(
            'users.setPresence',
            presence='auto'
        )
        res = post_message('Bot is up!')

        while not should_quit:
            message = slack_client.rtm_read()
            if message:
                print("Recieved Message: {}".format(message))
                command, channel = parse_bot_commands(message)
                # print("Received message in {}".format(channel))
                print("Command: {}".format(command))
                if command:
                    command = command.lower()
                    handle_command(command, channel)

            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
