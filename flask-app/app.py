from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

s3 = boto3.client('s3')

BUCKET_NAME = "tiger-mle-pg"
BASE_FOLDER = "home/kajal.agarwal/"

@app.route('/', methods=['GET'])
def list_files():
    folder_name = request.args.get('folder', '').strip()
    
    if folder_name not in ["A", "B", "C"]:
        return jsonify({"error": "Invalid folder name"}), 400

    prefix = BASE_FOLDER + folder_name + "/"
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

    if "Contents" in response:
        files = [obj["Key"].replace(prefix, "") for obj in response["Contents"] if obj["Key"] != prefix]
        return jsonify({"files": files})
    else:
        return jsonify({"message": "No files found"}), 200  # Changed 404 to 200 for an empty folder

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085, debug=True)

