from setuptools import setup
setup_requires = ['setuptools']

try:
    setup(
        name='zapzap',
        version='1.0',
        author='Rafael Tosta',
        author_email='rafa.ecomp@gmail.com',
        description='Web App for Whatsapp',
        license='GPLv3+',
        packages=['zapzap'],
        setup_requires=setup_requires,
        entry_points={'gui_scripts': ['zapzap = zapzap.__main__:main']},
        keywords='zapzap whatsapp client web app',
        classifiers=[
            'Environment :: X11 Applications :: Qt',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Topic :: Office/Business',
            'Programming Language :: Python :: 3 :: Only'
        ]
    )
except Exception as e:
    print(e)
