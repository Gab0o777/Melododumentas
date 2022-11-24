import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response

from slack_helper import SlackHelper
from reports_helper import ReportGenerator

load_dotenv(dotenv_path=Path(".") / '.env')

app = Flask(__name__)
slackHelper = SlackHelper(os.environ['SLACK_TOKEN'])

@app.route('/build-report', methods=['POST'])
def reportGenerationHandler():
    payload = request.form
    channel = payload.get('channel_id')
    datesArr = payload.get('text').split(' ')

    alerts = slackHelper.getAlertsInRange(channel, datesArr[0], datesArr[1])
    ReportGenerator().generateReport(alerts, datesArr[0], datesArr[1])

    return Response(), 200
    

if (__name__ == "__main__"):
    app.run(debug=True)