from os import path, listdir


class AddonsManager:
    """
    Gerencia os addons em js que serão injetados no website
    """
    js_addons = None

    @staticmethod
    def load_addons():
        """
        Carrega os arquivos js que serão injetados no website
        """
        if AddonsManager.js_addons is not None:
            return AddonsManager.js_addons

        curr_dir = path.dirname(path.abspath(__file__))
        js_dir = path.join(curr_dir, '..', 'js')
        AddonsManager.js_addons = []

        if path.isdir(js_dir):
            for file in listdir(js_dir):
                if file.endswith('.js'):
                    filepath = path.join(js_dir, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        AddonsManager.js_addons.append(f.read())

        print('Addons carregados:')
        print(AddonsManager.js_addons)

        return AddonsManager.js_addons

    @staticmethod
    def inject_addons(page):
        """
        Injeta os addons em js na página
        """
        js_addons = AddonsManager.load_addons()
        for addon in js_addons:
            page.runJavaScript(addon)
