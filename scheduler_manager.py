from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR


class SchedulerManager:
    """Class to manage scheduling jobs."""
    def __init__(self, job_function, interval_seconds=5):
        """
        Initialize the SchedulerManager.
        :param job_function: The function to execute periodically.
        :param interval_seconds: Interval in seconds for job execution.
        """
        self.scheduler = BackgroundScheduler()
        self.job_function = job_function
        self.interval_seconds = interval_seconds

    def start(self):
        """Start the scheduler and add the periodic job."""
        self.scheduler.add_job(self.job_function, "interval", seconds=self.interval_seconds)
        self.scheduler.add_listener(self.error_listener, EVENT_JOB_ERROR)
        self.scheduler.start()
        print("Scheduler started. Press Ctrl+C to exit.")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        print("Scheduler stopped.")

    @staticmethod
    def error_listener(event):
        """Log errors that occur during job execution."""
        if event.exception:
            print(f"Job crashed: {event.exception}")
        else:
            print("Job executed successfully.")
