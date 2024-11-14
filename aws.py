import boto3
region_name = 'ap-south-1'  # For example, 'us-west-1'
 
# S3 bucket information
bucket_name = 'cdnavathi'
prefix = 'travelGuide/dev/'
 
# Initialize S3 client with credentials
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)
 
def restore_deleted_files():
    try:
        is_truncated = True  # To handle pagination
        next_key_marker = None
        next_version_id_marker = None
 
        while is_truncated:
            # Call S3 to list object versions with pagination
            if next_key_marker:
                response = s3.list_object_versions(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    KeyMarker=next_key_marker,
                    VersionIdMarker=next_version_id_marker
                )
            else:
                response = s3.list_object_versions(
                    Bucket=bucket_name,
                    Prefix=prefix
                )
            delete_markers = response.get('DeleteMarkers', [])
 
            # Process delete markers (restore objects)
            for marker in delete_markers:
                key = marker['Key']
                version_id = marker['VersionId']
 
                # Delete the delete marker to restore the object
                s3.delete_object(Bucket=bucket_name, Key=key, VersionId=version_id)
                print(f"Restored: {key}")
 
            # Check if the results are paginated and handle the next page if necessary
            is_truncated = response.get('IsTruncated', False)
            if is_truncated:
                next_key_marker = response.get('NextKeyMarker', None)
                next_version_id_marker = response.get('NextVersionIdMarker', None)
 
        print(f"All deleted files in '{prefix}' have been restored!")
    except Exception as e:
        print(f"An error occurred: {e}")
# Run the restore function
if __name__ == "__main__":
    restore_deleted_files()