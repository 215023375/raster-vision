# flake8: noqa

from os import path as op
import io
from urllib.parse import urlparse

from setuptools import (setup, find_namespace_packages)

here = op.abspath(op.dirname(__file__))
with io.open(op.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')


def create_git_install_requires(all_requirements: list) -> list:
    git_install_requires = []
    # if git+, get package name and add below into requires list
    # install_requires = [
    #   'some-pkg @ git+ssh://git@github.com/someorgname/pkg-repo-name@v1.1#egg=some-pkg',
    # ]
    for req in all_requirements:
        if 'git+' not in req:
            continue
        # req is git url
        # git+https://github.com/215023375/raster-vision.git@external-config-registry-no-jittor#egg=rastervision_pipeline&subdirectory=rastervision_pipeline
        parsed_url = urlparse(req)
        url_fragments = parsed_url.fragment.split('&')
        package_name = [fragment for fragment in url_fragments if 'egg=' in fragment][0].replace("egg=", "")
        
        git_install_requires.append(f"{package_name} @ {req}")

    return git_install_requires


install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
all_install_requires = [*install_requires, *create_git_install_requires(all_reqs)]

name = 'rastervision_pytorch_backend'
version = '0.13.2'
description = 'A rastervision plugin that adds PyTorch backends for rastervision.core pipelines'

setup(
    name=name,
    version=version,
    description=description,
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
    packages=find_namespace_packages(exclude=['integration_tests*', 'tests*']),
    install_requires=all_install_requires,
    zip_safe=False)
