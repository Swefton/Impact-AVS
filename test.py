from google.cloud import storage
from test_functions.credetials import GCLOUD_PROJECT_ID

def get_file_metadata(bucket_name, blob_name):
    """Retrieves metadata of a blob from the bucket."""
    storage_client = storage.Client(project=GCLOUD_PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Access metadata
    metadata = blob.metadata
    return metadata


print(get_file_metadata("journalvideoanalysis", "video.mp4"))