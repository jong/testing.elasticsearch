import tempfile
import socket
import os
import signal
from shutil import rmtree
from time import sleep
from datetime import datetime

from clom import clom
import requests


__all__ = ['ElasticSearchServer']


def _unused_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    _, port = sock.getsockname()
    sock.close()
    return port


class ElasticSearchServer(object):
    def __init__(self, root=None, cmd=None, foreground=True):
        """
        root:  Root directory for elasticsearch data and logs. This directory will
               contain index data and logs for this instance of elasticsearch.

               http://www.elastic.co/guide/en/elasticsearch/reference/current/setup-dir-layout.html

               If you specify a `root` directory, it will not be removed on
               exit. This gives you a chance to look at logs and preserve (or
               reuse) data.
        cmd: The `elasticsearch` command to run if `elasticsearch` is not in $PATH.

        Usage of this class:

            with ElasticSearch(root="/tmp/testing.elasticsearch") as es:
                es = YourElasticSearchClient(es.uri())

            # elasticsearch terminated here when context exits
        """
        if cmd is None:
            cmd = str(clom.which('elasticsearch').shell())
        self._cmd = cmd

        self._foreground = foreground

        self._use_tmp_dir = False
        self._root = root
        self._es_pid = None
        self._owner_pid = os.getpid()

        self._bind_host = None
        self._bind_port = None

    def __del__(self):
        self.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def uri(self):
        """
        Returns the elasticsearch uri for the testing instance.
        """
        if not self._bind_host or not self._bind_port:
            return
        return "http://{0._bind_host}:{0._bind_port}".format(self)

    def _configure(self):
        """
        Configure this instance of elasticsearch before trying to start the
        server.

        This method exists mainly for unit test hooks so that we can prepare
        to start the elasticsearch server without actually making it start up,
        which takes a relatively long time.
        """
        # setup home dir
        if not self._root:
            self._use_tmp_dir = True
            self._root = tempfile.mkdtemp(suffix='-elastic')

        self._data_path = os.path.join(self._root, 'data')
        self._logs_path = os.path.join(self._root, 'logs')

        self._bind_host = "127.0.0.1"
        self._bind_port = _unused_port()

    def start(self):
        """
        Start the test elasticsearch instance.
        """
        if self._es_pid:
            # already started
            return

        self._configure()

        pid = os.fork()
        if pid == 0:
            # now start elasticsearch
            bind_host = '-Des.network.bind_host=%s' % self._bind_host
            bind_port = '-Des.http.port=%s' % self._bind_port
            data_path = '-Des.path.data=%s' % self._data_path
            logs_path = '-Des.path.logs=%s' % self._logs_path

            # Older version of elastic don't automatically stay in the foreground
            # and need to be instructed with '-f'
            foreground = ""
            if self._foreground:
                foreground = "-f"

            try:
                os.execl(
                    self._cmd,
                    self._cmd,
                    bind_host,
                    bind_port,
                    data_path,
                    logs_path,
                    foreground
                )
            except Exception:
                raise RuntimeError("Could not start elasticsearch.")
        else:
            while True:
                try:
                    result = requests.get(self.uri())
                    if result.status_code == 200:
                        break
                except requests.exceptions.ConnectionError:
                    # service not up yet, ignore.
                    pass

                if os.waitpid(pid, os.WNOHANG)[0] != 0:
                    raise RuntimeError("Failed to start elasticsearch.")

                sleep(0.5)
            self._es_pid = pid

    def stop(self):
        """
        Stop the test elasticsearch instance.
        """
        if self._owner_pid == os.getpid() and self._es_pid:
            self._terminate()
            self._cleanup()

    def _terminate(self):
        os.kill(self._es_pid, signal.SIGTERM)
        killed_at = datetime.now()

        try:
            while (os.waitpid(self._es_pid, os.WNOHANG)):
                if (datetime.now() - killed_at).seconds > 10.0:
                    os.kill(self._es_pid, signal.SIGKILL)
                    raise RuntimeError("Unable to cleanly stop elasticsearch.")
                sleep(0.1)
        except:
            # Child process already terminated.
            pass

        self._bind_host = None
        self._bind_port = None
        self._es_pid = None

    def _cleanup(self):
        if self._use_tmp_dir and os.path.exists(self._root):
            rmtree(self._root, ignore_errors=True)
