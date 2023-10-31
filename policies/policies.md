# Policies Required for IdioSplash

Note: API Gateway Roles and Cloudwatch Roles are automatically created for you when creating Lambda functions. You do not need to create them manually.

All required policies are located in the policies folder as _templates_. The policies are as follows:

## DynamoDB Policies

There are three DynamoDB tables that are required for IdioSplash to work. The first being Read/Write access for the GenerateOTP function. The second is Get/Delete access for the VerifyOTP function. The third is for required by SendOTPEmail to read the stream from the DynamoDB table.

## SES Policy

There is one role for SES that is required for IdioSplash to work. This role is for the SendOTPEmail function. It is required to send emails to the user.

## Lambda Policy

There is one role for Lambda that is allows for invocation access only. This policy is utilized by VerifyOTP to invoke the GenerateIPSK function.
