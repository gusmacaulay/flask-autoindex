import os.path
from flask import *
from werkzeug import cached_property
from jinja2 import FileSystemLoader
from .entry import *
from . import icons


__dir__ = os.path.abspath(os.path.dirname(__file__))
__name__ = "__autoindex__"


class AutoIndex(Module):

    def _register_autoindex(self, state):
        """Registers a magic module named __autoindex__."""
        if __name__ not in state.app.modules:
            state.app.modules[__name__] = self

    def __init__(self, import_name, browse_root=None, **options):
        """Initializes an autoindex module."""
        super(AutoIndex, self).__init__(import_name, **options)
        self._record(self._register_autoindex)
        self.browse_root = browse_root
        for rule in "/", "/<path:path>":
            self.browse = self.route(rule)(self.browse)

    def browse(self, path="."):
        """Browses the files in path."""
        abspath = os.path.join(self.browse_root, path)
        if os.path.isdir(abspath):
            sort_by = request.args.get("sort_by", "name")
            entries = Entry.browse(path,
                                   root=self.browse_root,
                                   sort_by=sort_by)
            titlepath = "/" + ("" if path == "." else path)
            return render_template("{0}/browse.html".format(self.name),
                                   path=titlepath,
                                   entries=entries,
                                   sort_by=sort_by)
        elif os.path.isfile(abspath):
            return send_file(abspath)
        else:
            return abort(404)

    def send_static_file(self, filename):
        """Serves a static file when it is in the autoindex's static directory.
        Otherwise it serve from module's static directory.
        """
        module_static = os.path.join(__dir__, "static")
        if os.path.isfile(os.path.join(module_static, filename)):
            return send_from_directory(module_static, filename)
        else:
            return super(AutoIndex, self).send_static_file(filename)

    @cached_property
    def jinja_loader(self):
        """Merges a pre-loaded templates folder."""
        paths = [os.path.join(path, "templates") \
                 for path in __dir__, self.root_path]
        return FileSystemLoader(paths)

