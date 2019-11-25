
# What it is

RDF Demo is:

- free, libre and gratis, open source code ([GPLv2-licensed](LICENSE)).

- a web service that makes an RDF dataset in [HDT](http://www.rdfhdt.org/) format
    available for use in web applications.

- live at [http://34.223.88.59/].

- lightweight!  ... The demo host is a two-core Amazon EC2 `t3a.micro` instance with 1GB of
    RAM, serving a 1.1B triple dataset: the DBPedia 2016-10 English release.

# Why it is

[Graphs](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)) are interesting data
structures.

[RDF](https://en.wikipedia.org/wiki/Resource_Description_Framework) is a popular model
for describing graph data.

Resource-efficiency is a fun engineering challenge.

# Installation

1. Install system packages.

```
    apt-get install g++ python3-dev virtualenv
```

2. Create a virtualenv.

```
    virtualenv -p /usr/bin/python3 VENV_DIR
```

3. Install python packages into virtualenv.

```
    VENV_DIR/bin/pip install -r requirements.txt
```

# Configure

1. Obtain an HDT dataset.

2. Download the index for the dataset.

    - OR, load the HDT file and wait a few minutes; the index will be created by pyHDT
    automatically when it is not present.  In python:

```
    >>> from hdt import HDTDocument
    >>> HDTDocument('/path/to/hdt/file')
```

3. Create config file `$HOME/.rdf_demo_rc` with these contents:

```
    hdt_file_path: /path/to/hdt/file
```

4. Set PYTHONPATH.  (CHECKOUT_DIR is the directory containing this file.)

```
    export PYTHONPATH=CHECKOUT_DIR/rdf_demo/:$PYTHONPATH
```

# Run

This will start an HTTP server at 127.0.0.1:5000.

```
    VENV_DIR/bin/python CHECKOUT_DIR/scripts/run_app.py
```

# Toys

I experimented with alternative backends for the storage of the dataset before realizing
that HDT is actually the ideal storage format for this project.

None of these scale to the size of DBPedia 2016-10, so they are not part of the live demo:

- [bdb_tool](bdb_tool) is based on Berkeley DB (bsddb3 python package).
- [git_db](git_db) is based on libgit2 (pygit2 python package).
- [h5graph](h5graph) is based on HDF5 (h5py python package).

