from setuptools import setup


setup(
    name='testing.elasticsearch',
    packages=['testing'],
    package_dir={'': 'src'},
    version=open('VERSION.txt').read().strip(),
    author='Jon Gartman',
    author_email='jongartman@gmail.com',
    url='https://github.com/jong/testing.elasticsearch',
    keywords=['testing', 'elasticsearch'],
    license='MIT',
    description='Automatically sets up an elasticsearch instance in a temporary directory, and destroys it after testing',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    long_description=open('README.rst').read(),
    install_requires=[
        "requests>=2.6.0",
    ],
)
