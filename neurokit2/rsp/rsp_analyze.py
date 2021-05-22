# -*- coding: utf-8 -*-
import pandas as pd

from .rsp_eventrelated import rsp_eventrelated
from .rsp_intervalrelated import rsp_intervalrelated


def rsp_analyze(data, sampling_rate=1000, method="auto", subepoch_rate=[None, None]):
    """Performs RSP analysis on either epochs (event-related analysis) or on longer periods of data such as resting-
    state data.

    Parameters
    ----------
    data : dict or DataFrame
        A dictionary of epochs, containing one DataFrame per epoch, usually obtained via `epochs_create()`,
        or a DataFrame containing all epochs, usually obtained via `epochs_to_df()`. Can also take a
        DataFrame of processed signals from a longer period of data, typically generated by `rsp_process()`
        or `bio_process()`. Can also take a dict containing sets of separate periods of data.
    sampling_rate : int
        The sampling frequency of the signal (in Hz, i.e., samples/second). Defaults to 1000Hz.
    method : str
        Can be one of 'event-related' for event-related analysis on epochs, or 'interval-related' for
        analysis on longer periods of data. Defaults to 'auto' where the right method will be chosen
        based on the mean duration of the data ('event-related' for duration under 10s).
    subepoch_rate : list
        For event-related analysis,, a smaller "sub-epoch" within the epoch of an event can be specified.
        The ECG rate-related features of this "sub-epoch" (e.g., RSP_Rate, RSP_Rate_Max),
        relative to the baseline (where applicable), will be computed. The first value of the list specifies
        the start of the sub-epoch and the second specifies the end of the sub-epoch (in seconds),
        e.g., subepoch_rate = [1, 3] or subepoch_rate = [1, None]. Defaults to [None, None].

    Returns
    -------
    DataFrame
        A dataframe containing the analyzed RSP features. If event-related analysis is conducted, each
        epoch is indicated by the `Label` column. See `rsp_eventrelated()` and `rsp_intervalrelated()`
        docstrings for details.

    See Also
    --------
    bio_process, rsp_process, epochs_create, rsp_eventrelated, rsp_intervalrelated

    Examples
    ----------
    >>> import neurokit2 as nk

    >>> # Example 1: Download the data for event-related analysis
    >>> data = nk.data("bio_eventrelated_100hz")
    >>>
    >>> # Process the data for event-related analysis
    >>> df, info = nk.bio_process(rsp=data["RSP"], sampling_rate=100)
    >>> events = nk.events_find(data["Photosensor"], threshold_keep='below',
    ...                         event_conditions=["Negative", "Neutral", "Neutral", "Negative"])
    >>> epochs = nk.epochs_create(df, events, sampling_rate=100, epochs_start=-0.1, epochs_end=1.9)
    >>>
    >>> # Analyze
    >>> nk.rsp_analyze(epochs, sampling_rate=100) #doctest: +SKIP
    >>>
    >>> # Example 2: Download the resting-state data
    >>> data = nk.data("bio_resting_5min_100hz")
    >>>
    >>> # Process the data
    >>> df, info = nk.rsp_process(data["RSP"], sampling_rate=100)
    >>>
    >>> # Analyze
    >>> nk.rsp_analyze(df, sampling_rate=100) #doctest: +SKIP

    """
    method = method.lower()

    # Event-related analysis
    if method in ["event-related", "event", "epoch"]:
        # Sanity checks
        if isinstance(data, dict):
            for i in data:
                colnames = data[i].columns.values
        elif isinstance(data, pd.DataFrame):
            colnames = data.columns.values

        if len([i for i in colnames if "Label" in i]) == 0:
            raise ValueError(
                "NeuroKit error: rsp_analyze(): Wrong input or method, we couldn't extract extract epochs features."
            )
        else:
            features = rsp_eventrelated(data, subepoch_rate=subepoch_rate)

    # Interval-related analysis
    elif method in ["interval-related", "interval", "resting-state"]:
        features = rsp_intervalrelated(data, sampling_rate)

    # Auto
    elif method in ["auto"]:

        if isinstance(data, dict):
            for i in data:
                duration = len(data[i]) / sampling_rate
            if duration >= 10:
                features = rsp_intervalrelated(data, sampling_rate)
            else:
                features = rsp_eventrelated(data, subepoch_rate=subepoch_rate)

        if isinstance(data, pd.DataFrame):
            if "Label" in data.columns:
                epoch_len = data["Label"].value_counts()[0]
                duration = epoch_len / sampling_rate
            else:
                duration = len(data) / sampling_rate
            if duration >= 10:
                features = rsp_intervalrelated(data, sampling_rate)
            else:
                features = rsp_eventrelated(data, subepoch_rate=subepoch_rate)

    return features
