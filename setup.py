import os
from distutils.core import setup
from distutils.command.install import install
from distutils.command.install_data import install_data

from sams import __version__

# nasty global for relocation
RELOCATE = None

class InstallSams(install):

    def finalize_options(self):
        install.finalize_options(self)

        global RELOCATE ; RELOCATE = self.home

class InstallDataSams(install_data):
    # this class is used to filter out data files which should not be overwritten

    def finalize_options(self):
        install_data.finalize_options(self)

        # relocation
        if RELOCATE:
            print('relocating to %s' % RELOCATE)
            for (prefix, files) in reversed(self.data_files):
                if prefix.startswith('/'):
                    new_prefix = os.path.join(RELOCATE, prefix[1:])
                    self.data_files.remove((prefix, files))
                    self.data_files.append((new_prefix, files))

        # check that we don't overwrite /etc files
        for (prefix, files) in reversed(self.data_files):
            if prefix.startswith(os.path.join(RELOCATE or '/', 'etc')):
                for basefile in files:
                    fn = os.path.join(prefix, os.path.basename(basefile))
                    if os.path.exists(fn):
                        print('Skipping installation of %s (already exists)' % fn)
                        files.remove(basefile)
            if not files:
                self.data_files.remove((prefix, []))


cmdclasses = {'install': InstallSams, 'install_data': InstallDataSams} 

setup(name='sams-software-accounting',
      version=__version__,
      description='SAMS Software Accounting',
      author='Magnus Jonsson',
      author_email='magnus@hpc2n.umu.se',
      url='http://www.hpc2n.umu.se/',      
      packages=['sams','sams.aggregator','sams.loader','sams.output','sams.pidfinder','sams.sampler',
                'sams.backend','sams.software','sams.xmlwriter'],
      scripts = ['sams-aggregator.py','sams-collector.py','sams-post-receiver.py',
                 'sams-post-receiver.py','sams-software-extractor.py','sams-software-updater.py',
                 'extras/sgas-sa-registrant/bin/sgas-sa-registrant'],
      install_requires = [
          'Flask',
          'httplib2',
          'Twisted',
          'PyYAML',
      ],
      cmdclass = cmdclasses,

      data_files = [
        ('/etc/sams', ['sams-aggregator.yaml']),
        ('/etc/sams', ['sams-collector.yaml']),
        ('/etc/sams', ['sams-post-receiver.yaml']),
        ('/etc/sams', ['sams-software-extractor.yaml']),
        ('/etc/sams', ['sams-software-updater.yaml']),
        ('/etc/sams', ['sams-post-receiver.yaml']),
        ('/etc/sams', ['extras/sgas-sa-registrant/etc/sgas-sa-registrant.conf']),
      ]

)
