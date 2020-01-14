const TEXTBLOB = 1;
const VADER = 2;
const LSTM = 3;
const BERT = 4;
const ALL_MODELS = 100;


const CLASSIFIER_TITLE = {};
CLASSIFIER_TITLE[TEXTBLOB] = 'TextBlob Scores';
CLASSIFIER_TITLE[VADER] = 'VADER Scores';
CLASSIFIER_TITLE[LSTM] = 'LSTM Scores';
CLASSIFIER_TITLE[ALL_MODELS] = 'All Models';

const CNN = 'CNN';
const NYT = "New York Times";
const FOX = 'Fox News';
const ALL_NEWS_GROUPS = 'all_groups';

const POINT_STYLES = {};
POINT_STYLES[ALL_NEWS_GROUPS] = 'rectRot';
POINT_STYLES[CNN] = 'circle';
POINT_STYLES[NYT] = 'rect';
POINT_STYLES[FOX] = 'triangle';

const NEWS_COMPANIES = {};
NEWS_COMPANIES[ALL_NEWS_GROUPS] = '';
NEWS_COMPANIES[CNN] = 'CNN';
NEWS_COMPANIES[NYT] = "New York Times";
NEWS_COMPANIES[FOX] = 'Fox News';

const LINE_COLORS = {};
LINE_COLORS[ALL_NEWS_GROUPS] = "rgba(192, 57, 43, 1)";
LINE_COLORS[TEXTBLOB] = "rgba(192, 57, 43, 1)";
LINE_COLORS[VADER] = "rgba(104, 192, 43, 1)";
LINE_COLORS[LSTM] = "rgba(43, 178, 192, 1)";
LINE_COLORS[BERT] = "rgba(131, 43, 192, 1)";

const DEFAULT_NUM_DAYS = 180;

let getData = $.get('/data/');
let getLSTMData = $.post('/analyze/lstm', {text: 'Great win for Bernie Sanders'});
let classifiers = {};
classifiers[TEXTBLOB] = {};
classifiers[VADER] = {};
classifiers[LSTM] = {};
let titles = [];
let classifier_labels = [];
let news_companies = [];
let chart;
let dates = [];
let first_index = 0;
let second_index = -1;
let current_classifier = TEXTBLOB;
let current_news = ALL_NEWS_GROUPS;
let second_news_index;


$("#text-button").click(function () {
    let model = $('label.active').text().trim();
    let text_field = $('#text-field').val();
    $.post("/analyze/textblob", {text: text_field}, function (data) {
        console.log(data);
    });
});

getLSTMData.done(function (results) {
    console.log(results)
});


getData.done(function (results) {
    const ctx = document.getElementById('myChart').getContext('2d');
    set_variables(results);

    const data = {
        labels: classifier_labels,
        datasets: createDataset(TEXTBLOB, ALL_NEWS_GROUPS)
    };
    const options = {
        type: 'line',

        data: data,
        aspectRatio: 2,

        options: {
            tooltips: {
                callbacks: {
                    title: function (tooltipItems) {
                        let index = tooltipItems[0].index;
                        let news_co = news_companies[index];
                        let score = tooltipItems[0].value;
                        let date = classifier_labels[index];
                        let minutes = date.getUTCMinutes();
                        if (minutes < 10) {
                            minutes = '0' + String(minutes);
                        }
                        let hour_min = date.getUTCHours() + ':' + minutes;

                        return roundToTwo(score) + ' - ' + news_co + ' - ' + date.toDateString() + ' - ' + hour_min;
                    },

                    label: function (tooltipItem) {

                        return titles[tooltipItem.index];
                    }
                },
                titleFontSize: 20,
                bodyFontSize: 16,

            },
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    time: {
                        unit: 'day',
                        //     displayFormats: {
                        //         day: 'MMM Do HA'
                        // }
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Date'
                    }
                }],
            },
            title: {
                display: true,
                text: 'TextBlob Scores',
                fontSize: 30
            },
            legend: {
                display: false,
                labels: {
                    fontSize: 18
                }
            }
        }
    };
    chart = new Chart(ctx, options);

});

function roundToTwo(num) {
    return +(Math.round(num + "e+3") + "e-3");
}

function createDataset(chartIdentifier, news_co) {
    if(chartIdentifier === ALL_MODELS){
        return [createDataset(TEXTBLOB, news_co)[0], createDataset(VADER, news_co)[0], createDataset(LSTM, news_co)[0]];
    }
    let styles = get_line_style(chartIdentifier, news_co);
    console.log(classifiers);
    console.log(current_classifier, current_news);
    console.log(chartIdentifier, news_co);
    console.log(classifiers[chartIdentifier]);
    let new_data = classifiers[chartIdentifier][news_co];
    return [{
        label: styles['label'],
        fill: false,
        borderColor: styles['color'],
        backgroundColor: 'rgba(255,255,255,1)',
        pointStyle: styles['point'],
        pointRadius:0,
        pointBorderWidth:4,
        borderWidth:2,
        tension:0.2,
        data: new_data.slice(first_index, second_index)
    }];
}

function updateChart(chartIdentifier, news_co) {
    chart.options.legend.display = false;
    chart.options.title.text = CLASSIFIER_TITLE[chartIdentifier];
    current_classifier = chartIdentifier;
    current_news = news_co;

    if (chartIdentifier === ALL_MODELS || news_co !== ALL_NEWS_GROUPS) {
        chart.options.legend.display = true;
    }

    chart.data.labels = classifier_labels.slice(first_index, second_index);
    chart.data.datasets = createDataset(chartIdentifier, news_co);
    chart.update();
}

//Returns a two element array.
//First element is new label
//Second element is new border dash style
function get_line_style(chartIdentifier, news_co) {
    if (news_co !== null) {
        return {
            label: NEWS_COMPANIES[news_co] + ' ' + CLASSIFIER_TITLE[chartIdentifier],
            color: LINE_COLORS[chartIdentifier],
            point: POINT_STYLES[news_co],
        };
    }
    return {
        label: CLASSIFIER_TITLE[chartIdentifier],
        color: LINE_COLORS[chartIdentifier],
        point: POINT_STYLES[ALL_NEWS_GROUPS],
    };
}


$("#textblob").click(function () {
    console.log('1');
    updateChart(TEXTBLOB, current_news);
});
$("#vader").click(function () {
    console.log('2');
    updateChart(VADER, current_news);
});
$("#lstm").click(function () {
    console.log('3');
    updateChart(LSTM, current_news);
});
$("#all-models").click(function () {
    updateChart(ALL_MODELS, current_news);
});

$(".news-btn").click(function () {
    let news_btn = this.id;
    switch (news_btn) {
        case "cnn":
            updateChart(current_classifier, CNN);
            console.log("*******************************");
            console.log(current_classifier, current_news, CNN);
            break;
        case "nyt":
            updateChart(current_classifier, NYT);
            break;
        case "fox":
            updateChart(current_classifier, FOX);
            break;
        case "all-news":
            updateChart(current_classifier, ALL_NEWS_GROUPS);
            break;
        default:
            break;
    }
});


$(".filter-btn").click(function () {
    let filter_btn = this.id;
    let indices = [0, dates.length];
    //todo: change starting date to be custom
    switch (filter_btn) {
        case "1w":
            indices = get_date_indices(new Date(), dates, 7);
            break;
        case "2w":
            indices = get_date_indices(new Date(), dates, 14);
            break;
        case "1m":
            indices = get_date_indices(new Date(), dates, 30);
            break;
        case "3m":
            indices = get_date_indices(new Date(), dates, 90);
            break;
        case "6m":
            indices = get_date_indices(new Date(), dates, 180);
            break;
        default:
            break;
    }
    if (indices[0] !== -1) {
        first_index = indices[0];
        second_index = indices[1];
        if (second_news_index === -1) {
            second_news_index = second_index;
        }
        updateChart(current_classifier, current_news);
    }

});

function set_variables(results) {
    console.log(results);
    titles = results['titles'];
    news_companies = results['news_co'];
    classifiers[TEXTBLOB][ALL_NEWS_GROUPS] = results['textblob_averaged'];
    classifiers[TEXTBLOB][CNN] = results['cnn_textblob_averaged'];
    classifiers[TEXTBLOB][NYT] = results['nyt_textblob_averaged'];
    classifiers[TEXTBLOB][FOX] = results['fox_textblob_averaged'];

    classifiers[VADER][ALL_NEWS_GROUPS] = results['vader_averaged'];
    classifiers[VADER][CNN] = results['cnn_vader_averaged'];
    classifiers[VADER][NYT] = results['nyt_vader_averaged'];
    classifiers[VADER][FOX] = results['fox_vader_averaged'];

    classifiers[LSTM][ALL_NEWS_GROUPS] = results['lstm_averaged'];
    classifiers[LSTM][CNN] = results['cnn_lstm_averaged'];
    classifiers[LSTM][NYT] = results['nyt_lstm_averaged'];
    classifiers[LSTM][FOX] = results['fox_lstm_averaged'];

    dates = make_date_list(new Date(), DEFAULT_NUM_DAYS);
    classifier_labels = dates;
}


//Starting date should be a Date object
function make_date_list(starting_date, number_of_days) {
    if (starting_date === null) {
        starting_date = new Date();
    }
    let date_array = [];
    for (let i = 0; i < number_of_days; i++) {
        new_date = new Date();
        new_date.setUTCDate(starting_date.getUTCDate() - i);
        date_array.push(new_date);
    }
    return date_array;
}

function get_date_indices(starting_date, date_array, num_days) {
    let first_index = -1;
    let second_index = date_array.length;
    let second_date = new Date();
    second_date.setUTCDate(starting_date.getUTCDate() - num_days);
    for (let i = 0; i < date_array.length; i++) {
        // check for same year, month, day
        let correct_day = (starting_date.getUTCDate() === date_array[i].getUTCDate());
        let correct_month = (starting_date.getUTCMonth() === date_array[i].getUTCMonth());
        let correct_year = (starting_date.getUTCFullYear() === date_array[i].getUTCFullYear());
        if (correct_day && correct_month && correct_year) {
            first_index = i;
        }
    }
    if (first_index !== -1) {
        last_date = date_array[date_array.length - 1];
        //if last date is within range of requested days
        if (last_date < second_date) {
            second_index = first_index + num_days;
        }

    }
    return [first_index, second_index];
}