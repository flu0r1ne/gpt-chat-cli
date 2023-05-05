import setuptools

setuptools.setup(
    name='gpt-chat-cli',
    version='0.0.1',
    entry_points = {
        'console_scripts': ['gpt-chat-cli=gpt_chat_cli.gcli:main'],
    },
    author='Flu0r1ne',
    description='A simple ChatGPT CLI',
    packages=['gpt_chat_cli'],
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'openai >= 0.27.6',
    ],
    python_requires='>=3.7'
)
