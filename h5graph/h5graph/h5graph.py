
import h5py


class H5GroupSize():
    def __init__(self, group, do_init=False):
        self.group = group
        if do_init:
            self.group['size'] = '0'
            self.group['last_size'] = '0'

    @property
    def value(self):
        return int(self.group['size'].value)

    def increment(self):
        # do this little shuffle to ensure that either size or last_size is always
        # stored, since changing a value requires deleting it first.
        last_size = int(self.group.pop('last_size').value)
        self.group['last_size'] = str(last_size + 1)

        size = int(self.group.pop('size').value)
        assert size == last_size, (size, last_size)
        self.group['size'] = str(last_size + 1)


class H5Group():
    def __init__(self, file_, name, do_create=False):
        self.file = file_
        self.name = name
        try:
            self.elements = file_[name]
            self.size = H5GroupSize(self.elements)
        except KeyError as e:
            if do_create:
                self.elements = file_.create_group(name)
                self.size = H5GroupSize(self.elements, True)
            else:
                raise e

    def __repr__(self):
        return f'H5Group({self.name})'

    def __len__(self):
        return self.size.value

    def __getitem__(self, key):
        return self.elements[key].value

    def __setitem__(self, key, value):
        try:
            del self.elements[key]
        except KeyError:
            pass
        self.elements[key] = value
        self.size.increment()


class H5UniqueId():
    def __init__(self, file_, name, do_create=False):
        self.file = file_
        self.name = name
        try:
            self.elements = file_[f'/{name}s']
            self.ids = file_[f'/{name}ids']
            self.size = H5GroupSize(self.elements)
        except KeyError as e:
            if do_create:
                self.elements = file_.create_group(f'{name}s')
                self.ids = file_.create_group(f'{name}ids')
                self.size = H5GroupSize(self.elements, True)
            else:
                raise e

    def __repr__(self):
        return f'H5UniqueId({self.name})'

    def __len__(self):
        return self.size.value

    def element_id(self, str_):
        id_ = self.elements.get(str_)
        if id_:
            id_ = id_.value
        else:
            self.elements[str_] = id_ = str(len(self) + 1)
            self.ids[id_] = str_
            self.size.increment()
        return id_

    def element(self, id_):
        return self.ids.get(id_).value


class H5Graph():
    def __init__(self, path, mode='r', log=None, do_create=False):
        self.log = log or print
        self.file = h5py.File(path, mode)
        self.path = path
        self.nouns = H5UniqueId(self.file, 'noun', do_create)
        self.verbs = H5UniqueId(self.file, 'verb', do_create)
        self.in_edges = H5Group(self.file, 'in_edges', do_create)
        self.out_edges = H5Group(self.file, 'out_edges', do_create)

    def __repr__(self):
        return f'H5Graph({self.path})'

    @property
    def n_nouns(self):
        return len(self.nouns)

    @property
    def n_verbs(self):
        return len(self.verbs)

    @property
    def n_in_edges(self):
        return len(self.in_edges)

    @property
    def n_out_edges(self):
        return len(self.out_edges)

    def report(self):
        self.log(f'{repr(self)} has {self.n_nouns} nouns, {self.n_verbs} verbs, '
                 f'{self.n_in_edges} inbound edges, and {self.n_out_edges} '
                 f'outbound edges')
