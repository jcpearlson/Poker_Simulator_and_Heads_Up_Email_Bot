import pandas as pd
import schedule
import time
from datetime import datetime

# seperate python file to hold important info so it is hidden
from Private_info import getGmail, getGmailPass, getRecipientList

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

    # Add body to the email
    message.attach(MIMEText(body, "plain"))

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
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(attachment_path)}",
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



def sendEmailFinal(send_email=True):
    # get current time
    current_time_name = datetime.now().time()

    # read in csv
    data = read_csv()

    # create img path for image and save down
    img_path = f'media/{current_time_name}_monte_carlo.png'
    runSimulation(data).savefig(img_path)

    if send_email:
        # get email body
        body = getBody(data)
        recipients = getRecipientList()

        ## test list
        # recipients = [getGmail()]

        # send out the email
        send_email(recipients,'Josh <> Jimmy Heads-up Update!',body,img_path)


sendEmailFinal(send_email=False)


# TODO make sure this email is set up as a CRON job
 
# # Schedule the task to run weekly
# schedule.every().week.do(sendEmailFinal)

# # Daemon process to keep it running
# while True:
#     schedule.run_pending()
#     time.sleep(60)  # Check every minute
