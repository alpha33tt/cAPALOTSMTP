import os
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import re
import time
import dkim
import random
from email.utils import formatdate
import socket

app = Flask(__name__)

# Enhanced email configuration
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=os.getenv('MAIL_USERNAME', 'hewlettpackardenterprise01@gmail.com'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD', 'aoarlmobvjtablgm'),
    MAIL_DEFAULT_SENDER=('PAUL MOTIL', os.getenv('MAIL_DEFAULT_SENDER', 'paulmotil235@gmail.com')),
    MAIL_MAX_EMAILS=50,
    MAIL_SUPPRESS_SEND=False,
    MAIL_ASCII_ATTACHMENTS=False
)

# Initialize Flask-Mail
mail = Mail(app)

# Domain verification and authentication setup
DOMAIN = "yourdomain.com"  # Replace with your actual domain
DKIM_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
YourPrivateKeyHere
-----END RSA PRIVATE KEY-----"""

def get_ip_address():
    """Get server IP address for reverse DNS matching"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

@app.route('/')
def index():
    return render_template('index.html')

def strip_html_tags(html):
    """Remove HTML tags and return plain text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)

def add_dkim_signature(msg):
    """Add DKIM signature to email headers"""
    headers = ['From', 'To', 'Subject', 'Date']
    sig = dkim.sign(
        message=msg.as_bytes(),
        selector='default',
        domain=DOMAIN,
        privkey=DKIM_PRIVATE_KEY.encode(),
        include_headers=headers
    )
    msg['DKIM-Signature'] = sig.decode().split(':', 1)[1].strip()
    return msg

def warmup_sending_pattern(total_emails):
    """Implement gradual warmup for new IP/domain"""
    if total_emails < 100:
        return random.uniform(5, 10)
    elif total_emails < 500:
        return random.uniform(2, 5)
    else:
        return random.uniform(1, 3)

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        from_name = "PAUL MOTIL"
        from_email = "paulmotil235@gmail.com"
        recipients = [email.strip() for email in request.form['bcc'].split(',') if email.strip()]
        subject = request.form['subject'].strip()
        body = request.form['email-body'].strip()
        reply_to = request.form.get('reply-to', from_email).strip()

        # Validate inputs
        if not recipients:
            return jsonify({"status": "error", "message": "No valid recipients provided"}), 400
        if not subject:
            return jsonify({"status": "error", "message": "Subject cannot be empty"}), 400
        if not body:
            return jsonify({"status": "error", "message": "Email body cannot be empty"}), 400

        plain_text_body = strip_html_tags(body)
        responses = []
        total_sent = 0

        for email in recipients:
            try:
                msg = Message(
                    subject=subject,
                    recipients=[email],
                    body=plain_text_body,
                    html=body,
                    sender=f"{from_name} <{from_email}>",
                    reply_to=reply_to,
                    date=formatdate(localtime=True)
                
                msg.extra_headers = {
                    'X-Mailer': 'CustomMailer/1.0',
                    'X-Originating-IP': get_ip_address(),
                    'Precedence': 'bulk',
                    'X-Priority': '3 (Normal)',
                    'X-MSMail-Priority': 'Normal',
                    'X-Content-Type-Options': 'nosniff',
                    'X-Entity-Ref-ID': str(random.randint(100000, 999999)),
                    'List-Unsubscribe': f'<mailto:unsubscribe@{DOMAIN}?subject=Unsubscribe>',
                    'Feedback-ID': f"{from_name}:{DOMAIN}",
                    'X-Campaign-ID': str(random.randint(1000, 9999))
                }

                msg = add_dkim_signature(msg)

                if 'attachment' in request.files:
                    attachment = request.files['attachment']
                    if attachment and attachment.filename:
                        msg.attach(
                            attachment.filename,
                            attachment.content_type,
                            attachment.read(),
                            'attachment',
                            '7bit'
                        )

                mail.send(msg)
                total_sent += 1
                responses.append(f"Email to {email} sent successfully!")

                delay = warmup_sending_pattern(total_sent)
                time.sleep(delay)

            except Exception as e:
                app.logger.error(f"Error sending to {email}: {str(e)}")
                responses.append(f"Failed to send to {email}: {str(e)}")
                continue

        return jsonify({
            "status": "success",
            "responses": responses,
            "sent_count": total_sent,
            "failed_count": len(recipients) - total_sent
        })

    except Exception as e:
        app.logger.error(f"System error: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"System error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
