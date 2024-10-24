import logging
from typing import Dict

from graphql import GraphQLError

from hct_mis_api.apps.accountability.models import Message

logger = logging.getLogger(__name__)


class MessageArgumentVerifier:
    ARGUMENTS = {
        "sampling_type": {
            Message.SamplingChoices.FULL_LIST: {
                "required": ["full_list_arguments"],
                "not_allowed": ["random_sampling_arguments"],
            },
            Message.SamplingChoices.RANDOM: {
                "required": ["random_sampling_arguments"],
                "not_allowed": ["full_list_arguments"],
            },
        },
        "only_one_of_these": ["households", "target_population", "registration_data_import"],
    }

    def __init__(self, input_data: Dict) -> None:
        self.input_data = input_data

    def verify(self) -> None:
        only_one_of_these = self.ARGUMENTS.get("only_one_of_these")
        inputs = [self.input_data.get(argument) for argument in only_one_of_these]
        fields = [*only_one_of_these]
        last_1 = fields.pop()
        if not any(inputs):
            err_msg = f"Must provide any one of {', '.join(fields)} or {last_1}"
            logger.error(err_msg)
            raise GraphQLError(err_msg)
        if len([value for value in inputs if value]) > 1:
            err_msg = f"Must provide only one of {', '.join(fields)} or {last_1}"
            logger.error(err_msg)
            raise GraphQLError(err_msg)

        options = self.ARGUMENTS.get("sampling_type")
        for key, value in options.items():
            if key != self.input_data.get("sampling_type"):
                continue
            for required in value.get("required"):
                if self.input_data.get(required) is None:
                    err_msg = f"Must provide {required} for {key}"
                    logger.error(err_msg)
                    raise GraphQLError(err_msg)
            for not_allowed in value.get("not_allowed"):
                if self.input_data.get(not_allowed) is not None:
                    err_msg = f"Must not provide {not_allowed} for {key}"
                    logger.error(err_msg)
                    raise GraphQLError(err_msg)
