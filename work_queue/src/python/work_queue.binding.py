## @package WorkQueuePython
#
# Python Work Queue bindings.
#
# The objects and methods provided by this package correspond to the native
# C API in @ref work_queue.h.
#
# The SWIG-based Python bindings provide a higher-level interface that
# revolves around the following objects:
#
# - @ref work_queue::WorkQueue
# - @ref work_queue::Task

import copy
import os

def set_debug_flag(*flags):
    for flag in flags:
        cctools_debug_flags_set(flag)

cctools_debug_config('work_queue_python')

##
# Python Task object
#
# This class is used to create a task specification.
class Task(_object):

    ##
    # Create a new task specification.
    #
    # @param self       Reference to the current task object.
    # @param command    The shell command line to be exected by the task.
    def __init__(self, command):
        self._task = None

        try:
            self._task = work_queue_task_create(command)
            if not self._task:
                raise
        except:
            raise Exception('Unable to create internal Task structure')

    def __del__(self):
        if self._task:
            work_queue_task_delete(self._task)

    @staticmethod
    def _determine_file_flags(flags, cache):
        if flags is None:
            flags = WORK_QUEUE_CACHE

        if cache:
            flags |= WORK_QUEUE_CACHE
        else:
            flags &= ~WORK_QUEUE_CACHE

        return flags

    ##
    # Return a copy of this task
    #
    def clone(self):
        """Return a (deep)copy this task that can also be submitted to the WorkQueue."""
        new = copy.copy(self)
        new._task = work_queue_task_clone(self._task)
        return new


    ##
    # Set the command to be executed by the task.
    #
    # @param self       Reference to the current task object.
    # @param command    The command to be executed.
    def specify_command(self, command):
        return work_queue_task_specify_command(self._task, command)

    ##
    # Set the worker selection algorithm for task.
    #
    # @param self       Reference to the current task object.
    # @param algorithm  One of the following algorithms to use in assigning a
    #                   task to a worker. See @ref work_queue_schedule_t for
    #                   possible values.
    def specify_algorithm(self, algorithm):
        return work_queue_task_specify_algorithm(self._task, algorithm)

    ##
    # Attach a user defined logical name to the task.
    #
    # @param self       Reference to the current task object.
    # @param tag        The tag to attach to task.
    def specify_tag(self, tag):
        return work_queue_task_specify_tag(self._task, tag)

    ##
    # Indicate that the task would be optimally run on a given host.
    #
    # @param self       Reference to the current task object.
    # @param hostname   The hostname to which this task would optimally be sent.
    def specify_preferred_host(self, hostname):
        return work_queue_task_specify_preferred_host(self._task, hostname)

    ##
    # Add a file to the task.
    #
    # @param self           Reference to the current task object.
    # @param local_name     The name of the file on local disk or shared filesystem.
    # @param remote_name    The name of the file at the execution site.
    # @param type           Must be one of the following values: @ref WORK_QUEUE_INPUT or @ref WORK_QUEUE_OUTPUT
    # @param flags          May be zero to indicate no special handling, or any
    #                       of the @ref work_queue_file_flags_t or'd together The most common are:
    #                       - @ref WORK_QUEUE_NOCACHE
    #                       - @ref WORK_QUEUE_CACHE
    #                       - @ref WORK_QUEUE_WATCH
    # @param cache          Legacy parameter for setting file caching attribute.  By default this is enabled.
    #
    # For example:
    # @code
    # # The following are equivalent
    # >>> task.specify_file("/etc/hosts", type=WORK_QUEUE_INPUT, flags=WORK_QUEUE_NOCACHE)
    # >>> task.specify_file("/etc/hosts", "hosts", type=WORK_QUEUE_INPUT, cache=false)
    # @endcode
    def specify_file(self, local_name, remote_name=None, type=None, flags=None, cache=True):
        if remote_name is None:
            remote_name = os.path.basename(local_name)

        if type is None:
            type = WORK_QUEUE_INPUT

        flags = Task._determine_file_flags(flags, cache)
        return work_queue_task_specify_file(self._task, local_name, remote_name, type, flags)

    ##
    # Add a file piece to the task.
    #
    # @param self           Reference to the current task object.
    # @param local_name     The name of the file on local disk or shared filesystem.
    # @param remote_name    The name of the file at the execution site.
    # @param start_byte     The starting byte offset of the file piece to be transferred.
    # @param end_byte       The ending byte offset of the file piece to be transferred.
    # @param type           Must be one of the following values: @ref WORK_QUEUE_INPUT or @ref WORK_QUEUE_OUTPUT
    # @param flags          May be zero to indicate no special handling, or any
    #                       of the @ref work_queue_file_flags_t or'd together The most common are:
    #                       - @ref WORK_QUEUE_NOCACHE
    #                       - @ref WORK_QUEUE_CACHE
    # @param cache          Legacy parameter for setting file caching attribute.  By default this is enabled.
    def specify_file_piece(self, local_name, remote_name=None, start_byte=0, end_byte=0, type=None, flags=None, cache=True):
        if remote_name is None:
            remote_name = os.path.basename(local_name)

        if type is None:
            type = WORK_QUEUE_INPUT

        flags = Task._determine_file_flags(flags, cache)
        return work_queue_task_specify_file_piece(self._task, local_name, remote_name, start_byte, end_byte, type, flags)

    ##
    # Add a input file to the task.
    #
    # This is just a wrapper for @ref specify_file with type set to @ref WORK_QUEUE_INPUT.
    def specify_input_file(self, local_name, remote_name=None, flags=None, cache=True):
        return self.specify_file(local_name, remote_name, WORK_QUEUE_INPUT, flags, cache)

    ##
    # Add a output file to the task.
    #
    # This is just a wrapper for @ref specify_file with type set to @ref WORK_QUEUE_OUTPUT.
    def specify_output_file(self, local_name, remote_name=None, flags=None, cache=True):
        return self.specify_file(local_name, remote_name, WORK_QUEUE_OUTPUT, flags, cache)

    ##
    # Add a directory to the task.
    # @param self           Reference to the current task object.
    # @param local_name     The name of the directory on local disk or shared filesystem. Optional if the directory is empty.
    # @param remote_name    The name of the directory at the remote execution site.
    # @param type           Must be one of the following values: @ref WORK_QUEUE_INPUT or @ref WORK_QUEUE_OUTPUT
    # @param flags          May be zero to indicate no special handling, or any
    #                       of the @ref work_queue_file_flags_t or'd together The most common are:
    #                       - @ref WORK_QUEUE_NOCACHE
    #                       - @ref WORK_QUEUE_CACHE
    # @param recursive      Indicates whether just the directory (0) or the directory and all of its contents (1) should be included.
    # @param cache          Legacy parameter for setting file caching attribute.  By default this is enabled.
    # @return 1 if the task directory is successfully specified, 0 if either of @a local_name, or @a remote_name is null or @a remote_name is an absolute path.
    def specify_directory(self, local_name, remote_name=None, type=None, flags=None, recursive=0, cache=True):
        if remote_name is None:
            remote_name = os.path.basename(local_name)

        if type is None:
            type = WORK_QUEUE_INPUT

        flags = Task._determine_file_flags(flags, cache)
        return work_queue_task_specify_directory(self._task, local_name, remote_name, type, flags, recursive)

    ##
    # Add an input bufer to the task.
    #
    # @param self           Reference to the current task object.
    # @param buffer         The contents of the buffer to pass as input.
    # @param remote_name    The name of the remote file to create.
    # @param flags          May take the same values as @ref specify_file.
    # @param cache          Legacy parameter for setting file caching attribute.  By default this is enabled.
    def specify_buffer(self, buffer, remote_name, flags=None, cache=True):
        flags = Task._determine_file_flags(flags, cache)
        return work_queue_task_specify_buffer(self._task, buffer, len(buffer), remote_name, flags)

    ##
    # Indicate the number of cores required by this task.
    def specify_cores( self, cores ):
        return work_queue_task_specify_cores(self._task,cores)

    ##
    # Indicate the memory (in MB) required by this task.
    def specify_memory( self, memory ):
        return work_queue_task_specify_memory(self._task,memory)

    ##
    # Indicate the disk space (in MB) required by this task.
    def specify_disk( self, disk ):
        return work_queue_task_specify_disk(self._task,disk)

    ##
    # Indicate the the priority of this task (larger means better priority, default is 0).
    def specify_priority( self, priority ):
        return work_queue_task_specify_priority(self._task,priority)

    # Indicate the maximum end time (in seconds from the Epoch) of this task.
    def specify_end_time( self, seconds ):
        return work_queue_task_specify_end_time(self._task,seconds)

    # Set this environment variable before running the task.
    # If value is None, then variable is unset.
    def specify_environment_variable( self, name, value = None ):
        return work_queue_task_specify_enviroment_variable(self._task,name,value)

    ##
    # Get the user-defined logical name for the task.
    #
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.tag
    # @endcode
    @property
    def tag(self):
        return self._task.tag

    ##
    # Get the shell command executed by the task.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.command
    # @endcode
    @property
    def command(self):
        return self._task.command_line

    ##
    # Get the priority of the task.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.priority
    # @endcode
    @property
    def priority(self):
        return self._task.priority

    ##
    # Get the algorithm for choosing worker to run the task.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.algorithm
    # @endcode
    @property
    def algorithm(self):
        return self._task.worker_selection_algorithm

    ##
    # Get the standard output of the task. Must be called only after the task
	# completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.output
    # @endcode
    @property
    def output(self):
        return self._task.output

    ##
    # Get the task id number. Must be called only after the task was submitted.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.id
    # @endcode
    @property
    def id(self):
        return self._task.taskid

    ##
    # Get the exit code of the command executed by the task. Must be called only
	# after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.return_status
    # @endcode
    @property
    def return_status(self):
        return self._task.return_status

    ##
    # Get the result of the task, such as successful, missing file, etc.
    # See @ref work_queue_result_t for possible values.  Must be called only
    # after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.result
    # @endcode
    @property
    def result(self):
        return self._task.result

    ##
    # Get the number of times the task has been resubmitted internally.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.total_submissions
    # @endcode
    @property
    def total_submissions(self):
        return self._task.total_submissions

    ##
    # Get the address and port of the host on which the task ran.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.host
    # @endcode
    @property
    def host(self):
        return self._task.host

    ##
    # Get the name of the host on which the task ran.
	# Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.hostname
    # @endcode
    @property
    def hostname(self):
        return self._task.hostname

    ##
    # Get the time at which this task was submitted.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.submit_time
    # @endcode
    @property
    def submit_time(self):
        return self._task.time_task_submit

    ##
    # Get the time at which this task was finished.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.finish_time
    # @endcode
    @property
    def finish_time(self):
        return self._task.time_task_finish

    ##
    # Get the time spent in upper-level application (outside of work_queue_wait).
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.app_delay
    # @endcode
    @property
    def app_delay(self):
        return self._task.time_app_delay

    ##
    # Get the time at which the task started to transfer input files.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.send_input_start
    # @endcode
    @property
    def send_input_start(self):
        return self._task.time_send_input_start

    ##
    # Get the time at which the task finished transferring input files.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.send_input_finish
    # @endcode
    @property
    def send_input_finish(self):
        return self._task.time_send_input_finish

    ##
    # The time at which the task began.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.execute_cmd_start
    # @endcode
    @property
    def execute_cmd_start(self):
        return self._task.time_execute_cmd_start

    ##
    # Get the time at which the task finished (discovered by the master).
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.execute_cmd_finish
    # @endcode
    @property
    def execute_cmd_finish(self):
        return self._task.time_execute_cmd_finish

    ##
	# Get the time at which the task started to transfer output files.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.receive_output_start
    # @endcode
    @property
    def receive_output_start(self):
        return self._task.time_receive_output_start

    ##
    # Get the time at which the task finished transferring output files.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.receive_output_finish
    # @endcode
    @property
    def receive_output_finish(self):
        return self._task.time_receive_output_finish

    ##
    # Get the number of bytes received since task started receiving input data.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.total_bytes_received
    # @endcode
    @property
    def total_bytes_received(self):
        return self._task.total_bytes_received

    ##
    # Get the number of bytes sent since task started sending input data.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.total_bytes_sent
    # @endcode
    @property
    def total_bytes_sent(self):
        return self._task.total_bytes_sent

    ##
    # Get the number of bytes transferred since task started transferring input data.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.total_bytes_transferred
    # @endcode
    @property
    def total_bytes_transferred(self):
        return self._task.total_bytes_transferred

    ##
    # Get the time comsumed in microseconds for transferring total_bytes_transferred.
	# Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.total_transfer_time
    # @endcode
    @property
    def total_transfer_time(self):
        return self._task.total_transfer_time

    ##
    # Get the time spent in microseconds for executing the command on the worker.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.cmd_execution_time
    # @endcode
    @property
    def cmd_execution_time(self):
        return self._task.cmd_execution_time

    ##
    # Get the time spent in microseconds for executing the command on any worker.
    # Must be called only after the task completes execution.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print t.total_cmd_execution_time
    # @endcode
    @property
    def total_cmd_execution_time(self):
        return self._task.total_cmd_execution_time

    ##
    # Get the resources measured for the task execution if resource monitoring is enabled.
    # Must be called only after the task completes execution.
    # @code
    # >>> print t.resources_measured('resident_memory')
    # @endcode
    @property
    def resources_measured(self):
        if not self._task.resources_measured:
            return None

        return self._task.resources_measured

##
# Python Work Queue object
#
# This class uses a dictionary to map between the task pointer objects and the
# @ref work_queue::Task.
class WorkQueue(_object):
    ##
    # Create a new work queue.
    #
    # @param self       Reference to the current work queue object.
    # @param port       The port number to listen on. If zero is specified, then the default is chosen, and if -1 is specified, a random port is chosen.
    # @param name       The project name to use.
    # @param catalog    Whether or not to enable catalog mode.
    # @param exclusive  Whether or not the workers should be exclusive.
    # @param shutdown   Automatically shutdown workers when queue is finished. Disabled by default.
    #
    # @see work_queue_create    - For more information about environmental variables that affect the behavior this method.
    def __init__(self, port=WORK_QUEUE_DEFAULT_PORT, name=None, catalog=False, exclusive=True, shutdown=False):
        self._shutdown   = shutdown
        self._work_queue = None
        self._stats      = None
        self._stats_hierarchy = None
        self._task_table = {}

        try:
            self._work_queue = work_queue_create(port)
            self._stats      = work_queue_stats()
            self._stats_hierarchy = work_queue_stats()
            if not self._work_queue:
                raise Exception('Could not create work_queue on port %d' % port)

            if name:
                work_queue_specify_name(self._work_queue, name)

            work_queue_specify_master_mode(self._work_queue, catalog)
        except Exception, e:
            raise Exception('Unable to create internal Work Queue structure: %s' % e)

    def __free_queue(self):
        if self._work_queue:
            if self._shutdown:
                self.shutdown_workers(0)
            work_queue_delete(self._work_queue)

    def __exit__(self):
        self.__free_queue()

    def __del__(self):
        self.__free_queue()

    ##
    # Get the project name of the queue.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print q.name
    # @endcode
    @property
    def name(self):
        return work_queue_name(self._work_queue)

    ##
    # Get the listening port of the queue.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print q.port
    # @endcode
    @property
    def port(self):
        return work_queue_port(self._work_queue)

    ##
    # Get queue statistics.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print q.stats
    # @endcode
    # The fields in @ref work_queue_stats can also be individually accessed through this call. For example:
    # @code
    # >>> print q.stats.workers_busy
    # @endcode
    @property
    def stats(self):
        work_queue_get_stats(self._work_queue, self._stats)
        return self._stats

    ##
    # Get worker hierarchy statistics.
    # @a Note: This is defined using property decorator. So it must be called without parentheses
    # (). For example:
    # @code
    # >>> print q.stats
    # @endcode
    # The fields in @ref work_queue_stats can also be individually accessed through this call. For example:
    # @code
    # >>> print q.stats.workers_busy
    # @endcode
    @property
    def stats_hierarchy(self):
        work_queue_get_stats_hierarchy(self._work_queue, self._stats_hierarchy)
        return self._stats_hierarchy

    ##
    # Get current task state. See @ref work_queue_task_state_t for possible values.
    # @code
    # >>> print q.task_state(taskid)
    # @endcode
    def task_state(self, taskid):
        return work_queue_task_state(self._work_queue, taskid)

    ## Enables resource monitoring of tasks in the queue. And writes a summary of the monitored information to a file.
    #
    #  Returns 1 on success, 0 on failure (i.e., monitoring was not enabled).
    #
    # @param self 	Reference to the current work queue object.
    # @param summaryfile Filename for the summary log (If NULL, writes to wq-\<pid\>-resource-usage).
    def enable_monitoring(self, summaryfile):
        return work_queue_enable_monitoring(self._work_queue, summaryfile)

    ##
    # Turn on or off fast abort functionality for a given queue.
    #
    # @param self       Reference to the current work queue object.
    # @param multiplier The multiplier of the average task time at which point to abort; if negative (the default) fast_abort is deactivated.
    def activate_fast_abort(self, multiplier):
        return work_queue_activate_fast_abort(self._work_queue, multiplier)

    ##
    # Determine whether there are any known tasks queued, running, or waiting to be collected.
    #
    # Returns 0 if there are tasks remaining in the system, 1 if the system is "empty".
    #
    # @param self       Reference to the current work queue object.
    def empty(self):
        return work_queue_empty(self._work_queue)

    ##
    # Determine whether the queue can support more tasks.
    #
    # Returns the number of additional tasks it can support if "hungry" and 0 if "sated".
    #
    # @param self       Reference to the current work queue object.
    def hungry(self):
        return work_queue_hungry(self._work_queue)

    ##
    # Set the worker selection algorithm for queue.
    #
    # @param self       Reference to the current work queue object.
    # @param algorithm  One of the following algorithms to use in assigning a
    #                   task to a worker. See @ref work_queue_schedule_t for
    #                   possible values.
    def specify_algorithm(self, algorithm):
        return work_queue_specify_algorithm(self._work_queue, algorithm)

    ##
    # Set the order for dispatching submitted tasks in the queue.
    #
    # @param self       Reference to the current work queue object.
    # @param order  	One of the following algorithms to use in dispatching
	# 					submitted tasks to workers:
    #                   - @ref WORK_QUEUE_TASK_ORDER_FIFO
    #                   - @ref WORK_QUEUE_TASK_ORDER_LIFO
    def specify_task_order(self, order):
        return work_queue_specify_task_order(self._work_queue, order)

    ##
    # Change the project name for the given queue.
    #
    # @param self   Reference to the current work queue object.
    # @param name   The new project name.
    def specify_name(self, name):
        return work_queue_specify_name(self._work_queue, name)

    ##
    # Change the project priority for the given queue.
    #
    # @param self       Reference to the current work queue object.
    # @param priority   An integer that presents the priorty of this work queue master. The higher the value, the higher the priority.
    def specify_priority(self, priority):
        return work_queue_specify_priority(self._work_queue, priority)

    ## Specify the number of tasks not yet submitted to the queue.
    # It is used by work_queue_pool to determine the number of workers to launch.
    # If not specified, it defaults to 0.
    # work_queue_pool considers the number of tasks as:
    # num tasks left + num tasks running + num tasks read.
    # @param q A work queue object.
    # @param ntasks Number of tasks yet to be submitted.
    def specify_num_tasks_left(self, ntasks):
        return work_queue_specify_num_tasks_left(self._work_queue, ntasks)

    ##
    # Specify the master mode for the given queue.
    #
    # @param self   Reference to the current work queue object.
    # @param mode   This may be one of the following values: @ref WORK_QUEUE_MASTER_MODE_STANDALONE or @ref WORK_QUEUE_MASTER_MODE_CATALOG.
    def specify_master_mode(self, mode):
        return work_queue_specify_master_mode(self._work_queue, mode)

    ##
    # Specify the catalog server the master should report to.
    #
    # @param self       Reference to the current work queue object.
    # @param hostname   The hostname of the catalog server.
    # @param port       The port the catalog server is listening on.
    def specify_catalog_server(self, hostname, port):
        return work_queue_specify_catalog_server(self._work_queue, hostname, port)

    ##
    # Specify a log file that records the states of connected workers and submitted tasks.
    #
    # @param self     Reference to the current work queue object.
    # @param logfile  Filename.
    def specify_log(self, logfile):
        return work_queue_specify_log(self._work_queue, logfile)

    ##
    # Add a mandatory password that each worker must present.
    #
    # @param self      Reference to the current work queue object.
    # @param password  The password.

    def specify_password(self, password):
        return work_queue_specify_password(self._work_queue, password)

    ##
    # Add a mandatory password file that each worker must present.
    #
    # @param self      Reference to the current work queue object.
    # @param file      Name of the file containing the password.

    def specify_password_file(self, file):
        return work_queue_specify_password_file(self._work_queue, file)

    ##
    # Cancel task identified by its taskid and remove from the given queue.
    #
    # @param self   Reference to the current work queue object.
    # @param id     The taskid returned from @ref submit.
    def cancel_by_taskid(self, id):
        return work_queue_cancel_by_taskid(self._work_queue, id)

    ##
    # Cancel task identified by its tag and remove from the given queue.
    #
    # @param self   Reference to the current work queue object.
    # @param tag    The tag assigned to task using @ref work_queue_task_specify_tag.
    def cancel_by_tasktag(self, tag):
        return work_queue_cancel_by_tasktag(self._work_queue, tag)

    ##
    # Shutdown workers connected to queue.
    #
    # Gives a best effort and then returns the number of workers given the shutdown order.
    #
    # @param self   Reference to the current work queue object.
    # @param n      The number to shutdown.  To shut down all workers, specify "0".
    def shutdown_workers(self, n):
        return work_queue_shut_down_workers(self._work_queue, n)

    ##
    # Blacklist workers running on host.
    #
    # @param self   Reference to the current work queue object.
    # @param host   The hostname the host running the workers.
    def blacklist(self, host):
        return work_queue_blacklist_add(self._work_queue, host)

    ##
    # Remove host from blacklist. Clear all blacklist if host not provided.
    #
    # @param self   Reference to the current work queue object.
    # @param host   The of the hostname the host.
    def blacklist_clear(self, host=None):
        if host is None:
            return work_queue_blacklist_clear(self._work_queue)
        else:
            return work_queue_blacklist_remove(self._work_queue, host)

    ##
    # Change keepalive interval for a given queue.
    #
    # @param self     Reference to the current work queue object.
    # @param interval Minimum number of seconds to wait before sending new keepalive
    #                 checks to workers.
    def specify_keepalive_interval(self, interval):
        return work_queue_specify_keepalive_interval(self._work_queue, interval)

    ##
    # Change keepalive timeout for a given queue.
    #
    # @param self     Reference to the current work queue object.
    # @param timeout  Minimum number of seconds to wait for a keepalive response
    #                 from worker before marking it as dead.
    def specify_keepalive_timeout(self, timeout):
        return work_queue_specify_keepalive_timeout(self._work_queue, timeout)

    ##
    # Turn on master capacity measurements.
    #
    # @param self     Reference to the current work queue object.
    #
    def estimate_capacity(self):
        return work_queue_specify_estimate_capacity_on(self._work_queue, 1)

    ##
    # Tune advanced parameters for work queue.
    #
    # @param self  Reference to the current work queue object.
    # @param name  The name fo the parameter to tune. Can be one of following:
    #              - "asynchrony-multiplier" Treat each worker as having (actual_cores * multiplier) total cores. (default = 1.0)
    #              - "asynchrony-modifier" Treat each worker as having an additional "modifier" cores. (default=0)
    #              - "min-transfer-timeout" Set the minimum number of seconds to wait for files to be transferred to or from a worker. (default=300)
    #              - "foreman-transfer-timeout" Set the minimum number of seconds to wait for files to be transferred to or from a foreman. (default=3600)
    #              - "fast-abort-multiplier" Set the multiplier of the average task time at which point to abort; if negative or zero fast_abort is deactivated. (default=0)
    #              - "keepalive-interval" Set the minimum number of seconds to wait before sending new keepalive checks to workers. (default=300)
    #              - "keepalive-timeout" Set the minimum number of seconds to wait for a keepalive response from worker before marking it as dead. (default=30)
    # @param value The value to set the parameter to.
    # @return 0 on succes, -1 on failure.
    #
    def tune(self, name, value):
        return work_queue_tune(self._work_queue, name, value)

    ##
    # Submit a task to the queue.
    #
    # It is safe to re-submit a task returned by @ref wait.
    #
    # @param self   Reference to the current work queue object.
    # @param task   A task description created from @ref work_queue::Task.
    def submit(self, task):
        taskid = work_queue_submit(self._work_queue, task._task)
        self._task_table[taskid] = task
        return taskid

    ##
    # Wait for tasks to complete.
    #
    # This call will block until the timeout has elapsed
    #
    # @param self       Reference to the current work queue object.
    # @param timeout    The number of seconds to wait for a completed task
    #                   before returning.  Use an integer to set the timeout or the constant @ref
    #                   WORK_QUEUE_WAITFORTASK to block until a task has completed.
    def wait(self, timeout=WORK_QUEUE_WAITFORTASK):
        task_pointer = work_queue_wait(self._work_queue, timeout)
        if task_pointer:
            task = self._task_table[int(task_pointer.taskid)]
            del(self._task_table[task_pointer.taskid])
            return task
        return None
