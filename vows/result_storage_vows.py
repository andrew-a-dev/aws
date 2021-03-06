#se!/usr/bin/python
# -*- coding: utf-8 -*-

from pyvows import Vows, expect

from thumbor.context import Context
from thumbor.config import Config
from fixtures.storage_fixture import IMAGE_BYTES, get_server

from boto.s3.connection import S3Connection
from moto import mock_s3

from tc_aws.result_storages.s3_storage import Storage

s3_bucket = 'thumbor-images-test'

class Request(object):
  url = None

@Vows.batch
class S3ResultStorageVows(Vows.Context):

  class CanStoreImage(Vows.Context):
    @mock_s3
    def topic(self):
      self.conn = S3Connection()
      self.conn.create_bucket(s3_bucket)

      config = Config(RESULT_STORAGE_BUCKET=s3_bucket)
      ctx = Context(config=config, server=get_server('ACME-SEC'))
      ctx.request = Request
      ctx.request.url = 'my-image.jpg'

      storage = Storage(ctx)
      path = storage.put(IMAGE_BYTES)

      return path

    def should_be_in_catalog(self, topic):
      expect(topic).to_equal('my-image.jpg')

  class CanGetImage(Vows.Context):
    @mock_s3
    def topic(self):
      self.conn = S3Connection()
      self.conn.create_bucket(s3_bucket)

      config = Config(RESULT_STORAGE_BUCKET=s3_bucket)
      ctx = Context(config=config, server=get_server('ACME-SEC'))
      ctx.request = Request
      ctx.request.url = 'my-image-2.jpg'

      storage = Storage(ctx)
      storage.put(IMAGE_BYTES)

      return storage.get()

    def should_not_be_null(self, topic):
      expect(topic).not_to_be_null()
      expect(topic).not_to_be_an_error()

    def should_have_proper_bytes(self, topic):
      expect(topic).to_equal(IMAGE_BYTES)

  class HandlesStoragePrefix(Vows.Context):
    @mock_s3
    def topic(self):
      self.conn = S3Connection()
      self.conn.create_bucket(s3_bucket)

      config = Config(RESULT_STORAGE_BUCKET=s3_bucket, RESULT_STORAGE_AWS_STORAGE_ROOT_PATH='tata')
      ctx = Context(config=config, server=get_server('ACME-SEC'))

      storage = Storage(ctx)

      return storage.normalize_path('toto')

    def should_return_the_same(self, topic):
      expect(topic).to_equal("tata/toto")

