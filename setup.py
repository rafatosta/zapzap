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
                  'zapzap.controllers.main_window_components',
                  'zapzap.controllers.main_window_decoration',
                  'zapzap.engine',
                  'zapzap.services',
                  'zapzap.theme',
                  'zapzap.view',
                  'zapzap.model'],
        include_package_data=True,
        package_data={'zapzap': ['assets/icons/app/*/*.svg',
                                 'assets/icons/app/*/*.png',
                                 'assets/icons/titlebar_buttons/*/*/*.svg',
                                 'assets/icons/banners/*.svg',
                                 'assets/icons/banners/*.png',
                                 'assets/segoe-ui/*.ttf',
                                 'po/*/LC_MESSAGES/*.mo']},
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
