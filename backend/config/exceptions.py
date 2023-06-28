class DockerCommandError(Exception):
    """
    Exception raised when a forbidden command is found in the Dockerfile, cannot use: 'USER root', 'EXPOSE', 'ADD'.
    """
