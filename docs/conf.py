# -- Paramètres généraux ---------------------------------------------------

project = 'Prédiction Forex '
copyright = '2025'
author = 'Yassine_Ouissam'

language = 'fr'

# -- Extensions ------------------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx.ext.githubpages',
]

# -- Thème HTML ------------------------------------------------------------

html_theme = 'furo'
html_title = "Documentation du Dashboard IA Forex"
html_static_path = ['_static']
html_logo = '_static/logo.png'  # optionnel si tu ajoutes un logo

html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#0066cc",
        "color-brand-content": "#333333",
    },
}

html_static_path = ['_static']

