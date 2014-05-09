# coding: utf-8
import magic
import requests
import sys
import time

# from watchdog.observers import Observer
# special case of observer to work with vagrant network fs
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import PatternMatchingEventHandler

from settings import APP_PORT, APP_HOST


class MyHandler(PatternMatchingEventHandler):
    patterns = ["*"]
    ignore_directories = True

    def _post(self, data):
        requests.post(
            'http://%s:%s/items' % (APP_HOST, APP_PORT),
            data=data
        )

    def process(self, event):
        print event.src_path, event.event_type, magic.from_file(event.src_path, mime=True)
        data = {
            'path': event.src_path,
            'type': magic.from_file(event.src_path, mime=True),
            'event_type': event.event_type
        }
        self._post(data)

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        print event.src_path, event.event_type
        self._post({
            'path': event.src_path,
            'event_type': event.event_type
        })

    def on_moved(self, event):
        self.process(event)

if __name__ == '__main__':
    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(MyHandler(), path=args[0] if args else '../watch_here')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()