#Pipe contents of each exported file through FILTER_CONTENTS <file-path> <hg-hash> <is-binary>"
import shlex
import hashlib
import pathlib
import os.path

def build_filter(args):
    return Filter(args)

class Filter:
    def __init__(self, args):
        self.filter_contents = shlex.split(args)
        self.convertext = {b'.gz', b'.GZ'}

    def file_data_filter(self,file_data):
        d = file_data['data']
        file_ctx = file_data['file_ctx']
        filename = file_data['filename']

        # An empty file is the pointer for an empty file. That is, empty files are passed through LFS without any change.
        # https://github.com/git-lfs/git-lfs/blob/main/docs/spec.md
        if file_ctx is None or not d:
            return
        _, ext = os.path.splitext(filename)
        if not ext in self.convertext:
            return
        sha256hash = hashlib.sha256(d).hexdigest()
        lfs_path = pathlib.Path(f".git/lfs/objects/{sha256hash[0:2]}/{sha256hash[2:4]}")
        lfs_path.mkdir(parents=True, exist_ok=True)
        lfs_file_path = lfs_path / sha256hash
        if not lfs_file_path.is_file():
            (lfs_path / sha256hash).write_bytes(d)

        file_data['data'] = ('version https://git-lfs.github.com/spec/v1\noid sha256:{}\nsize {}\n'.format(sha256hash, len(d))).encode('ascii')


version https://git-lfs.github.com/spec/v1\n
oid sha256:{}\n
size {}\n
