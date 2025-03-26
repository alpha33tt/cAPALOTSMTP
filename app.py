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
