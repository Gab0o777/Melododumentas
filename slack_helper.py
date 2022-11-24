import slack
from utils import getUnixTimestamp

# Literals
APPLICATION_TERM = "{application:"
THREAD_TS = "thread_ts"
MESSAGES_KEY = "messages"
BLOCKS_KEY = "blocks"
ELEMENTS_KEY = "elements"


class SlackHelper:
    def __init__(self, token):
        self.token = token
        self.client = slack.WebClient(token=token)

    def getAlertsInRange(self, channel, date1, date2):
        alerts = []
        history = self.getChannelHistory(channel, date1, date2)

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

                thread_messages = self.getMessageReplies(channel, thread_id)

                users = {}
                for thread in thread_messages:
                    user_id = thread.get("user")
                    user_info = {}

                    if users.get(user_id) != None:
                        user_info = users.get(user_id)
                    else:
                        user_info = self.getUserProfile(user_id)
                        users[user_id] = user_info

                    thread["user"] = {
                        "name": user_info.get("realname"),
                        "email": user_info.get("email"),
                        "picture": user_info.get("image_24"),
                    }

                    if (thread.get("files") != None):
                        files_list = []

                        if (len(thread.get("files")) == 1):
                            for attachment in thread.get("files"):
                                file = self.getAttachment(attachment.get("id"))
                                print(file)
                                files_list.append(file.get("thumb_800"))
                        thread["files"] = files_list
                               

                # First message in threads is parent message so it is removed in threads
                alert["threads"] = thread_messages[1:]

            if (alert.get("app") != None):
                alerts.append(alert)


        return alerts

    def getAttachment(self, attachment_id): 
        return self.client.api_call(
            "files.info",
            params={
                "token": self.token,
                "file": attachment_id
            },
        ).get("file")

    def getChannelHistory(self, channel, date1, date2):
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
        return self.client.api_call(
            "conversations.replies", params={"channel": channel, "ts": thread_id}
        ).get("messages")

    def getUserProfile(self, user):
        return self.client.api_call("users.profile.get", params={"user": user}).get(
            "profile", None
        )

    def getTextFromMessageElement(self, element):
        text = element.get("text")
        if text == None:
            text = element.get(ELEMENTS_KEY)[0].get("text")
        return text
    
    def getApplicationFromMessage(self, text):
        app = {"appname": "", "reason": ""}

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