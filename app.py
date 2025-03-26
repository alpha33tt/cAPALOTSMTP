from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import os
import time

app = Flask(__name__)

# Configure email settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hewlettpackardenterprise01@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'aoarlmobvjtablgm'  # Your app password
app.config['MAIL_DEFAULT_SENDER'] = 'hewlettpackardenterprise01@gmail.com'

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        # Check if the required fields are available
        from_name = request.form.get('from-name')
        bcc_emails = request.form.get('bcc', '').split(',')
        subject = request.form.get('subject')
        body = request.form.get('email-body')
        reply_to = request.form.get('reply-to', '')

        # Validate that required fields are present
        if not from_name or not bcc_emails or not subject or not body:
            return jsonify({"status": "error", "message": "Missing required fields."}), 400

        responses = []
        updates = []

        # Loop through BCC emails to send one by one
        for email in bcc_emails:
            if not email.strip():  # Skip empty emails
                continue

            # Send email
            msg = Message(
                subject=subject,
                recipients=[],  # No recipients since we are using BCC
                bcc=[email],
                body=body,
                sender=f"{from_name} <{app.config['MAIL_DEFAULT_SENDER']}>",
                reply_to=reply_to,
            )

            # Update status: email is being sent
            updates.append({"email": email, "status": "sending"})
            time.sleep(2.5)  # Wait for 2.5 seconds to simulate delay between sends

            # Send the email
            mail.send(msg)

            # Update status: email sent successfully
            updates.append({"email": email, "status": "sent"})
            responses.append(f"Email to {email} sent successfully!")

        return jsonify({"status": "success", "updates": updates})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
