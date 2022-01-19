from setuptools import setup, find_packages
setup_requires = ['setuptools']

try:
    result = setup(
        name='zapzap',
        version='1.0',
        author='rtosta',
        author_email='rafa.ecomp@gmail.com',
        description='Web App for Whatsapp',
        license='GPLv3+',
        packages=['zapzap'],
        setup_requires=setup_requires,
        entry_points={'gui_scripts': ['zapzap = zapzap.__main__:main']},
        keywords='zapzap whatsapp client web app',
        packages=find_packages(),
        classifiers=[
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Topic :: Office/Business',
            'Programming Language :: Python :: 3 :: Only'
        ],
        install_requires=[
            'PySide6',
        ]
    )
except:
    print('deu erro!')
