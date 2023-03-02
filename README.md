# Upload S3 file to SharePoint Site

This script uses minimal dependencies to grab the recent upload in an S3 bucket and uploads the file to a SharePoint site.

## How to run this script once a file is uploaded to your S3 bucket?

Below are the steps to trigger a Lambda function once a file is uploaded in your S3 bucket.

Creation of Lambda function steps:

1. Upload this script to a Lambda function
2. Fill in the environment variables
3. Create the necessary VPC
4. Allow permissions for download in S3

Creation of Lambda function trigger steps:

1. Go to "Properties" tab in your S3 bucket page
2. Scroll down to the "Events" section
3. Click "Add Notifications" and a new window will open
4. Give the new notification a name.
5. Select "PUT" in the events section (a PUT request will trigger the Lambda function)
6. Select the Lambda function you use after a file is uploaded
