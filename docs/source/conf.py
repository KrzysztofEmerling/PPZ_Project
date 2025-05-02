import os
import sys

sys.path.insert(0, os.path.abspath('../../app'))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Sudoku-sweeper'
copyright = '2025, Agnieszka Głowacka, Martyna Trębacz, Oliwia Skucha, Jakub Rogoża, Krzysztof Emerling, Szymon Duda'
author = 'Agnieszka Głowacka, Martyna Trębacz, Oliwia Skucha, Jakub Rogoża, Krzysztof Emerling, Szymon Duda'
release = 'v0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # dla Pythona
    'sphinx_js',           # dla JS
]

js_source_path = '../../app/static'

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
