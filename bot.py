from slack_helper import SlackHelper
from reports import Reports
from utils import validateDates
from exceptions import InvalidArgumentNumberException, InvalidParamsFormatException

class BotService():

    def __init__(self):
        self.slackHelper = SlackHelper()
        self.reports = Reports()

    def generateReportInDateRange(self, payload):
        """Creates report from messages in date range for slack channel.

        Attributes:
            payload: contains request information and params
        """
        channel = payload.get('channel_id')
        user = payload.get("user_name", "-")
        try:
            validateDates(payload.get('text'))
            datesArr = payload.get('text').split(' ')

            self.slackHelper.writeMessageInChannel(channel, f"Generating channel report from {datesArr[0]} to {datesArr[1]}... please wait")

            # Getting alerts from channel in given dates range
            alerts = self.slackHelper.getAlertsInRange(channel, datesArr[0], datesArr[1])

            # Generating report with slack input
            self.reports.generate(alerts, datesArr[0], datesArr[1], user)
        except Exception:
            self.slackHelper.writeMessageInChannel(channel, "Oopss :( Las fechas recibidas no parecen ser validas. Recorda llamar al bot con 2 fechas en el formato: 1/11 20/11")