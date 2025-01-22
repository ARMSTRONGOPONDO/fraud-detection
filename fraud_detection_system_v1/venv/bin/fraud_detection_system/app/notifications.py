from twilio.rest import Client

def send_notification(transaction):
    account_sid = 'AC5da8b60b33c771f243da45882fb2f056'
    auth_token = '0c8169f3adc1e53a8c27aee131b56508'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Transaction flagged: {transaction}",
        from_='+1234567890',
        to='+0987654321'
    )
    print(f"Notification sent: {message.sid}")

