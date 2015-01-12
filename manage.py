#!/usr/bin/env python
import sys

try:
    if sys.argv[1] == 'admin':
        from website.admin import app
    else:
        from website.frontend import app
except IndexError:
    from website.frontend import app

app.run(host='0.0.0.0', port=80, use_reloader=True)