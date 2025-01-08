import smtplib

def handle_bounce(campaign, recipient, error_message):
    EmailLog.objects.create(
        campaign=campaign,
        recipient=recipient,
        subject="Bounced Email",
        status='bounced',
        error_message=error_message
    )
    # You might want to update the contact status or notify the user here

def send_bulk_emails(campaign_id, batch_size=100, delay=1):
    # ... (previous code)

    for i in range(0, total_contacts, batch_size):
        batch = contacts[i:i+batch_size]
        messages = []
        for contact in batch:
            if validate_email_address(contact.email):
                email = EmailMessage(
                    subject=campaign.email_template.subject,
                    body=campaign.email_template.body,
                    from_email=smtp_config.from_email,
                    to=[contact.email],
                    connection=connection,
                )
                messages.append(email)

        # Send the batch
        try:
            connection.send_messages(messages)
            sent_count += len(messages)

            # Log the sent emails
            for msg in messages:
                EmailLog.objects.create(
                    campaign=campaign,
                    recipient=msg.to[0],
                    subject=msg.subject,
                    status='sent'
                )
        except smtplib.SMTPException as e:
            # Handle bounces
            for msg in messages:
                handle_bounce(campaign, msg.to[0], str(e))

        # Delay between batches to avoid rate limiting
        time.sleep(delay)

    return sent_count