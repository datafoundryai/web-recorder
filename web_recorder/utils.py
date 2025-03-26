from importlib import resources


def get_js_path(js_filename):
    """Get path to a JS file in the package."""
    try:
        # For Python 3.9+
        with resources.files("web_recorder.rrweb").joinpath(js_filename) as path:
            return str(path)
    except Exception:
        # For older Python versions
        with resources.path("web_recorder.rrweb", js_filename) as path:
            return str(path)
