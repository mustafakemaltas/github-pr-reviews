from setuptools import setup, find_packages

setup(
    name='github-pr-list',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyInquirer',
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'grev=githubprreviewer.main:main',
        ],
    },
    # Additional metadata
    author='Mustafa Kemal Taş',
    author_email='dev.mekate@gmail.com',
    description='A tool for listing and reviewing GitHub PRs',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/tasmustafakemal/github-pr-list',  # Optional
)
