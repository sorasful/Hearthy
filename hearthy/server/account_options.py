class AccountOptions:
    def __init__(self, db, prefix):
        self.prefix = prefix
        self.db = db

    def __iter__(self):
        options = self.db.prefix_query(self.prefix, include_docs=True)
        def iterator():
            for option in options:
                yield (option['key'][-1], option['doc'])
        return iterator

    def __getitem__(self, name):
        return self.db[self.prefix + [name]]

    def __setitem__(self, name, value):
        """ Set's an option.

        Args:
           name (str): the option name
           value (dict): json serializable object
        """
        self.db[self.prefix + [name]] = value
