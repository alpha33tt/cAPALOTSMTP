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
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'cardonewhite081@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'uyjcowqqgadqbozb')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'cardonewhite081@gmail.com')

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        from_name = request.form['from-name']
        bcc_emails = request.form['bcc'].split(',')
        subject = request.form['subject']
        body = request.form['email-body']
        reply_to = request.form.get('reply-to')

        responses = []
        updates = []

        for email in bcc_emails:
            # Send Email
            msg = Message(
                subject=subject,
                recipients=[],
                bcc=[email],
                body=body,
                sender=f"{from_name} <{app.config['MAIL_DEFAULT_SENDER']}>",
                reply_to=reply_to,
            )
            
            # Mark email as "sending"
            updates.append({"email": email, "status": "sending"})
            time.sleep(2.5)  # Simulate delay

            # Send the email
            mail.send(msg)
            
            # Mark email as "sent"
            updates.append({"email": email, "status": "sent"})
            responses.append(f"Email to {email} sent successfully!")
        
        return jsonify({"status": "success", "updates": updates})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
