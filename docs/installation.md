# Installation

In most cases it should be possible to install Software Accounting as long as Python is already installed.

## Virtual environment

An easy opyion to install and update Software Accounting is to install it in a Python virtual environment. Create the Python virtual environment where you want it installed, and install Software Accounting using pip. Pip will install Software Accounting from the Python Packaging Index (PyPI).

```
python -m venv /opt/softwareaccounting
/opt/softwareaccounting/bin/pip install softwareaccounting
```

You can then update Software Accounting as new releases are published to PyPI.

```
/opt/softwareaccounting/bin/pip install --upgrade softwareaccounting
```

The POST Receiver is optional, it will not be installed by default but it can be installed with pip.

```
/opt/softwareaccounting/bin/pip install 'softwareaccounting[post-receiver]'
```
