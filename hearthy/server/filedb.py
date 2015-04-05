import os
import json
import tempfile
import shutil

class FileDb:
    def __init__(self, basedir, encoding='UTF-8'):
        """
        Args:
           basedir (str): The database location on the file system
           encoding (str): File encoding used store and read documents, defaults to UTF-8
        """
        self.basedir = basedir
        self.encoding = encoding
        self.tmpdir = os.path.join(self.basedir, 'tmp')

    def try_create_path(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def get_path(self, key):
        # TODO: make sure all components are safe
        return os.path.join(self.basedir, *key)

    def prefix_query(self, prefix, include_doc=True):
        # TODO: this should be recursive
        path = self.get_path(prefix)

        ret = []
        for name in os.listdir(path):
            key = prefix + [name]
            if include_doc:
                ret.append({'key': key, 'doc': self[key]})
            else:
                ret.append(key)
        return ret

    def prefix_copy(self, prefix, dst):
        """ Copies all documents beginning with a prefix

        Args:
           prefix (list): the prefix
           dst (list): the destination
        """
        src = self.get_path(prefix)
        dst_path = self.get_path(dst)

        with tempfile.TemporaryDirectory(dir=self.tmpdir) as tmpdst:
            path = os.path.join(tmpdst, 'moveme')
            shutil.copytree(src, os.path.join(tmpdst, path))

            try:
                os.replace(path, dst_path)
            except FileNotFoundError:
                self.try_create_path(dst_path)
                os.replace(path, dst_path)

    def __setitem__(self, key, value):
        """ Stores a document in the database

        Args:
          key (list): path specifying where to store the document
          value (dict): document to store
        """
        dst_path = self.get_path(key)

        with tempfile.NamedTemporaryFile(
                mode='w',
                dir=self.tmpdir,
                encoding=self.encoding,
                delete=False) as f:
            json.dump(value, f)
            src_path = f.name

        try:
            os.replace(src_path, dst_path)
        except FileNotFoundError:
            self.try_create_path(dst_path)
            os.replace(src_path, dst_path)

    def __getitem__(self, key):
        """ Retreives a document from the database

        Args:
           key (list): path of the document

        Returns:
           dict. The requested document
        """
        path = self.get_path(key)

        with open(path, 'r', encoding=self.encoding) as f:
            doc = json.load(f)

        return doc

    def __delitem__(self, key):
        """ Deletes a document from the database """
        path = self.get_path(key)
        os.unlink(path)
