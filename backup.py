# Azure version of backup script
import os
import zipfile
import datetime
import yaml
import logging
from azure.storage.blob import BlobServiceClient

logging.basicConfig(filename='backup.log', level=logging.INFO)

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def create_backup_zip(source_dir, output_dir="backups"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    zip_name = f"{output_dir}/backup-{timestamp}.zip"
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), source_dir))
    logging.info(f"Created archive: {zip_name}")
    return zip_name

def upload_to_blob(file_path, conn_str, container):
    client = BlobServiceClient.from_connection_string(conn_str)
    blob = client.get_blob_client(container=container, blob=os.path.basename(file_path))
    with open(file_path, "rb") as data:
        blob.upload_blob(data, overwrite=True)
    logging.info(f"Uploaded to Azure container: {container}")

def main():
    try:
        config = load_config()
        path = create_backup_zip(config["backup_dir"])
        upload_to_blob(path, config["connection_string"], config["container_name"])
    except Exception as e:
        logging.error(f"Failed backup: {e}")

if __name__ == "__main__":
    main()
