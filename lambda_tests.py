# for aws
import boto3

# for errors
import botocore

# time formatting
from datetime import datetime

####################################     IMPORTANT NOTES    ####################################
#
#    Script will run on bucket and COPY files older than X days to a new folder.
#    Script will skip folders with date format matching backup_format (including folders content).
#
#  * Fill in bucket name
#
#  * IF YOU CHANGE BACKUP_FORMAT - MAKE SURE TO CHANGE SUBSTRING LENGTH IN TRY IF NEEDED
#    AND LOG FORMAT CHANGES (TO SKIP THEM IN TRY)
#
#  * SCRIPT DOES NOT REMOVE ORIGINAL FILES!!!
#
#  * AFTER RUNNING SCRIPT, ORIGINAL FILES MUST BE HANDLED (REMOVED OR MOVED TO SOME
#    BACKUP FOLDER / OTHER BUCKET) FOR SCRIPT TO WORK ON NEXT RUN.
#    THIS IS BECAUSE SCRIPT CREATES FOLDER ONLY ONCE!
#
#  * Returns 0 on success and 1 if not all files were copied
#
#################################################################################################

# bucket for script to run on
bucket_name = 'unique-bucket-321'

# How old file's last modified should be (in days) for it to be moved to new bucket
desired_age = 1

# desired format for backup folders
backup_format = '%d-%m-%Y'

########################################################################################

s3_resource = boto3.resource('s3')

s3_client = boto3.client('s3')

# Get desired bucket
bucket = s3_resource.Bucket(bucket_name)

new_folder_name = ''

# Get current time to compare to objects modified time (should have same formats for successful comparison)
current_time = datetime.strptime(datetime.now().strftime(backup_format), backup_format)

# Create a paginator to pull all objects if there is more than 1,000 (aws limit)
paginator = s3_client.get_paginator('list_objects')
pageresponse = paginator.paginate(Bucket=bucket_name)

# Go through all bucket's objects
for pageobject in pageresponse:

    for file in pageobject["Contents"]:

        # compare objects modified time to current time
        last_modified = datetime.strptime(str(file["LastModified"].strftime(backup_format)), backup_format)

        # check if object is older than desired_age
        if (current_time - last_modified).days >= desired_age:

            # invoke try to ignore previews backup folders we created
            # SUBSTRING LENGTH IS FORMAT DEPENDED
            try:

                datetime.strptime(file['Key'][:10], backup_format)
            except ValueError:

                # file is not backup folder and is older than specified
                # format / name for a new folder with a name of date object was last modified on
                new_folder_name = last_modified.strftime(backup_format)

                # Create new folder in a bucket (less traffic heavy than checking for existence first)
                s3_client.put_object(
                    Bucket=bucket_name,
                    Body='',
                    Key='%s/' % new_folder_name)

                # check if object is already backed up
                try:

                    s3_resource.Object(bucket_name, '%s/%s' % (new_folder_name, file['Key'])).load()

                except botocore.exceptions.ClientError as e:

                    # file is not backed up, copy it to appropriate folder
                    s3_client.copy_object(Bucket=bucket_name,
                                          CopySource={'Bucket': bucket_name, 'Key': file["Key"]},
                                          Key='%s/%s' % (new_folder_name, file["Key"]))