import json
import boto3

# Initialize SES client
ses_client = boto3.client('ses', region_name='us-east-1')


def send_email(email, otp):
    """
    Send an OTP (One-Time Password) email to a user.

    This function sends an email containing a generated OTP to the specified email address.

    Parameters:
    - email (str): The recipient's email address.
    - otp (str): The One-Time Password to be sent in the email.

    Returns:
    - bool: True if the email was successfully sent, False otherwise.

    Raises:
    - Exception: If there is an error while sending the email, an exception is raised,
      and the error message is printed.

    Example:
    ```
    if send_email("recipient@example.com", "123456"):
        print("OTP email sent successfully.")
    else:
        print("Failed to send OTP email.")
    ```
    """

    # Email content
    sender_email = 'example@gmail.com'  # Replace with the sender's email address
    recipient_email = email  # Replace with the recipient's email address
    subject = 'Verify Email'
    message = f"""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Verify your login</title>
      <!--[if mso]><style type="text/css">body, table, td, a {{ font-family: Arial, Helvetica, sans-serif !important; }}</style><![endif]-->
    </head>
    <body style="font-family: Helvetica, Arial, sans-serif; margin: 0px; padding: 0px; background-color: #ffffff;">
      <table role="presentation"
        style="width: 100%; border-collapse: collapse; border: 0px; border-spacing: 0px; font-family: Arial, Helvetica, sans-serif; background-color: rgb(239, 239, 239);">
        <tbody>
          <tr>
            <td align="center" style="padding: 1rem 2rem; vertical-align: top; width: 100%;">
              <table role="presentation" style="max-width: 600px; border-collapse: collapse; border: 0px; border-spacing: 0px; text-align: left;">
                <tbody>
                  <tr>
                    <td style="padding: 40px 0px 0px;">
                      <div style="padding: 20px; background-color: rgb(255, 255, 255);">s
                        <div style="color: rgb(0, 0, 0); text-align: left;">
                          <h2>Verification Code</h2>
                          <p style="padding-bottom: 16px; color: black;">Please use the verification code below to sign in to x domain.</p>
                          <p style="padding-bottom: 16px;"><strong style="font-size: 130%">{otp}</strong></p>
                          <p style="padding-bottom: 16px; color: black">If you didn’t request this, you can ignore this email.</p>
                          <p style="padding-bottom: 16px; color: black">Thanks,<br>Your Company</p>
                        </div>
                      </div>
                      <div style="padding-top: 20px; color: rgb(153, 153, 153); text-align: center;">
                        <p style="padding-bottom: 16px">Secured by IdioSplash</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </tbody>
      </table>
    </body>
    """

    try:
        # Send the email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': message}}
            }
        )

        # Log the response
        print("Email sent successfully:", json.dumps(response, indent=2))

        return True
    except Exception as e:
        print("Error sending email:", str(e))
        return False


def lambda_handler(event, context):

    # loops through all records being processed from DynamoDB stream
    # the stream is configured to only send one at a time
    for record in event["Records"]:

        # Create an API Gateway response
        res = {}

        # filter only for eventName = INSERT
        if record["eventName"] == "INSERT":
            email = record["dynamodb"]["NewImage"]["email"]["S"]
            otp = record["dynamodb"]["NewImage"]["otp"]["S"]

            if send_email(email, otp):
                res = {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "message": "Email sent successfully."
                    }
                }
            else:
                res = {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "message": "Email failed to send"
                    }
                }

        return json.dumps(res)
