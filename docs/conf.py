import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

project = 'MindPy'
author = 'Anuja Gajaweera'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',  # Pulls documentation from your docstrings
    'sphinx.ext.napoleon', # Supports Google/NumPy style docstrings
]

html_theme = 'sphinx_rtd_theme'
