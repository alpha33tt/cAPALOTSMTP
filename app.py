import os
import random
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from email.utils import formatdate

app = Flask(__name__)

# Configure email settings for Gmail SMTP
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'hewlettpackardenterprise01@gmail.com')  # Your Gmail email address
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'aoarlmobvjtablgm')  # Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'hewlettpackardenterprise01@gmail.com')

# Initialize Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

def get_ip_address():
    # This function retrieves the client's IP address from the Flask request object
    return request.remote_addr

def strip_html_tags(html):
    """Remove HTML tags and return plain text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        from_name = "PAUL MOTIL"  # Sender name
        from_email = "paulmotil235@gmail.com"  # The email address to be used in the "Reply-To"
        recipients = request.form['recipients'].split(',')  # Recipients (comma-separated)
        subject = request.form['subject']  # Email subject
        body = request.form['email-body']  # Email body
        reply_to = request.form.get('reply-to', from_email)  # Reply-to address

        # Get the plain text version of the email body
        plain_text_body = strip_html_tags(body)

        if not plain_text_body.strip():
            return 'Email body cannot be empty.', 400

        # Prepare the response
        responses = []

        # Loop through the recipients and send them one by one
        for email in recipients:
            msg = Message(
                subject=subject,
                recipients=[email],
                body=plain_text_body,
                html=body,
                sender=f"{from_name} <{from_email}>",
                reply_to=reply_to,
                date=formatdate(localtime=True)  # Include current date/time
            )

            # Set custom email headers
            msg.extra_headers = {
                'X-Mailer': 'CustomMailer/1.0',
                'X-Originating-IP': get_ip_address(),  # Add IP address of the sender
                'Precedence': 'bulk',  # For email bulk sending
                'X-Priority': '3 (Normal)',  # Set email priority
                'X-MSMail-Priority': 'Normal',  # Set MSMail priority
                'X-Content-Type-Options': 'nosniff',  # Block sniffing of content type
                'X-Entity-Ref-ID': str(random.randint(100000, 999999)),  # Unique ID
                'List-Unsubscribe': f'<mailto:unsubscribe@{from_email}?subject=Unsubscribe>',  # Unsubscribe option
                'Feedback-ID': f"{from_name}:{from_email}",
                'X-Campaign-ID': str(random.randint(1000, 9999))  # Random campaign ID
            }

            # Handle file attachments (if any)
            if 'attachment' in request.files:
                attachment = request.files['attachment']
                if attachment:
                    msg.attach(attachment.filename, attachment.content_type, attachment.read())

            # Send the email
            mail.send(msg)

            # Append success message to responses
            responses.append(f"Email to {email} sent successfully!")

        return jsonify({"status": "success", "responses": responses})

    except Exception as e:
        app.logger.error(f"Error while sending email: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
   import os

# Get the port from the environment (Render will provide this dynamically)
port = int(os.environ.get('PORT', 10000))  # Default to 10000 if PORT is not set

app.run(debug=True, host='0.0.0.0', port=port)
