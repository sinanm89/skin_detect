"""Skinny, measuring nudity and skin percentage in images.

This module measures the skin coefficient of images in order to determine
if the people in it are nude or not.

Example:
    The module is a twistd plugin so it can be run by::

        $ twistd -n skinny

Flags:
    --port -p (int): Port number for the plugin to run. Defaults to 8000
"""
