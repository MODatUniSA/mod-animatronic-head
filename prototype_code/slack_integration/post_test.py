from slackclient import SlackClient

slack_token = '...'
sc = SlackClient(slack_token)

sc.api_call(
  "chat.postMessage",
  channel="#project-almostjosh",
  text="Test from Python with Bot token! :tada:"
)
