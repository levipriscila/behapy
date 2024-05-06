import logging
from .fp import load_preprocessed_fibre
from .events import load_events
from .pathutils import list_preprocessed
import pandas as pd
from collections import namedtuple


def load_preprocessed_experiment(root):
    Preprocessed = namedtuple('Preprocessed', ['recordings', 'dff', 'events'])
    recordings = pd.DataFrame(list_preprocessed(root))
    if recordings.empty:
        return Preprocessed(None, None, None)

    def _load_preprocessed(row):
        r = row.iloc[0]
        return load_preprocessed_fibre(root, r.subject, r.session,
                                       r.task, r.run, r.label)

    def _load_events(row):
        r = row.iloc[0]
        try:
            events = load_events(root, r.subject, r.session, r.task, r.run)
        except FileNotFoundError:
            logging.warning(f'No events found for subject {r.subject}, '
                            f'session {r.session}, task {r.task} and '
                            f'run {r.run}')
            events = None
        return events

    id = ['subject', 'session', 'task', 'run', 'label']
    dff = recordings.groupby(id).apply(_load_preprocessed)
    dff.attrs = _load_preprocessed(recordings.iloc[[0]]).attrs
    events = recordings.groupby(id).apply(_load_events)
    events.attrs = _load_events(recordings.iloc[[0]]).attrs
    return Preprocessed(recordings, dff, events)
