import uuid
import requests
import os
from fpdf import FPDF
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(".") / '.env')
SLACK_TOKEN = os.environ['SLACK_TOKEN']

class Reports:

    def getStatistics(self, alerts):
        statistics = []
        retriggered = 0

        apps = {}
        retriggered_alerts = {}
        for alert in alerts:
            app = alert.get("app")
            app_witout_spaces = app.replace(" ", "_")
            key = f"{app_witout_spaces}-{alert.get('reason').replace(' ', '-')}"

            # Counting re-triggered alerts
            if (retriggered_alerts.get(key) == None):
                retriggered_alerts[key] = 1
            else:
                retriggered_alerts[key] = retriggered_alerts[key] + 1

            # Counting most triggered app
            if apps.get(app) == None:
                apps[app] = 1
            else:
                apps[app] = apps[app] + 1

        for item in retriggered_alerts:
            if retriggered_alerts.get(item) > 1:
                data = retriggered_alerts.get(item)
                retriggered += data
        
        selected_app = "-"
        for app in apps:
            count = 1
            if (apps.get(app) > count):
                count = apps.get(app)
                selected_app = app

        statistics.append({'Alertas repetidas': retriggered})
        statistics.append({'Aplicación más reiterada': selected_app})
        statistics.append({'Comentarios/Accionables': " *   ", "multiple": True})
        return statistics

    def writeCell(self, pdf, text, fontSize, fontStyle, border=0, fill=False, height=8, ln=2, align="L", w=0):
        pdf.set_font("Nunito", fontStyle, fontSize)

        pdf.multi_cell(
            ln=ln,
            h=height,
            align=align,
            w=w,
            txt=f"{text}",
            border=border,
            fill=fill
        )

    def addMeliHeader(self, pdf, startDate, endDate, user):
        pdf.set_left_margin(0)
        pdf.set_right_margin(0)
        pdf.set_xy(0, 5)

        # Meli yellow color
        pdf.set_fill_color(254, 230, 0)
        pdf.set_text_color(95,95,95)

        self.writeCell(pdf, f"", 15.0, "", 0, True, 3.0, 2, "R", 0)
        self.writeCell(pdf, f"Guardia {startDate} al {endDate}  ", 15.0, "B", 0, True, 8.0, 2, "R", 0)
        self.writeCell(pdf, f"", 15.0, "", 0, True, 2.0, 2, "R", 0)
        self.writeCell(pdf, f"{user}  ", 15.0, "", 0, True, 5.0, 2, "R", 0)
        self.writeCell(pdf, f"", 15.0, "", 0, True, 3.0, 2, "R", 0)
        pdf.image('./resources/logo.PNG', 8, 9, 18, 12)

    def addMainPage(self, pdf, alerts, date1, date2, user):
        pdf.add_page()
        self.addMeliHeader(pdf, date1, date2, user)
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)

        pdf.ln(30)
        pdf.set_text_color(80,80,80)
        self.writeCell(pdf, f"Resumen de guardia", 35.0, "B", 0, False, 12.0, 2, "L", 0)
        
        pdf.ln(5)
        pdf.set_text_color(110,110,110)
        self.writeCell(pdf, f"Período del {date1} al {date2}", 18.0, "", 0, False, 8.0, 2, "L", 0)

        pdf.ln(15)
        self.writeCell(pdf, f"Encargado", 15.0, "B", 0, False, 8.0, 2, "L", 0)

        pdf.ln(6)
        pdf.cell(20)
        self.writeCell(pdf, f"{user}", 18.0, "", 0, False, 5.0, 2, "L", 0)

        pdf.ln(13)
        self.writeCell(pdf, "Cantidad de alertas", 15.0, "B", 0, False, 5.0, 2, "L", 0)

        pdf.ln(6)
        pdf.cell(20)
        self.writeCell(pdf, f"{len(alerts)}", 18.0, "", 0, False, 5.0, 2, "L", 0)
        
        pdf.ln(20)

        # Printing statistics table
        for item in self.getStatistics(alerts):
            key = list(item.keys())[0]
            data = item.get(key)
            cell_height = 12

            if item.get("multiple"):
                cell_height = 40

            self.writeCell(pdf, f" {key}", 14, "", 1, False, cell_height, 3, "L", pdf.epw/2)
            self.writeCell(pdf, f" {data}", 14, "B", 1, False, cell_height, 3, "L", pdf.epw/2)
            pdf.ln(12)

    def writeThreadMessage(self, pdf, message):
        pdf.cell(15)
        message_user = message.get("user")
        message_text = message.get("text")
        message_files = message.get("files")

        # Write user picture
        if (message_user != None):
            pdf.image(message_user.get("picture"), w=10, h=10)
            pdf.ln(-12)
            pdf.cell(30)
            self.writeCell(pdf, message_user.get("name"), 13.0, "B")

        # Write text message
        if (message_text != None and message_text != ""):
            self.writeCell(pdf, message_text, 12.0, "")

        # Write images/attachments
        if (message_files != None and len(message_files) > 0):
            pic_width = 120

            for attachment in message_files:
                pdf.ln(5)

                # pdf total width - picture width - pdf margins
                # divided by 2 to get spaces neded to be center aligned
                left_margin = ((pdf.epw - pic_width)/2) + 5
                pdf.cell(left_margin)

                response = requests.get(attachment, headers={'Authorization': f'Bearer {SLACK_TOKEN}'})
                pdf.image(BytesIO(response.content), w=pic_width)

        pdf.ln(5)

    def addAlertsPage(self, pdf, alerts):
        pdf.add_page()
        pdf.set_text_color(20, 20, 20)

        try:
            for alert in alerts:

                # Writing headlines
                self.writeCell(pdf, alert.get('app'), 16.0, "B")
                self.writeCell(pdf, alert.get('reason'), 12.0, "", "B")
                pdf.ln(5)

                if alert.get("threads") != None:
                    for message in alert.get("threads"):
                        self.writeThreadMessage(pdf, message)
        except Exception as ex:
            print(f"Error writing alerts --> {ex}")

    def generate(self, alerts, date1, date2, user):
        pdf = FPDF(format='A4')
        pdf.add_font('Nunito', '', './fonts/Nunito-VariableFont_wght.ttf', uni=True)
        pdf.add_font('Nunito', 'B', './fonts/Nunito-Bold.ttf', uni=True)
        pdf.set_auto_page_break(True, 8)
        self.addMainPage(pdf, alerts, date1, date2, user)
        self.addAlertsPage(pdf, alerts)

        pdf.output(f"docs/{uuid.uuid1()}.pdf", "F")
        print(f"Successfully generated report for dates: {date1} {date2}")