"""
Utility functions and helpers for the ecsctl package.
"""

import contextlib
import signal


@contextlib.contextmanager
def ignore_user_entered_signals():
    """
    Context manager that temporarily ignores user-entered signals (SIGINT, SIGQUIT, SIGTSTP)
    to prevent subprocess interruption.

    This is particularly useful when running interactive shell sessions where we want
    the child process to handle these signals instead of the parent process.

    Example:
        with ignore_user_entered_signals():
            subprocess.run(['some', 'command'])

    References:
        - https://github.com/hreeder/assh/issues/3
    """
    signal_list = [signal.SIGINT, signal.SIGQUIT, signal.SIGTSTP]
    actual_signals = []
    
    # Store original signal handlers and set them to ignore
    for user_signal in signal_list:
        actual_signals.append(signal.signal(user_signal, signal.SIG_IGN))
    try:
        yield
    finally:
        # Restore original signal handlers
        for sig, user_signal in enumerate(signal_list):
            signal.signal(user_signal, actual_signals[sig]) 