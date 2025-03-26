from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import time

app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

app.config['MAIL_USERNAME'] = 'paulmotil235@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'aoarlmobvjtablgm'  # Replace with your app-specific password
app.config['MAIL_DEFAULT_SENDER'] = 'paulmotil235@gmail.com'

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
        recipients = request.form['recipients'].split(',')  # Split comma-separated emails
        subject = request.form['subject']
        body = request.form['email-body']
        reply_to = request.form.get('reply-to')

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
                recipients=[email],  # Send email individually to each recipient
                body=plain_text_body,  # Plain text content
                html=body,  # HTML content
                sender=f"{from_name} <{app.config['MAIL_DEFAULT_SENDER']}>",  # From name
                reply_to=reply_to,  # Set the 'Reply-to' email
            )

            # Set headers properly using the Message object attributes
            msg.extra_headers = {
                'X-Mailer': 'Flask-Mail',
                'List-Unsubscribe': '<mailto:unsubscribe@yourdomain.com>',
                'Precedence': 'bulk',
            }

            # Handle file attachments (if any)
            if 'attachment' in request.files:
                attachment = request.files['attachment']
                if attachment:
                    msg.attach(attachment.filename, attachment.content_type, attachment.read())

            # Forward the email (send it individually)
            mail.send(msg)

            # Wait 2.5 seconds before sending the next email to avoid being flagged as spam
            time.sleep(2.5)

            # Add a response for each sent email
            responses.append(f"Email to {email} sent successfully!")

        return jsonify({"status": "success", "responses": responses})

    except Exception as e:
        app.logger.error(f"Error while sending email: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
