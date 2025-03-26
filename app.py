import os
import re
import time
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Consider using services like SendGrid for production
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'cardonewhite081@gmail.com')  # Use your verified email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'uyjcowqqgadqbozb')  # Use your Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'cardonewhite081@gmail.com')

# Initialize Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')  # Ensure this file exists in your templates folder

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
        progress_updates = []  # This will store the progress of each email

        # Loop through the BCC emails and send them one by one
        for email in bcc_emails:
            # Send signal for "Sending" state
            progress_updates.append({"status": "sending", "email": email})

            msg = Message(
                subject=subject,
                recipients=[],  # No recipients, since we're using BCC
                bcc=[email],
                body=plain_text_body,  # Plain text content
                html=body,  # HTML content
                sender=f"{from_name} <{app.config['MAIL_DEFAULT_SENDER']}>",  # From name
                reply_to=reply_to,  # Set the 'Reply-to' email
            )

            # Send the email
            mail.send(msg)

            # Wait a bit before sending the next email (2.5 seconds delay)
            time.sleep(2.5)

            # Send signal for "Sent" state
            progress_updates.append({"status": "sent", "email": email})

        return jsonify({"status": "success", "updates": progress_updates})

    except Exception as e:
        app.logger.error(f"Error while sending email: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
