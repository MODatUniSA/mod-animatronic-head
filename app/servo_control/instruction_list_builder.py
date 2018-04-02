
from copy import copy
import logging

# TODO: Implement infinite recursion detection/protection.

from libs.config.path_helper import PathHelper
from app.servo_control.instruction_iterator import InstructionIterator
from app.servo_control.instruction_list import InstructionList

class InstructionListBuilder:
    """ Builds instruction lists/iterators from a filename. Handles arbitrarily deep structure
        of nested/parallel sequences, and returns a hierarchy of instruction iterators
    """

    IDENTIFY_BY_FILENAME = False

    def __init__(self):
        self._logger = logging.getLogger('instruction_list_builder')

    def build(self, filename):
        """ Builds instruction lists/Iterators from the input filename.
            Returns a hierarchy of instruction iterators
        """

        instruction_list = InstructionList()
        success, parallel_sequences = instruction_list.load_instructions(filename)

        if not success:
            self._logger.error("Failed to load instruction list")
            return None

        for sequence in parallel_sequences:
            instruction_list.merge(self.build(sequence.filename))

        instruction_list.sort_instructions()
        return instruction_list

    @classmethod
    def create_iterator(cls, instruction_list, **kwargs):
        """ Creates an instruction iterator, assigning the argument callbacks
        """

        instruction_iterator = InstructionIterator()
        execute_callback = kwargs.get('execute_callback')
        complete_callback = kwargs.get('complete_callback')
        if execute_callback:
            instruction_iterator.add_instruction_callback(execute_callback)
        if complete_callback:
            instruction_iterator.add_complete_callback(complete_callback)

        instruction_iterator.set_instruction_list(instruction_list)
        return cls.iterator_info(instruction_iterator, **kwargs)

    @classmethod
    def iterator_info(cls, iterator, **kwargs):
        return {
            'id'             : id(iterator),
            'iterator'       : iterator,
            'without_servos' : kwargs.get('without_servos'),
            'override'       : kwargs.get('override', False),
            'overridden'     : set()
        }

    @classmethod
    def _iterator_identifier(cls, iterator, filename):
        """ Used so we can key by filename (for debugging) or iterator id
        """
        return filename if cls.IDENTIFY_BY_FILENAME else id(iterator)
