import os
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import re
import time

app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'hewlettpackardenterprise01@gmail.com')  # Gmail username
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'aoarlmobvjtablgm')  # Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'hewlettpackardenterprise01@gmail.com')

# Initialize Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

def strip_html_tags(html):
    """Remove HTML tags and return plain text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        from_name = request.form['from-name']
        bcc_emails = request.form['bcc'].split(',')
        subject = request.form['subject']
        body = request.form['email-body']
        reply_to = request.form.get('reply-to')

        # Get the plain text version of the email body
        plain_text_body = strip_html_tags(body)

        if not plain_text_body.strip():
            return 'Email body cannot be empty.', 400

        # Prepare the response
        responses = []
        email_counter = 1

        # Loop through the BCC emails and send them one by one
        for email in bcc_emails:
            msg = Message(
                subject=subject,
                recipients=[],  # No recipients, since we're using BCC
                bcc=[email],
                body=plain_text_body,  # Plain text content
                html=body,  # HTML content
                sender=f"{from_name} <{app.config['MAIL_DEFAULT_SENDER']}>",  # From name
                reply_to=reply_to,  # Set the 'Reply-to' email
            )

            # Set headers properly using the Message object attributes
            msg.extra_headers = {
                'X-Mailer': 'Flask-Mail',
                'List-Unsubscribe': '<mailto:unsubscribe@yourdomain.com>',  # Include unsubscribe link
                'Precedence': 'bulk',  # Mark email as bulk
                'List-Id': 'example-list@yourdomain.com',  # Use a unique list ID
            }

            # Handle file attachments (if any)
            if 'attachment' in request.files:
                attachment = request.files['attachment']
                if attachment:
                    msg.attach(attachment.filename, attachment.content_type, attachment.read())

            # Send the email
            mail.send(msg)

            # Wait for 2.5 seconds before sending the next email
            time.sleep(2.5)

            responses.append(f"Email to {email} sent successfully!")
            email_counter += 1

        return jsonify({"status": "success", "responses": responses})

    except Exception as e:
        app.logger.error(f"Error while sending email: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
