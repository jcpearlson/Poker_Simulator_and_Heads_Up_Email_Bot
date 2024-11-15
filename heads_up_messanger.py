# generics
import pandas as pd
import schedule
import time
from datetime import datetime

# separate python file to hold important info so it is hidden
from Private_info import getGmail, getGmailPass, getRecipientList,getOutlook,getPathToProject

# load in the simulator
from heads_up_simulator import runSimulation,getBody

# email library
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# helper functions
from helper_functions import * 

def send_email(recipient, subject, body, attachment_path=None):
    sender_email = getGmail()
    sender_password = getGmailPass()

    # Setup the MIME
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ', '.join(recipient)
    message["Subject"] = subject
    
    html_body = f"""
    <html>
        <body style="font-family: Courier New, monospace;">
            <pre style="font-size: 10px;">{body}</pre>
        </body>
    </html>
    """

    # adding weather report
    weather_report = body.find('63130')
    if weather_report != -1:
        html_body = f"""
    <html>
        <body style="font-family: Courier New, monospace;">
            <pre>{body[:weather_report]}</pre>
            <pre style="font-size: 8px;">{body[weather_report:]}</pre>
        </body>
    </html>
    """

    # Attach HTML-formatted body
    message.attach(MIMEText(html_body, "html"))

    # Attach file if provided
    if attachment_path:
        try:
            # Open file in binary mode
            with open(attachment_path, "rb") as attachment:
                # Instance of MIMEBase and named as part
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                
            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)
            
            # Add header with file name
            fileName = 'Projected_Results.png'
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {fileName}",
            )
            
            # Attach the part to the email
            message.attach(part)

        except Exception as e:
            logMsg(f"Failed to attach file: {e}")

    # Connect to the SMTP server
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, message.as_string())
            logMsg(f"Email sent to {recipient}")
    except Exception as e:
        logMsg(f"Error sending email to {recipient}: {e}")



def sendEmailFinal(email=True,testEmail=False):
    logMsg("******************* Starting run *******************")

    # get current time
    current_time_name = datetime.now().time()

    # read in csv
    data = read_csv()

    # get project path
    base = getPathToProject()

    # create img path for image and save 
    img_path = f'{base}Heads-Up-Emails/media/{current_time_name}_monte_carlo.png'
    runSimulation(data).savefig(img_path)

    if email:
        # get email body
        body = getBody(data)

        # if test email then getOutlook(personal email) else normal list
        recipients = [getOutlook()] if testEmail else getRecipientList()

        # send out the email
        send_email(recipients,'Weather Report + Josh <> Jimmy Heads-up Update!',body,img_path)


if __name__ == '__main__':
    """
    Params:
    - email:bool                     True to send email, false for no email.
    - (optional) testEmail:bool      True to send email only to me, false to send to group. Default is false.
    """
    sendEmailFinal(email=True,testEmail=False)

