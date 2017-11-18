from aoiklivereload import LiveReloader


def live_reload():
    reloader = LiveReloader()
    reloader.start_watcher_thread()
