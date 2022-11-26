# flake8: noqa

from os import path as op
import os
import json
import io
import re
from setuptools import (setup, find_namespace_packages)
from imp import load_source
from urllib.parse import urlparse

here = op.abspath(op.dirname(__file__))
__version__ = '0.13.2'

# get the dependencies and installs
with io.open(op.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

# The RTD build environment fails with the reqs in bad_reqs.
if 'READTHEDOCS' in os.environ:
    bad_reqs = ['pyproj', 'h5py']
    all_reqs = list(
        filter(lambda r: r.split('==')[0] not in bad_reqs, all_reqs))


def create_git_install_requires(all_requirements: list) -> list:
    """
    https://stackoverflow.com/questions/32688688/how-to-write-setup-py-to-include-a-git-repository-as-a-dependency
    :param all_requirements:
    :return:
    """

    git_install_requires = []
    # if git+, get package name and add below into requires list
    # install_requires = [
    #   'some-pkg @ git+ssh://git@github.com/someorgname/pkg-repo-name@v1.1#egg=some-pkg',
    # ]
    for req in all_requirements:
        if 'git+' not in req:
            continue
        # req is git url
        # git+https://github.com/215023375/raster-vision.git@mainline#egg=rastervision_pipeline&subdirectory=rastervision_pipeline
        parsed_url = urlparse(req)
        url_fragments = parsed_url.fragment.split('&')
        package_name = [fragment for fragment in url_fragments if 'egg=' in fragment][0].replace("egg=", "")
        
        git_install_requires.append(f"{package_name} @ {req}")

    return git_install_requires


install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
all_install_requires = [*install_requires, *create_git_install_requires(all_reqs)]


def replace_images(readme):
    """Replaces image links in the README with static links to
    the GitHub release branch."""
    release_branch = '.'.join(__version__.split('.')[:2])
    r = r'\((docs/)(.*\.png)'
    rep = (r'(https://raw.githubusercontent.com/azavea/raster-vision/'
           '{}/docs/\g<2>'.format(release_branch))

    return re.sub(r, rep, readme)


# del extras_require['feature-extraction']

setup(
    name='rastervision',
    version=__version__,
    description='An open source framework for deep learning '
    'on satellite and aerial imagery',
    long_description=replace_images(open('README.md').read()),
    long_description_content_type='text/markdown',
    url='https://github.com/215023375/raster-vision',
    author='Azavea',
    author_email='info@azavea.com',
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    keywords=
    'raster deep-learning ml computer-vision earth-observation geospatial geospatial-processing',
    packages=[],
    include_package_data=True,
    install_requires=all_install_requires)
