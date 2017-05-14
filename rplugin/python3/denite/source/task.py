import os
import re
import sys
import datetime
from .base import Base

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from tasklib.backends import TaskWarrior  # noqa


class Source(Base):
    """ Vim session loader source for Denite.nvim """

    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'task'
        self.kind = 'task'
        self.vars = {
            'taskrc': os.environ.get('TASKRC', '~/.taskrc'),
            'data_dir': os.environ.get('TASKDATA', '~/.task'),
            'format': '{id:3.3} | {priority:1.1} | {project:15.15} | {description:40.40} | {entry} | {due}',  # noqa
            'date_format': '%y-%m-%d %H:%M',
            'label_width': 17,
        }

    def gather_candidates(self, context):
        candidates = []

        for task in self._tw().tasks.all():
            default_keys = {
                'uuid', 'due', 'project', 'description', 'priority',
                'urgency', 'tags', 'modified', 'entry', 'status',
            }
            values = {key: '' for key in default_keys}
            for k, v in task._data.items():
                if isinstance(v, datetime.datetime):
                    # v = v.strftime(self.vars['date_format'])
                    v = self._pretty_date(v)
                values[k] = str(v)

            formatter = self._calc_percentage(self.vars['format'])
            word = formatter.format(**values)

            candidates.append({
                'word': word,
                'action__id': task['id'],
            })

        return candidates

    def _tw(self):
        return TaskWarrior(
            data_location=self.vars['data_dir'],
            taskrc_location=self.vars['taskrc'],
            create=False)

    def _calc_percentage(self, format):
        """ Compiles sizes from numbers in format, handled as percentage """
        winwidth = self.vim.call('winwidth', 0)
        pattern = r'([\<\>\.\:\^])(\d+)'

        def calc_percent(obj):
            percent = round(winwidth * (int(obj.group(2)) / 100))
            return obj.group(1) + str(percent)

        return re.sub(pattern, calc_percent, format)

    def _pretty_date(self, dt):
        now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        diff = now - dt
        s = diff.seconds
        if diff.days > 7 or diff.days < 0:
            return dt.strftime('%d %b %y')
        elif diff.days > 0:
            return '{}d'.format(diff.days)
        elif s <= 1:
            return 'just now'
        elif s < 60:
            return '{}s'.format(s)
        elif s < 3600:
            return '{}m'.format(s / 60)
        else:
            return '{}h'.format(s / 3600)
