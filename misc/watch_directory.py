#!/usr/bin/env python3
import inotify

watcher = inotify.adapters.Inotify()

watcher.add_watch('../scraper/data')

for event in watcher.event_gen(yield_nones=False):
    (_, type_names, path, filename) = event

    print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(path, filename, type_names))
