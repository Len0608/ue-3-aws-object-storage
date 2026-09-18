"""Actions module — business logic implementations for the AWS Object Storage extension."""

from actions.output import ActionOutput
from actions.list_objects import list_objects
from actions.upload_file import upload_file

# Maps the action field value (SingleChoice.value) to the corresponding function.
# Keys must exactly match the choice labels defined in template.json and validated
# in InputFields._validate_action().
ACTION_MAPPER = {
    "List Objects": list_objects,
    "Upload File": upload_file,
}
