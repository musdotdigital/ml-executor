from marshmallow import Schema, fields
import enum


class StatusType(Schema):
    job_id = fields.Str(required=True)


class BackendType(str, enum.Enum):
    REMOTE = "remote"  # TODO: implement this
    LOCAL_DOCKER = "docker"
    LOCAL_SUBPROCESS = "subprocess"
