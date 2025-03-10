import boto3
from flask import Flask

app = Flask(__name__)

# Initialize S3 client
s3 = boto3.client('s3')
BUCKET_NAME = "tiger-mle-pg"

@app.route("/")
@app.route("/home")
def home():
    """ Home route listing files in S3 bucket """
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    
    if "Contents" in response:
        files = [obj["Key"] for obj in response["Contents"]]
        return f"<h1>Home Page</h1><p>Files in S3: {files}</p>"
    else:
        return "<h1>Home Page</h1><p>No files found or access denied.</p>"

@app.route("/about")
def about():
    """ About page listing all S3 buckets """
    s3_resource = boto3.resource('s3')
    buckets = [bucket.name for bucket in s3_resource.buckets.all()]
    
    return f"<h1>About Page</h1><p>Available Buckets: {buckets}</p>"

if __name__ == '__main__':
    # Run Flask on 8085 to match your EC2 setup
    app.run(host='0.0.0.0', port=8085)
