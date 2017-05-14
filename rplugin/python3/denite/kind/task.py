import os
import sys
import copy
from collections import OrderedDict

from .base import Base
from ..source.task import Source

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from tasklib.backends import TaskWarrior  # noqa


class Kind(Base):

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'task'
        self.default_action = 'edit'
        self.persist_actions += ['preview']
        # self.redraw_actions = ['preview']

        self.__vars = {}

    def action_edit(self, context):
        """ Action: Edit task """
        target = context['targets'][0]
        task_id = target.get('action__id')

        tw = self._tw(context)
        task = tw.tasks.get(id=task_id)

        self.vim.call(
            'taskwarrior#edit', context, self._task_view(task, readonly=False))

    def action_preview(self, context):
        """ Action: View task """
        target = context['targets'][0]
        task_id = target.get('action__id')

        tw = self._tw(context)
        task = tw.tasks.get(id=task_id)

        self.vim.call(
            'taskwarrior#preview', context, self._task_view(task))

    def _tw(self, context):
        """ Load source full vars and merge with user custom """
        # FIXME: Find a better way without importing Source
        if not self.__vars:
            custom = context['custom']['source'] \
                    .get('task', {}) \
                    .get('vars', {})
            self.__vars = Source(self.vim).vars.copy()
            self.__vars.update(custom)

        return TaskWarrior(
            data_location=self.__vars['data_dir'],
            taskrc_location=self.__vars['taskrc'],
            create=False)

    def _task_view(self, task, readonly=True):
        """ Serializes an object Task as a tabular view """
        label_width = self.__vars.get('label_width', 17)

        s = []
        s.append('# {:{}}  {}'.format(
            'Name',
            label_width,
            'Details' if readonly else 'Editable details'))
        s.append('# {}  {}'.format('-' * label_width, '-' * 52))

        readonly = ['id', 'uuid', 'status', 'mask',
                    'imask', 'entry', 'modified', 'urgency']

        mapping = OrderedDict([
            ('id', 'ID'),
            ('uuid', 'UUID'),
            ('status', 'Status'),
            ('mask', 'Mask'),
            ('imask', 'iMask'),
            ('project', 'Project'),
            ('tags', 'Tags'),
            ('description', 'Description'),
            ('entry', 'Created'),
            ('start', 'Started'),
            ('end', 'Ended'),
            ('scheduled', 'Scheduled'),
            ('due', 'Due'),
            ('until', 'Until'),
            ('recur', 'Recur'),
            ('wait', 'Wait until'),
            ('modified', 'Modified'),
            ('parent', 'Parent'),
        ])

        def format_line(key, label, value):
            if isinstance(value, set):
                value = ' '.join(value)
            return '{prefix} {label:{width}.{width}}  {value}'.format(
                prefix='#' if key in readonly else ' ',
                label='{}:'.format(label),
                width=label_width,
                value=value,
            )

        d = copy.deepcopy(task._data)

        # Main columns
        for key, label in mapping.items():
            value = d.pop(key, '')
            s.append(format_line(key, label, value))

        # Annotations
        s.append('')
        for annotation in d.pop('annotations', []):
            s.append('  Annotation:        {} -- {}'.format(
                annotation['entry'], annotation['description']))

        # TODO: Let user create new annotations
        # now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        # s.append('  Annotation:        {} -- '.format(now))
        # s.append('')

        # UDA
        s.append('')
        d.pop('urgency')
        for key, value in d.items():
            value = d.get(key, '')
            s.append(format_line(key, key, value))

        return s
