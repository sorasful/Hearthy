from urllib.request import quote, unquote

class MemoryDb:
    def __init__(self):
        self.data = {}

    def get_path(self, key):
        return '!'.join(quote(x) for x in key)

    def prefix_query(self, prefix, include_doc=True):
        prefix_path = self.get_path(prefix)

        ret = []
        for k,v in self.data.items():
            if k.startswith(prefix_path):
                if include_doc:
                    ret.append({'key':unquote(k).split('!'), 'doc':v})
                else:
                    ret.append(unquote(k).split('!'))

        return ret

    def prefix_copy(self, prefix, dst):
        prefix_path = self.get_path(prefix)
        dst_path = self.get_path(dst)

        new = {}
        for k,v in self.data.items():
            if k.startswith(prefix_path):
                new[k.replace(prefix_path, dst_path, 1)] = v

        self.data.update(new)

    def __getitem__(self, key):
        path = self.get_path(key)
        return self.data[path]

    def __setitem__(self, key, value):
        path = self.get_path(key)
        self.data[path] = value
