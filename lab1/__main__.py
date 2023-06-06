"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws
import os
import mimetypes

"""
aws s3 ls $(pulumi stack output bucket_name)
- If error:
    - pip3 install --upgrade pyyaml
    - pip3 install --upgrade pulumi

Each instance is called a stack. We can have multiple environments.
"""
config = pulumi.Config()

site_dir = config.require("siteDir")

# Create new bucket
bucket = aws.s3.Bucket("testing-bucket", website={"index_document": "index.html"})

for file in os.listdir(site_dir):
    filepath = os.path.join(site_dir, file)
    mime_type, _ = mimetypes.guess_type(filepath)
    obj = aws.s3.BucketObject(
        file,
        bucket=bucket.bucket,
        source=pulumi.FileAsset(
            filepath
        ),  # Gets the asset based on the file path provided
        acl="public-read",  # Accessed anonymously over the internet
        content_type=mime_type,  # So it is served as the appropriate format such as html
    )

pulumi.export("bucket_name", bucket.bucket)
pulumi.export(
    "bucket_endpoint", pulumi.Output.concat("http://", bucket.website_endpoint)
)
