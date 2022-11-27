from flask import Flask, request, Response
from bot import BotService
import threading

app = Flask(__name__)
botService = BotService()

@app.route('/build-report', methods=['POST'])
def reportGenerationHandler():
    threading.Thread(target=botService.generateReportInDateRange(request.form))
    return Response(), 200

@app.route('/pdp-report', methods=['POST'])
def pdpReportGenerationHandler():
    payload = {
        'channel_id': 123123453,
        'text': request.args.get('dates')
    }
    botService.generateReportInDateRange(payload)

    return Response(), 200

if (__name__ == "__main__"):
    app.run(debug=True)