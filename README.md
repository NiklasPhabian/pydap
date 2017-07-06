# Pydap

[![Build Status](https://travis-ci.org/pydap/pydap.svg)](https://travis-ci.org/pydap/pydap)
[![Python2](https://img.shields.io/badge/python-2-blue.svg)](https://www.python.org/downloads/)
[![Python3](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/downloads/)
[![documentation](https://readthedocs.org/projects/pydap/badge/?version=latest)](http://pydap.readthedocs.org/en/latest/)
[![PyPI](https://img.shields.io/pypi/v/pydap.svg?maxAge=2592000?style=plastic)](https://pypi.python.org/pypi/Pydap/)

[Pydap](http://pydap.readthedocs.io/en/latest/) is an implementation of the Opendap/DODS protocol, written from scratch in pure python.  You can use Pydap to access scientific data on the internet without having to 
download it; instead, you work with special array and iterable objects that 
download data on-the-fly as necessary, saving bandwidth and time. The module 
also comes with a robust-but-lightweight Opendap server, implemented as a WSGI 
application.


# This Fork
In this fork, a feature for automatic citation generation is added to pydap. This is implemented by adding a "citation response" to pydap. The citation is constructed from meta data in the DAS, the date of access and the subsetting (selection) parameters. The citation response (citation representation of the data) can be accessed by appending ".citation" to the url of the dataset. 

The addition of the citation response is implemented in a fork of pydap, rather than in just an additional response for two reasons: 
1. Since the citation response contains the subsetting parameters, it requires knowledge of the request, rather than just the dataset. Therefore changes to the data handler lib had to be made.
2. For the purpose of presentation, the webinterface was modified to include buttons to access the citation response.

## Installing
This for can be installed by
  
    pip git+https://github.com/NiklasPhabian/pydap
    
## Launching a pydap server
One can use the pydap.wsgi.app:DapServer class, initialized with the path to your data files (a DapServer object is a WSGI callable). Then you can expose that as your "app" to any WSGI framework (from https://github.com/pydap/pydap/issues/46):

    from flask import Flask
    from pydap.wsgi.app import DapServer
  
    pydap_inst = DapServer('/path/to/my/data/files')
    app = Flask(__name__)
    app.wsgi_app = pydap_inst
    app.run('0.0.0.0', 8000)

An examplary pydap application is available at https://github.com/NiklasPhabian/occur_pydap
