class DarkReaderBridge:
    _instance = None
    _profile = None

    _extension_id = None
    _url = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, profile, extension_id):
        if not self._initialized:
            self._initialized = True

            self._extension_id = extension_id
            self._url = f"chrome-extension://{extension_id}/popup.html"

            DarkReaderBridge._profile = profile.extensionManager()

    @staticmethod
    def set_theme_colors(colors: list[int]):
        """
        Applies custom colors to the Dark Reader theme.
        """

        # We handle None values by converting them to 'null' for JavaScript,
        # otherwise we wrap the string in quotes.
        js_scrollbar = f'"{colors[3]}"' if colors[3] else "null"
        js_selection = f'"{colors[4]}"' if colors[4] else "null"

        # First we force the dark mode (t.mode = 1), then specify the color for
        # each of the 4 variables available.
        js_code = f"""
        chrome.storage.local.get(['theme'], (result) => {{
            if (result.theme) {{
                let t = result.theme;
                
                t.mode = 1; 
    
                t.darkSchemeBackgroundColor = "{colors[1]}";
                t.darkSchemeTextColor = "{colors[2]}";
                t.scrollbarColor = {js_scrollbar};
                t.selectionColor = {js_selection};
    
                chrome.storage.local.set({{theme: t}});
            }}
        }});
        """
        DarkReaderBridge._profile.page().runJavaScript(js_code)