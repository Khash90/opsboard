from prometheus_client import multiprocess


def child_exit(server, worker):
    """
    Remove Prometheus metric files belonging to workers
    that have exited.
    """
    multiprocess.mark_process_dead(worker.pid)
