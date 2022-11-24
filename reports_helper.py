from fpdf import FPDF
import uuid

class ReportGenerator:

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

    def addMeliHeader(self, pdf, startDate, endDate):
        pdf.set_left_margin(0)
        pdf.set_right_margin(0)
        pdf.set_xy(0, 5)

        # Meli yellow color
        pdf.set_fill_color(254, 230, 0)
        pdf.set_text_color(95,95,95)

        self.writeCell(pdf, f"Guardia {startDate} al {endDate}  ", 15.0, "B", 0, True, 12.0, 2, "R", 0)
        self.writeCell(pdf, f"Gabriel Tortomano   ", 15.0, "", 0, True, 9.0, 2, "R", 0)
        pdf.image('./resources/logo.PNG', 8, 10, 18, 12)

    def addMainPage(self, pdf, alerts, date1, date2):
        pdf.add_page()
        self.addMeliHeader(pdf, date1, date2)
        pdf.set_left_margin(20)
        pdf.set_right_margin(20)

        pdf.ln(30)
        pdf.set_text_color(80,80,80)
        self.writeCell(pdf, f"Resumen de guardia", 35.0, "B", 0, False, 12.0, 2, "L", 0)
        
        pdf.ln(5)
        pdf.set_text_color(110,110,110)
        self.writeCell(pdf, f"Gabriel Tortomano", 20.0, "", 0, False, 8.0, 2, "L", 0)

        pdf.ln(15)
        self.writeCell(pdf, f"Período de guardia", 15.0, "B", 0, False, 8.0, 2, "L", 0)

        pdf.ln(8)
        pdf.cell(20)
        self.writeCell(pdf, f"{date1} al {date2}", 16.0, "", 0, False, 5.0, 2, "L", 0)

        pdf.ln(15)
        self.writeCell(pdf, "Cantidad de alertas", 15.0, "B", 0, False, 5.0, 2, "L", 0)

        pdf.ln(8)
        pdf.cell(20)
        self.writeCell(pdf, f"{len(alerts)}", 16.0, "B", 0, False, 5.0, 2, "L", 0)
        
        pdf.ln(40)

        # Printing statistics table
        for item in self.getStatistics(alerts):
            key = list(item.keys())[0]
            data = item.get(key)
            cell_height = 10

            if item.get("multiple"):
                cell_height = 30

            self.writeCell(pdf, f" {key}", 14, "", 1, False, cell_height, 3, "L", pdf.epw/2)
            self.writeCell(pdf, f" {data}", 13, "B", 1, False, cell_height, 3, "L", pdf.epw/2)
            pdf.ln(10)

    def writeThreadMessage(self, pdf, message):
        pdf.cell(15)

        # Write user picture
        message_user = message.get("user")
        pdf.image(message_user.get("picture"), w=10, h=10)
        pdf.ln(-10)
        pdf.cell(32)

        self.writeCell(pdf, message.get("text"), 12.0, "")
        pdf.ln(10)

        if (message.get("files") != None):
            files = message.get("files")

            if (len(files) > 1):
                for attachment in files:
                    pdf.cell(60)
                    pdf.image(attachment, w=pdf.epw/2 - 10)
            else:
                pic_width = 90

                # pdf total width - picture width - pdf margins
                # divided by 2 to get spaces neded to be center aligned
                left_margin = (pdf.epw - pic_width - 10)/2
                pdf.cell(left_margin)

                # response = requests.get(files[0].get("thumb_720"))
                # im = Image.open(BytesIO(response.content))

                # TODO: investigate why attachments files wont work
                pdf.image(files[0], w=pic_width)
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

    def generateReport(self, alerts, date1, date2):
        pdf = FPDF(format='A4')
        pdf.add_font('Nunito', '', './fonts/Nunito-VariableFont_wght.ttf', uni=True)
        pdf.add_font('Nunito', 'B', './fonts/Nunito-Bold.ttf', uni=True)
        pdf.set_auto_page_break(True, 8)
        self.addMainPage(pdf, alerts, date1, date2)
        self.addAlertsPage(pdf, alerts)

        pdf.output(f"docs/{uuid.uuid1()}.pdf", "F")
        print(f"Successfully generated report for dates: {date1} {date2}")


