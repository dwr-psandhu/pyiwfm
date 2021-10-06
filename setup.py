from setuptools import setup
import versioneer

requirements = [
  'pandas',
  'xarray',
  'scikit-learn',
  'statsmodels',
  'dask',
  'numba',
  'pyepsg',
  'geopandas',
  'holoviews',
  'hvplot',
  'matplotlib',
  'bokeh',
  'geoviews',
  'ipyleaflet',
  'spatialpandas',
]

setup(
    name='pyiwfm',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Python utilities for IWFM",
    license="MIT",
    author="Nicky Sandhu",
    author_email='psandhu@water.ca.gov',
    url='https://github.com/dwr_psandhu/pyiwfm',
    packages=['pyiwfm'],
    entry_points={
        'console_scripts': [
            'pyiwfm=pyiwfm.cli:cli'
        ]
    },
    install_requires=requirements,
    keywords='pyiwfm',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
