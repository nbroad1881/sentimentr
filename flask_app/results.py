from datetime import timedelta, date, datetime

import pandas as pd
from flask_app.models import Article
from config import DB_URI, DB_TABLE_NAME, DB_SELECT_COLUMNS, DB_PARSE_COLUMNS, DB_DATETIME_COLUMN_NAME

CANDIDATES = ['TRUMP', 'BIDEN', 'SANDERS', 'WARREN', 'HARRIS', 'BUTTIGIEG']
CNN = 'CNN'
NYT = 'NEW YORK TIMES'
FOX = 'FOX NEWS'

needed_column_names = [
    "url",
    "datetime",
    "title",
    "news_co",
    "vader_positive",
    "vader_negative",
    "textblob_p_pos",
    "textblob_p_neg",
    "lstm_p_pos",
    "lstm_p_neg"
]

unnecessary_column_names = [
    'text',
    'vader_neutral',
    'vader_compound',
    'textblob_polarity',
    'textblob_subjectivity',
    'textblob_classification',
    'lstm_score',
    'lstm_category',
    'lstm_p_neu',
]

SCORE_COLUMNS = {
    'vader': 'vader_score',
    'textblob': 'textblob_score',
    'lstm': 'lstm_score',
}

CHART_DATA_COLUMNS = ['url', 'datetime', 'title', 'news_co', 'vader_score', 'textblob_score', 'lstm_score']


class Result:

    #  todo: set limit on how much to initially store
    def __init__(self):
        self.df = make_datetimes_descending(db_to_frame())
        self.calculate_scores()

    def calculate_scores(self):
        self.df.loc[:, SCORE_COLUMNS['vader']] = self.df['vader_positive'] - self.df['vader_negative']
        self.df.loc[:, SCORE_COLUMNS['textblob']] = self.df['textblob_p_pos'] - self.df['textblob_p_neg']
        self.df.loc[:, SCORE_COLUMNS['lstm']] = self.df['lstm_p_pos'] - self.df['lstm_p_neg']


def db_to_frame():
    return pd.read_sql_table(DB_TABLE_NAME, DB_URI, parse_dates=DB_PARSE_COLUMNS, columns=DB_SELECT_COLUMNS)


def make_datetimes_descending(df):
    return df.sort_values(by=DB_DATETIME_COLUMN_NAME, ascending=False)


def get_most_recent(df, num_entries=100):
    return make_datetimes_descending(df).iloc[:num_entries, :]


def get_data_for_chart(df):
    return df.loc[:, CHART_DATA_COLUMNS]


def average_by_day(df, days_back=180):
    df = df.loc[df[DB_DATETIME_COLUMN_NAME] > (datetime.utcnow() - timedelta(days=days_back))]
    datetimes = pd.DataFrame(data=df[DB_DATETIME_COLUMN_NAME].dt.floor(freq='D').unique(), columns=['datetime'])
    return pd.concat([df.groupby(by=df[DB_DATETIME_COLUMN_NAME].dt.floor(freq='D'), as_index=False)[
        list(SCORE_COLUMNS.values())].mean(), datetimes], axis=1)


def sort_by(df, column_name):
    """
    Sorts the DataFrame by the specified column name, then does a second level sort by datetime.
    Useful for grouping all data of news_co or candidate next to one another.
    :param df: DataFrame to be sorted.
    :type df: pandas.DataFrame
    :param column_name: column name to sort by
    :type column_name: string
    :return: sorted DataFrame
    :rtype: pandas.DataFrame
    """
    return df.sort_values(by=[column_name, DB_DATETIME_COLUMN_NAME], ascending=False)


def filter_by(df, column_name, value):
    """
    Returns only the portion of the DataFrame that has the given value in the specified column.
    Can be used to filter by news_co or candidate name.
    :param df: DataFrame of database scores
    :type df: pandas.DataFrame
    :param column_name: e.g. ['news_co', 'title']
    :type column_name: iterable of strings
    :param value: target value in column_name. If value is a name, use all lowercase.
    :type value: string
    :return: filtered DataFrame
    :rtype: pandas.DataFrame
    """
    lower_column = df[column_name].apply(lambda s: s.lower())
    return df.loc[lower_column.str.contains(value.lower())]

def reverse_all(df):
    return df.iloc[::-1];

def df_to_dict(df):
    d = {}
    for column in df.columns:
        d[column] = list(df.loc[:, column])
    return d


# *******************************************************
# Beyond this point is old work


def get_date_array(start=None, num_days_back=180):
    # todo: be able to use start and end to have custom date range.
    if start is not None:
        [start - timedelta(days=d) for d in range(num_days_back)]
    return [datetime.utcnow().date() - timedelta(days=d) for d in range(num_days_back)]


def average_results(scores, score_dates, date_arr, news_co_array=None, selected_news_co=None):
    """
    Given an array of scores, this will return an array of daily average scores from the date at the first index
    of score_dates to the date at the last index of score_dates.
    :param news_co_array: Array of the news_co associated with each score.
    :param selected_news_co: Choose an option from CNN, FOX, NYT to filter by that news agency
    :param date_arr: Array of dates starting with today and going 180 days back. Today uses utcnow.
    :param score_dates: Associated dates with each score. Must be in UTC
    :param scores: Sentiment scores for each headline
    :return:
    """
    daily_averages = []
    index = 0
    for d in date_arr:
        temp_sum = 0
        num_dates = 0
        while score_dates[index].date() == d:
            if news_co_array is None or selected_news_co.upper() in news_co_array[index].upper():
                temp_sum += scores[index]
                num_dates += 1
            index += 1
        if score_dates[index].date() > d:
            print("Score dates are in the future. Check dates")
        if num_dates == 0:
            average = 0
        else:
            average = temp_sum / num_dates
        daily_averages.append(average)

    return daily_averages


def custom_average(scores, dates, return_dates=False, window_size=1):
    """
    Takes an array of scores and dates and returns an average for each day.
    If return_dates is set to True, also return those dates.
    :param window_size: If an average over multiple days is desired
    :param scores:
    :param dates:
    :param return_dates:
    :return:
    """
    window_size = window_size

    start_date = dates[0]
    end_date = start_date - timedelta(days=window_size)

    averaged_scores = []
    new_dates = [start_date]
    index = 0
    temp_sum = 0
    counter = 0
    while start_date > end_date and index < len(scores):
        # Sum up scores when in time window
        if start_date >= dates[index] > end_date:
            temp_sum += scores[index]
            counter += 1
        #     When out of window, append average, reset counters, shift dates
        else:
            if counter == 0:
                average = 0
            else:
                average = temp_sum / counter
            averaged_scores.append(average)

            temp_sum = 0
            counter = 0
            new_dates.append(end_date)
            start_date = end_date
            end_date = start_date - timedelta(days=window_size)

        index += 1

    if return_dates:
        return averaged_scores, new_dates
    return averaged_scores


# todo: remove if using better_results
def lists_from_results(results):
    """
    Go from list of dictionaries to list of lists.
    Each sub-list is a category e.g. 'title'
    :param results:
    :return:
    """
    joined = [
        (
            res['title'],
            res['vader_positive'] - res['vader_negative'],
            res['textblob_p_pos'] - res['textblob_p_neg'],
            res['lstm_p_pos'] - res['lstm_p_neg'],
            res['news_co'],
            res['datetime']
        )
        for res in results
    ]
    return list(zip(*joined))


def to_dict(results):
    titles = [res['title'] for res in results]
    vader_scores = [res['vader_positive'] - res['vader_negative'] for res in results]
    textblob_scores = [res['textblob_p_pos'] - res['textblob_p_neg'] for res in results]
    lstm_scores = [res['lstm_p_pos'] - res['lstm_p_neg'] for res in results]
    news_co = [res['news_co'] for res in results]
    dates = [res['datetime'] for res in results]
    date_array = get_date_array()

    return {
        'titles': titles,
        'vader': vader_scores,
        'textblob': textblob_scores,
        'lstm': lstm_scores,
        'news_co': news_co,
        'dates': dates,
        'vader_averaged': average_results(vader_scores, dates, date_array),
        'textblob_averaged': average_results(textblob_scores, dates, date_array),
        'lstm_averaged': average_results(lstm_scores, dates, date_array),
        'dates_array': date_array,
        'cnn_textblob_averaged': average_results(textblob_scores, dates, date_array, news_co_array=news_co,
                                                 selected_news_co=CNN),
        'cnn_vader_averaged': average_results(vader_scores, dates, date_array, news_co_array=news_co,
                                              selected_news_co=CNN),
        'cnn_lstm_averaged': average_results(lstm_scores, dates, date_array, news_co_array=news_co,
                                             selected_news_co=CNN),
        'nyt_textblob_averaged': average_results(textblob_scores, dates, date_array, news_co_array=news_co,
                                                 selected_news_co=NYT),
        'nyt_vader_averaged': average_results(vader_scores, dates, date_array, news_co_array=news_co,
                                              selected_news_co=NYT),
        'nyt_lstm_averaged': average_results(lstm_scores, dates, date_array, news_co_array=news_co,
                                             selected_news_co=NYT),
        'fox_textblob_averaged': average_results(textblob_scores, dates, date_array, news_co_array=news_co,
                                                 selected_news_co=FOX),
        'fox_vader_averaged': average_results(vader_scores, dates, date_array, news_co_array=news_co,
                                              selected_news_co=FOX),
        'fox_lstm_averaged': average_results(lstm_scores, dates, date_array, news_co_array=news_co,
                                             selected_news_co=FOX),
    }


def get_all_results(db):
    query = [c for c in Article.__table__.c if c.name in needed_column_names]
    six_months_ago = date.today() - timedelta(days=180)
    up_to = date.today()

    queried_results = db.session.query(*query). \
        order_by(Article.datetime.desc()). \
        filter(Article.datetime >= six_months_ago). \
        filter(Article.datetime <= up_to)

    results_array = [r._asdict() for r in queried_results.all()]
    return to_dict(results_array)


"""
Return as dictionary of lists
"""


def create_dict_lists(titles, vader_scores, textblob_scores, lstm_scores, news_co, dates):
    return {
        'titles': titles,
        'vader': vader_scores,
        'textblob': textblob_scores,
        'lstm': lstm_scores,
        'news_co': news_co,
        'dates': dates
    }


def get_date_index(target, date_array):
    """
    Given a date array, returns the index that matches the parameter target
    :param target: Target date
    :param date_array: Array of Dates. The index in this array of the target date will be returned.
    :return: Index of target date in date_array or None
    """
    for index, d in enumerate(date_array):
        if target == d:
            return index
    return None


# todo: see if better results is a better implementation
def sort_by_candidate(candidates, titles, vader_scores, textblob_scores, lstm_scores, news_co, dates):
    """
    Sorts the results into a dict with candidate names as keys and
    :param candidates:
    :param titles:
    :param vader_scores:
    :param textblob_scores:
    :param lstm_scores:
    :param news_co:
    :param dates:
    :return:
    """
    results = {}
    better_results = {}
    for candidate in candidates:
        results[candidate] = []
        better_results[candidate] = {
            'titles': [],
            'vader_scores': [],
            'textblob_scores': [],
            'lstm_scores': [],
            'news_co': [],
            'dates': [],
        }
        for index, title in enumerate(titles):
            if candidate in title.upper():
                results[candidate].append((title,
                                           vader_scores[index],
                                           textblob_scores[index],
                                           lstm_scores[index],
                                           news_co[index],
                                           dates[index]))
                better_results[candidate]['titles'].append(title)
                better_results[candidate]['vader_scores'].append(vader_scores[index])
                better_results[candidate]['textblob_scores'].append(textblob_scores[index])
                better_results[candidate]['lstm_scores'].append(lstm_scores[index])
                better_results[candidate]['news_co'].append(news_co[index])
                better_results[candidate]['dates'].append(dates[index])
    return results


# todo: don't forget about news_co
def sort_by_news_co(news_companies, titles, vader_scores, textblob_scores, lstm_scores, news_co, dates):
    results = {}
    better_results = {}
    for news_name in news_companies:
        results[news_name] = []
        better_results[news_name] = {
            'titles': [],
            'vader_scores': [],
            'textblob_scores': [],
            'lstm_scores': [],
            'news_co': [],
            'dates': [],
        }
        for index, title in enumerate(titles):
            if news_name in title.upper():
                results[news_name].append((title,
                                           vader_scores[index],
                                           textblob_scores[index],
                                           lstm_scores[index],
                                           news_co[index],
                                           dates[index]))
                better_results[news_name]['titles'].append(title)
                better_results[news_name]['vader_scores'].append(vader_scores[index])
                better_results[news_name]['textblob_scores'].append(textblob_scores[index])
                better_results[news_name]['lstm_scores'].append(lstm_scores[index])
                better_results[news_name]['news_co'].append(news_co[index])
                better_results[news_name]['dates'].append(dates[index])
    return results
