import boto3
import csv
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Passing Jenkins Pipeline Parameters
aws_keys = os.envrion.get("AWS_ACCESS_KEY")
aws_secret = os.environ.get("AWS_SECRET_KEY")
aws_region =  os.environ.get("AWS_REGION")
recipient_list = os.environ.get("Email")

# Initialize a session using Amazon EC2
ec2 = boto3.client('ec2',aws_access_key=aws_keys,aws_secret_access=aws_secret,region=aws_region)

# Function to create a CSV file with deleted snapshot details
def create_csv_file(deleted_snapshots):
    # Define the CSV file name
    csv_file = 'deleted_snapshots.csv'
    
    # Write snapshot details to the CSV file
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Snapshot ID', 'Creation Time', 'Size (GB)'])
        # Write each snapshot's details
        for snapshot in deleted_snapshots:
            writer.writerow([snapshot['SnapshotId'], snapshot['StartTime'], snapshot['VolumeSize']])
    
    return csv_file

# Function to send an email with the CSV file as an attachment
def send_email_with_attachment(csv_file, target_email):
    # Email configuration
    sender_email = 'your_email@example.com'  # Replace with your email
    sender_password = 'your_password'       # Replace with your email password
    subject = 'Deleted EC2 Snapshots Report'
    body = 'Please find attached the list of deleted EC2 snapshots.'

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = target_email
    msg['Subject'] = subject
    msg.attach(MIMEMultipart(body))

    # Attach the CSV file
    with open(csv_file, 'rb') as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={csv_file}')
        msg.attach(part)

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Replace with your SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, target_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main function to delete snapshots and handle CSV/email
def delete_old_snapshots_and_send_report():
    # Get the current date and time
    current_date = datetime.now()

    # Calculate the date 7 days ago
    seven_days_ago = current_date - timedelta(days=7)

    # Describe all snapshots owned by the user
    response = ec2.describe_snapshots(OwnerIds=['self'])

    # List to store deleted snapshot details
    deleted_snapshots = []

    # Iterate through each snapshot
    for snapshot in response['Snapshots']:
        # Get the snapshot creation date
        snapshot_date = snapshot['StartTime'].replace(tzinfo=None)
        
        # Check if the snapshot is older than 7 days
        if snapshot_date < seven_days_ago:
            # Add snapshot details to the list
            deleted_snapshots.append({
                'SnapshotId': snapshot['SnapshotId'],
                'StartTime': snapshot['StartTime'],
                'VolumeSize': snapshot['VolumeSize']
            })
            # Delete the snapshot
            ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
            print(f"Deleted snapshot {snapshot['SnapshotId']} created on {snapshot_date}")

    # Create a CSV file with deleted snapshot details
    if deleted_snapshots:
        csv_file = create_csv_file(deleted_snapshots)
        print(f"CSV file '{csv_file}' created with deleted snapshot details.")

        # Send the CSV file as an email attachment
        target_email = 'target_email@example.com'  # Replace with the target email address
        send_email_with_attachment(csv_file, target_email)
    else:
        print("No snapshots were deleted.")

# Run the main function
delete_old_snapshots_and_send_report()
