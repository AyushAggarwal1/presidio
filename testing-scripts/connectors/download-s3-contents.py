# for s3 bucket need aws security reader permissions only

import boto3
import os

BUCKET_NAME = "<<-BUCKET_NAME->>"
LOCAL_DIR = "/home/ayush/Desktop/security-tools/presidio/s3-contents"

s3 = boto3.client("s3")

def download_bucket(bucket_name, local_dir):
    os.makedirs(local_dir, exist_ok=True)

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name)

    for page in pages:
        if "Contents" not in page:
            continue

        for obj in page["Contents"]:
            key = obj["Key"]

            # Skip "folders"
            if key.endswith("/"):
                continue

            local_path = os.path.join(local_dir, key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            print(f"Downloading s3://{bucket_name}/{key}")
            s3.download_file(bucket_name, key, local_path)

if __name__ == "__main__":
    download_bucket(BUCKET_NAME, LOCAL_DIR)
    print("Download complete.")
