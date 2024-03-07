from setuptools import setup

try:
    from testr.setup_helper import cmdclass
except ImportError:
    cmdclass = {}

setup(name='alerts',
      author='Malgosia Sobolewska',
      description='Chandra MTA Radiation Alerts',
      author_email='msobolewska@cfa.harvard.edu',
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      zip_safe=False,
      packages=['radalerts', 'radalerts.alerts', 'radalerts.radpars', 'radalerts.tests'],
      tests_require=['pytest'],
      cmdclass=cmdclass,
      )
