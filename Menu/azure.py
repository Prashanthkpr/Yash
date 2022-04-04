from django.conf import settings
from azure.storage.blob import BlobClient

def upload_file_to_azure(file_obj, container_name=None, blob_name=None):

   conn_str = settings.STORAGE_ACCESS_KEY
   blob = BlobClient.from_connection_string(
       conn_str=conn_str, container_name=container_name, blob_name=blob_name
   )
   # with open('/home/aravind/Downloads/covid.jpeg', "rb") as data:
   return blob.upload_blob(file_obj.read())


def get_file_url(container_name, blob_name):
   conn_str = settings.STORAGE_ACCESS_KEY
   blob = BlobClient.from_connection_string(
       conn_str=conn_str, container_name=container_name, blob_name=blob_name
   )
   if blob.exists():
       return blob.url
   return None


def delete_file(container_name, blob_name):
   conn_str = settings.STORAGE_ACCESS_KEY
   blob = BlobClient.from_connection_string(
       conn_str=conn_str, container_name=container_name, blob_name=blob_name
   )
   if blob.exists():
       blob.delete_blob()
       return True
   return False