from email.mime.text import MIMEText
import smtplib
import logging
import os

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")


# Alert function (it just logs the alert)
def send_alert(message):
    # Implement email alerting or integrate with a notification service
    logging.warning(f"ALERT: {message}")


# Alert function (using email)
def send_email_alert(message):
    if not all([SMTP_SERVER, SENDER_EMAIL, SMTP_PASSWORD, RECIPIENT_EMAIL]):
        logging.warning(
            "Email alert configuration is incomplete. Skipping email alert."
        )
        return

    msg = MIMEText(message)
    msg["Subject"] = "ALERT: Data Extraction Error"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        logging.info("Alert email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send alert email: {str(e)}")
