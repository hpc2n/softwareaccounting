# Installation

In most cases it should be possible to install Software Accounting as long as Python is already installed.

## Virtual environment

Using a Python virtual environment makes it simple to install and update Software Accounting, and its dependencies. Create the Python virtual environment where you want it installed, and install Software Accounting using pip. Pip will install Software Accounting from the Python Packaging Index (PyPI).

```
python -m venv --upgrade-deps /opt/softwareaccounting
/opt/softwareaccounting/bin/pip install softwareaccounting
```

You can then update Software Accounting and its dependencies as new releases are published to PyPI.

```
/opt/softwareaccounting/bin/pip install --upgrade --upgrade-strategy=eager softwareaccounting
```

The POST Receiver is optional, add it as an extras if needed when installing.

```
/opt/softwareaccounting/bin/pip install 'softwareaccounting[post-receiver]'
```
