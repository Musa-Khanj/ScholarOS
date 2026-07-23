from scholaros.scheduler import Scheduler
from scholaros.scheduler.task import Priority, Task


def test_submit():
    scheduler = Scheduler()

    called = []

    scheduler.submit(Task(Priority.NORMAL, func=lambda: called.append(True)))

    task = scheduler.queue.get()
    task.func()

    assert called == [True]