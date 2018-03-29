
from copy import copy
import logging

# TODO: Implement infinite recursion detection/protection.

from libs.config.path_helper import PathHelper
from app.servo_control.instruction_iterator import InstructionIterator
from app.servo_control.instruction_list import InstructionList, InstructionTypes


class InstructionListBuilder:
    """ Builds instruction lists/iterators from a filename. Handles arbitrarily deep structure
        of nested/parallel sequences, and returns a hierarchy of instruction iterators
    """

    IDENTIFY_BY_FILENAME = False

    def __init__(self, iterator_execute_callback, iterator_complete_callback):
        self._logger = logging.getLogger('instruction_list_builder')
        self._iterator_execute_callback = iterator_execute_callback
        self._iterator_complete_callback = iterator_complete_callback

    def build(self, filename, options=None):
        """ Builds instruction lists/Iterators from the input filename.
            Returns a hierarchy of instruction iterators
        """

        options = options or {}
        iterators = options.get('iterators', {})
        parent    = options.get('parent')

        instruction_list     = InstructionList(filename)
        instruction_iterator = self._create_instruction_iterator(instruction_list)

        if parent:
            self._logger.debug("Built nested iterator for %s: %d", filename, id(instruction_iterator))
        else:
            self._logger.debug("Building iterator for %s: %d", filename, id(instruction_iterator))

        iterator_key = type(self)._iterator_identifier(instruction_iterator, filename)
        type(self)._add_to_structure(iterator_key, instruction_iterator, iterators, options)

        if parent is not None:
            iterators[parent].setdefault('nested',{})
            iterators[parent]['nested'][filename] = instruction_iterator

        nested_options = copy(options)
        nested_options.update({
            'primary'   : False,
            'parent'    : iterator_key,
            'iterators' : iterators
        })

        for sequence in instruction_list.parallel_sequences:
            _,nested_iterators = self.build(
                filename=sequence.filename,
                options=nested_options
            )

            iterators.update(nested_iterators)

        # Return the iterator for the top level instructions, as well as the hierarchy
        return instruction_iterator, iterators

    @staticmethod
    def _add_to_structure(key, iterator, iterators, options):
        iterators[key] = {
            'iterator'       : iterator,
            'primary'        : options.get('primary', True),
            'without_servos' : options.get('without_servos'),
            'override'       : options.get('override', False),
            'overridden'     : set()
        }

    def _create_instruction_iterator(self, instruction_list=None):
        instruction_iterator = InstructionIterator()
        instruction_iterator.add_instruction_callback(self._iterator_execute_callback)
        instruction_iterator.add_complete_callback(self._iterator_complete_callback)
        if instruction_list is not None:
            instruction_iterator.set_instruction_list(instruction_list)

        return instruction_iterator

    @classmethod
    def _iterator_identifier(cls, iterator, filename):
        """ Used so we can key by filename (for debugging) or iterator id
        """
        return filename if cls.IDENTIFY_BY_FILENAME else id(iterator)
