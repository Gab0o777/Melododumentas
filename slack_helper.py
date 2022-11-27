import os
import slack
from pathlib import Path
from dotenv import load_dotenv
from utils import getUnixTimestamp

# Literals
APPLICATION_TERM = "{application:"
THREAD_TS = "thread_ts"
MESSAGES_KEY = "messages"
BLOCKS_KEY = "blocks"
ELEMENTS_KEY = "elements"

load_dotenv(dotenv_path=Path(".") / '.env')
SLACK_TOKEN = os.environ['SLACK_TOKEN']

class SlackHelper:

    def __init__(self):
        self.client = slack.WebClient(token=SLACK_TOKEN)

    def writeMessageInChannel(self, channel, text):
        self.client.chat_postMessage(channel=channel, text=text)

    def getAlertsInRange(self, channel, date1, date2):
        """ Retrieves and formats triggered alerts in channel.

        Attributes:
            channel: channel_id to get messages from
            date1: initial date
            date2: final date
        """
        alerts = []

        # Getting channel messages in date range
        history = self.getChannelHistory(channel, date1, date2)

        # Check if it is a triggered alert for each message in channel
        for message in history.get(MESSAGES_KEY):
            alert = {}
            for block in message.get(BLOCKS_KEY):
                for element in block.get(ELEMENTS_KEY):
                    text = self.getTextFromMessageElement(element)
                    appdata = self.getApplicationFromMessage(text)

                    # If message is a triggered alert
                    if appdata.get("appname") != "":

                        alert["app"] = appdata.get("appname")
                        alert["reason"] = appdata.get("reason")

            # If message has thread
            if message.get(THREAD_TS) != None:
                thread_id = message.get(THREAD_TS)

                # Retrieve thread messages from slack
                thread_messages = self.getMessageReplies(channel, thread_id)

                users = {}
                for thread in thread_messages:
                    user_id = thread.get("user")
                    user_info = {}

                    # Retrieving user from thread message
                    if users.get(user_id) != None:
                        user_info = users.get(user_id)
                    else:
                        user_info = self.getUserProfile(user_id)
                        users[user_id] = user_info

                    thread["user"] = {
                        "name": user_info.get("real_name"),
                        "email": user_info.get("email"),
                        "picture": user_info.get("image_24"),
                    }

                    # Retrieves file url for each attachment in thread message
                    if (thread.get("files") != None):
                        files_list = []

                        for attachment in thread.get("files"):
                            file = self.getAttachment(attachment.get("id"))
                            files_list.append(file.get("url_private_download"))

                        thread["files"] = files_list
                               

                # First message in threads is parent message so it is removed in threads
                alert["threads"] = thread_messages[1:]


            if (alert.get("app") != None):
                alerts.append(alert)

        return alerts

    def getAttachment(self, attachment_id): 
        """ Returns file information for given id.

        Attributes:
            attachment_id: slack file id to get info of
        """
        return self.client.api_call(
            'files.info',
            params={
                'token': SLACK_TOKEN,
                'file': attachment_id
            },
        ).get('file')

    def getChannelHistory(self, channel, date1, date2):
        """Retrieves channel message history in date range from slack.

        Attributes:
            channel: channel_id to get messages from
            date1: initial date
            date2: final date
        """

        # Slack needs unix timestamp
        initial_date = getUnixTimestamp(date1)
        final_date = getUnixTimestamp(date2)

        return self.client.api_call(
            "conversations.history",
            params={
                "channel": channel,
                "include_all_metadata": True,
                "oldest": initial_date,
                "latest": final_date,
            },
        )

    def getMessageReplies(self, channel, thread_id):
        """ Retrieves messages from thread.

        Attributes
            channel: channel_id to get messages from
            thread_id: id of thread
        """
        return self.client.api_call(
            'conversations.replies', 
            params={ 
                'channel': channel,
                'ts': thread_id
            }
        ).get("messages")

    def getUserProfile(self, user):
        """ Retrieves user information.

        Attributes:
            user: user_id to get info of
        """
        return self.client.api_call(
            'users.profile.get', 
                params={ 
                    'user': user
                }
            ).get('profile', None)

    def getTextFromMessageElement(self, element):

        # Message text can be in root or in root.elements.text
        text = element.get("text")

        if text == None:
            text = element.get(ELEMENTS_KEY)[0].get("text")
        return text
    
    def getApplicationFromMessage(self, text):
        """ Returns the application name and triggered alert's reason
            if Opsgenie message is detected in text.

        Attributes:
            text: string to parse
        """
        app = {"appname": "", "reason": ""}

        if (text == None):
            return app

        if APPLICATION_TERM in text:
            splitted = text.split("}")
            for term in splitted:
                if APPLICATION_TERM in term:
                    app["appname"] = (
                        term.replace(APPLICATION_TERM, "")
                        .replace("-", " ")
                        .replace("  ", "")
                        .strip()
                        .capitalize()
                    )

                if term.startswith("#"):
                    app["reason"] = (
                        term.split(": ")[1].replace("{", "").replace(":", " ")
                    )

        return app