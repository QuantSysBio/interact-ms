from setuptools import setup, find_packages

setup(
    name='interact-ms',
    version='2.0rc3',
    description='Interactive GUI for mass spectrometry identification and analysis.',
    author='John Cormican, Sahil Khan, Juliane Liepe, Manuel S. Pereira',
    author_email='juliane.liepe@mpinat.mpg.de',
    include_package_data=True,
	license_files = ('LICENSE.txt',),
    long_description=open('README.md', mode='r', encoding='UTF-8').read(),
    long_description_content_type='text/markdown',
    py_modules=[
        'interact_ms',
    ],
    entry_points={
        'console_scripts': [
            'interact-ms=interact_ms.api:main',
        ]
    },
    packages=find_packages(),
    python_requires='>=3.11',
    install_requires=[
        'piscecs-ms==0.3',
        'blinker==1.6.2',
        'click==8.1.3',
        'flask==2.3.2',
        'flask_cors==3.0.10',
        'itsdangerous==2.1.2',
        'MarkupSafe==2.1.3',
        'psutil==5.9.6',
        'Werkzeug==3.0.1',
        'six==1.16.0',
    ],
    project_urls={
        'Homepage': 'https://github.com/QuantSysBio/interact-ms',
        'Tracker': 'https://github.com/QuantSysBio/interact-ms/issues',
    },
    zip_safe=False,
)
