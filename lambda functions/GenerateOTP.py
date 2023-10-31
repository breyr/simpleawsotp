import json
import random
import string
import boto3
import time

# connect to DB
client = boto3.resource('dynamodb')
table = client.Table("EmailVerification")

# Calculate the expiration time (5 minutes from the current time)
expiration_time = int(time.time()) + (5 * 60)  # 5 minutes in seconds


def check_for_user(email):
    """
    Check if a user with the given email address exists in the database.

    Parameters:
    - email (str): The email address of the user to check for.

    Returns:
    - bool: True if a record with the provided email address exists in the database, False otherwise.

    Raises:
    - Exception: If there is an error reading from the DynamoDB table, an exception is raised.

    Example:
    ```
    if check_for_user("example@example.com"):
        print("User with email 'example@example.com' exists in the database.")
    else:
        print("User with email 'example@example.com' does not exist in the database.")
    ```
    """
    try:
        # read from database for email to see if the user already has an OTP there
        response = table.get_item(
            Key={
                "email": email
            }
        )
        print("Search in db", response)
        # if there is a record for that email
        if 'Item' in response:
            return True
        else:
            return False
    except Exception as e:
        print("Error reading from DynamoDB:", str(e))
        return False


def write_to_dynamodb(email, otp):
    """
    Write user data to a DynamoDB table.

    This function writes user information, including their email, OTP (One-Time Password),
    and a time-to-live (TTL) expiration time to a DynamoDB table.

    Parameters:
    - email (str): The email address of the user.
    - otp (str): The One-Time Password generated for the user.

    Returns:
    - bool: True if the data was successfully written to DynamoDB, False otherwise.

    Raises:
    - Exception: If there is an error while writing data to the DynamoDB table,
      an exception is raised, and the error message is printed.

    Example:
    ```
    if write_to_dynamodb("example@example.com", "123456"):
        print("User data successfully written to DynamoDB.")
    else:
        print("Failed to write user data to DynamoDB.")
    ```
    """

    print(email, otp)
    try:
        # Write data to DynamoDB
        response = table.put_item(
            Item={
                'email': email,     # 'S' for string
                'otp': otp,              # 'S'
                'ttl': expiration_time   # 'N' for number (Unix timestamp)
            }
        )
        print(response)
        return True
    except Exception as e:
        print(f"Error writing to DynamoDB: {e}")
        return False


def lambda_handler(event, context):

    # the body we get is a string
    body = json.loads(event["body"])

    # validate domain is within list of emails
    # if so, generate OTP and write to DynamoDB

    # maybe make STR_LEN configurable?
    STR_LEN = 6
    # string.digits is 0123456789
    otp = ''.join(random.choice(string.digits) for _ in range(STR_LEN))

    email = body["email"]
    # check for @arcadia.edu
    valid_email = True if email.split("@")[1] == "arcadia.edu" else False

    # if the email doesn't have arcadia.edu return 400
    if not valid_email:
        return json.dumps({
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "message": "Invalid email for this organization."
            }
        })

    # Create an API Gateway response
    res = {}

    # if the email passed in the request isn't found in the
    # EmailVerification table
    if not check_for_user(email):
        # if writing to the EmailVerification table is successfull
        if write_to_dynamodb(email, otp):
            res = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "email": email
                }
            }
        else:
            res = {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "message": "Error writing to database."
                }
            }
    else:
        res = {
            "statusCode": 409,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "message": "OTP previously generated for " + email + " please wait 5 minutes and try again."
            }
        }

    return json.dumps(res)
