from setuptools import setup
import zapzap
setup_requires = ['setuptools']
try:
    setup(
        name=zapzap.__appname__.lower(),
        version=zapzap.__version__,
        author=zapzap.__author__,
        author_email=zapzap.__email__,
        description=zapzap.__comment__,
        url=zapzap.__website__,
        license='GPLv3+',
        packages=['zapzap',
                  'zapzap.controllers',
                  'zapzap.engine',
                  'zapzap.services',
                  'zapzap.view']
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
