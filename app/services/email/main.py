import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, smtp_username: str, smtp_password: str, use_tls: bool = True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.use_tls = use_tls

    def _create_connection(self):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            # Consider using a logging library for better error tracking
            print(f"Failed to create SMTP connection: {e}")
            raise

    def send_email(self,
                    sender_email: str,
                    recipient_emails: List[str],
                    subject: str,
                    body: str,
                    is_html: bool = False,
                    cc_emails: Optional[List[str]] = None,
                    bcc_emails: Optional[List[str]] = None):
        """
        Sends an email to one or more recipients.

        Args:
            sender_email (str): The email address of the sender.
            recipient_emails (List[str]): A list of recipient email addresses.
            subject (str): The subject of the email.
            body (str): The content of the email.
            is_html (bool, optional): True if the body is HTML, False otherwise. Defaults to False.
            cc_emails (Optional[List[str]], optional): A list of CC recipient email addresses. Defaults to None.
            bcc_emails (Optional[List[str]], optional): A list of BCC recipient email addresses. Defaults to None.
        """
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(recipient_emails)
        if cc_emails:
            msg['Cc'] = ", ".join(cc_emails)
        msg['Subject'] = subject

        body_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, body_type))

        all_recipients = recipient_emails + (cc_emails or []) + (bcc_emails or [])

        try:
            with self._create_connection() as server:
                server.sendmail(
                    sender_email, all_recipients, msg.as_string()
                )
        except Exception as e:
            # Consider using a logging library for better error tracking
            print(f"Failed to send email: {e}")
            # Depending on your application's needs, you might want to re-raise the exception
            # raise

        if is_html:
            msg