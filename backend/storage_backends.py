from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class StaticStorage(S3Boto3Storage):
    location = 'static'
    # Remove ACL settings for bucket compatibility
    default_acl = None


class MediaStorage(S3Boto3Storage): 
    location = 'media'
    # Remove ACL settings for bucket compatibility
    default_acl = None
    file_overwrite = False


class CategoryImageStorage(S3Boto3Storage):
    location = 'categories'
    # Remove ACL settings for bucket compatibility
    default_acl = None
    file_overwrite = False


class ProductImageStorage(S3Boto3Storage):
    location = 'products'
    # Remove ACL settings for bucket compatibility
    default_acl = None
    file_overwrite = False
