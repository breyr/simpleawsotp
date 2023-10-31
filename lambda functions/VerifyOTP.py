import json
import boto3

# connect to DB
client = boto3.resource('dynamodb')
table = client.Table("EmailVerification")

# Create an AWS Lambda client
lambda_client = boto3.client('lambda')


def lambda_handler(event, context):

    res = {}

    # parse 'body' and get the otp sent from the user
    body = json.loads(event["body"])
    sent_otp = body['otp']

    try:
        # read from database for email
        # Query the DynamoDB table for the item with the specified primary key
        response = table.get_item(
            Key={
                "email": body["email"]
            }
        )

        # get the stored OTP for that user
        stored_otp = response['Item']['otp']

        if stored_otp == sent_otp:
            # delete record in dynamo
            try:
                response = table.delete_item(
                    Key={
                        "email": body["email"]
                    }
                )

                print("Item deleted successfully")

                # make call to GenerateIPSK function
                try:
                    # the payload required for Generate IPSK is only the
                    # verified email
                    payload = {
                        "body": {
                            "email": body["email"]
                        }
                    }
                    # invoke the lambda function passing the above payload
                    # 'RequestResponse' is synchronous and the default
                    # InvocationType per https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/invoke.html
                    gen_ipsk_res = lambda_client.invoke(
                        FunctionName="GenerateIPSK",
                        InvocationType="RequestResponse",
                        Payload=json.dumps(payload)
                    )
                    # convert bytes -> string -> dict
                    parsed_res = json.loads(json.loads(
                        gen_ipsk_res['Payload'].read().decode("utf-8")))
                    res = {
                        "statusCode": parsed_res["status"],
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": parsed_res
                    }
                except Exception as e:
                    print("Error invoking GenerateIPSK", str(e))

            except Exception as e:
                print("Error deleting item from DynamoDB:", str(e))
        else:
            # OTPs didn't match
            res = {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": {
                    "message": "Incorrect OTP."
                }
            }

    except Exception as e:
        # associate email doesn't have an OTP stored
        print(f"Error finding {body['email']} DynamoDB: {e}")
        res = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "message": "You don't have an OTP stored for " + body["email"]
            }
        }

    return json.dumps(res)
