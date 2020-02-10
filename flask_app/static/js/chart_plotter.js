const TEXTBLOB = 'textblob';
const VADER = 'vader';
const LSTM = 'lstm';
const BERT = 'bert';
const ALL_MODELS = 'all models';


const MODELS = [TEXTBLOB, VADER, LSTM, BERT, ALL_MODELS];

const CNN = 'CNN';
const NYT = "The New York Times";
const FOX = 'Fox News';
const ALL_NEWS_GROUPS = 'all news';

const NEWS_COMPANIES = [CNN, NYT, FOX];

const TRUMP = 'trump';
const BIDEN = 'biden';
const WARREN = 'warren';
const SANDERS = 'sanders';
const HARRIS = 'harris';
const BUTTIGIEG = 'buttigieg';
const CANDIDATES = [TRUMP, BIDEN, WARREN, HARRIS, SANDERS, BUTTIGIEG];


const LINE_COLORS = {};
LINE_COLORS[ALL_NEWS_GROUPS] = "rgba(192, 57, 43, 1)";
LINE_COLORS[TEXTBLOB] = "rgba(192, 57, 43, 1)";
LINE_COLORS[VADER] = "rgba(104, 192, 43, 1)";
LINE_COLORS[LSTM] = "rgba(43, 178, 192, 1)";
LINE_COLORS[BERT] = "rgba(131, 43, 192, 1)";

const DEFAULT_NUM_DAYS = 180;

const CNN_KEY = 'cnn';
const FOX_KEY = 'fox news';
const NYT_KEY = 'the new york times';

const NEWS_KEYS = [CNN_KEY, FOX_KEY, NYT_KEY];
const NEWS_KEYS_TO_NAMES = {};
NEWS_KEYS_TO_NAMES[CNN_KEY]=  CNN;
NEWS_KEYS_TO_NAMES[NYT_KEY]= NYT;
NEWS_KEYS_TO_NAMES[FOX_KEY]= FOX;


const DATETIME_KEY = 'datetime';
const LSTM_SCORE_KEY = 'lstm_score';
const TEXTBLOB_SCORE_KEY = 'textblob_score';
const VADER_SCORE_KEY = 'vader_score';
const NEWS_CO_KEY = 'news_co';
const URL_KEY = 'url';
const TITLE_KEY = 'title';

// const LABEL_KEY = {};
// LABEL_KEY[CNN_KEY] = 'CNN';
// LABEL_KEY[FOX_KEY] = 'Fox News';
// LABEL_KEY[NYT_KEY] = 'The New York Times';
// LABEL_KEY[LSTM_SCORE_KEY] = 'LSTM';
// LABEL_KEY[TEXTBLOB_SCORE_KEY] = 'TextBlob';
// LABEL_KEY[VADER_SCORE_KEY] = 'VADER';

const LABEL_TO_KEY = {};
LABEL_TO_KEY['TextBlob'] = TEXTBLOB_SCORE_KEY;
LABEL_TO_KEY['VADER'] = VADER_SCORE_KEY;
LABEL_TO_KEY['LSTM'] = LSTM_SCORE_KEY;
LABEL_TO_KEY['CNN'] = CNN_KEY;
LABEL_TO_KEY['Fox-News'] = FOX_KEY;
LABEL_TO_KEY['The-New-York-Times'] = NYT_KEY;


const NEWS_COMPANY_KEYS = [CNN_KEY, FOX_KEY, NYT_KEY];
const MODEL_KEYS = [LSTM_SCORE_KEY, TEXTBLOB_SCORE_KEY, VADER_SCORE_KEY];


let plotting_data = {};


const ctx = document.getElementById('myChart').getContext('2d');
let chartOptions = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{}],
    },

    options: {
        tooltips: {
            callbacks: {
                // todo: figure out how to put title of article for tooltip
                title: function (tooltipItem, data) {
                    let current_dataset = data.datasets[tooltipItem[0].datasetIndex];
                    console.log(current_dataset);
                    console.log(current_dataset.titles);
                    return data.datasets[tooltipItem[0].datasetIndex].titles[tooltipItem[0].index] || '';
                },
                label: function (tooltipItem, data) {
                    date = new Date(data.labels[tooltipItem['index']]);
                    news_group = data.datasets[tooltipItem.datasetIndex].news_co;
                    return NEWS_KEYS_TO_NAMES[news_group] + " - " + date.toDateString() || '';
                },
                labelColor: function (tooltipItem, chart) {
                    return {
                        borderColor: LINE_COLORS[ALL_NEWS_GROUPS],
                        backgroundColor: LINE_COLORS[ALL_NEWS_GROUPS],
                    };
                },
            },
            titleFontSize: 18,
            bodyFontSize: 16,
            footerFontSize: 16,

        },
        title: {
            display: false,
            text: '',
            fontSize: 30

        },
        legend: {
            display: false,
        },
        scales: {
            xAxes: [{
                // type: 'time',
                display: true,
                // todo: figure out whether to have constant time increments, or constant space between points
                scaleLabel: {
                    display: true,
                    labelString: 'Date',
                },
                ticks: {
                    source: 'data',
                    callback: function (value, index, values) {
                        return value.slice(0, 10);
                    }
                }
            }],
            yAxes: [{

                display: true,
                ticks: {
                    min: -1,
                    max: 1,
                },

            }]
        },
    }


};
let chart = new Chart(ctx, chartOptions);


// let getData = $.get('/data/');
// let allData = $.get('/data/');
let bidenData = $.get('/candidate/biden');
let trumpData = $.get('/candidate/trump');
let sandersData = $.get('/candidate/sanders');
let warrenData = $.get('/candidate/warren');
let buttigiegData = $.get('/candidate/buttigieg');
let harrisData = $.get('/candidate/harris');
let cnnData = $.get('/news/cnn');
let mytData = $.get('/news/nyt');
let foxData = $.get('/news/fox)');
// let getLSTMData = $.post('/analyze/lstm', {text: 'Great win for Bernie Sanders'});
let classifiers = {};
classifiers[TEXTBLOB] = {};
classifiers[VADER] = {};
classifiers[LSTM] = {};
let titles = [];
let classifier_labels = [];
let news_companies = [];
let dates = [];
let first_index = 0;
let second_index = -1;
let current_classifier = TEXTBLOB;
let current_news = ALL_NEWS_GROUPS;
let currentFocus = 'candidates';


$("#text-button").click(function () {
    let model = $('label.active').text().trim();
    let text_field = $('#text-field').val();
    $.post("/analyze/textblob", {text: text_field}, function (data) {
        console.log(data);
    });
});

function add_dataset_from_request(results, candidate) {
    plotting_data[candidate] = {};
    let list_results = turn_to_array(results);
    NEWS_KEYS.forEach(function (n) {
        plotting_data[candidate][n] = {};
        MODEL_KEYS.forEach(function (m) {
            plotting_data[candidate][n][m] = list_results[n][m];
        });
        plotting_data[candidate][n][DATETIME_KEY] = list_results[n][DATETIME_KEY];
        plotting_data[candidate][n][TITLE_KEY] = list_results[n][TITLE_KEY];
        plotting_data[candidate][n][URL_KEY] = list_results[n][URL_KEY];
    });
    // console.log(plotting_data)
    add_datasets(candidate);
}


bidenData.done(function (results) {
    add_dataset_from_request(results, BIDEN);
});
trumpData.done(function (results) {
    add_dataset_from_request(results, TRUMP);
    showDataset(TRUMP, CNN_KEY, TEXTBLOB_SCORE_KEY);
});
sandersData.done(function (results) {
    add_dataset_from_request(results, SANDERS);
});
warrenData.done(function (results) {
    add_dataset_from_request(results, WARREN);
});
buttigiegData.done(function (results) {
    add_dataset_from_request(results, BUTTIGIEG);
});
harrisData.done(function (results) {
    add_dataset_from_request(results, HARRIS);
});
cnnData.done(function (results) {

});
mytData.done(function (results) {

});
foxData.done(function (results) {

});


function roundToTwo(num) {
    return +(Math.round(num + "e+3") + "e-3");
}

function setLabels(candidate, news_co_key) {
    console.log("setLabels" + candidate + " " + news_co_key);
    chart.data.labels = plotting_data[candidate][news_co_key][DATETIME_KEY];
}

function showDataset(candidate, news_co, model, toggle) {
    console.log('showDataset:' + candidate + " " + news_co + " " + model)
    news_co = news_co.replace('-', ' ');
    model = model.replace('-', ' ');
    setLabels(candidate, news_co);

    chart.data.datasets.forEach(ds => {
        if (ds.label === candidate + '-' + news_co + '-' + model) {
            if (toggle) {
                ds['hidden'] = !ds['hidden'];
            } else {
                ds.hidden = false;
            }
        }
    });
    chart.update();
}

function add_datasets(candidate) {
    NEWS_COMPANY_KEYS.forEach(n => {
        MODEL_KEYS.forEach(m => {
            chart.data.datasets.push({
                label: candidate + '-' + n + '-' + m,
                // todo: remove when all candidates work
                data: plotting_data[candidate][n][m],
                borderColor: "rgba(192, 57, 43, 1)",
                hidden: true,
                fill: false,
                titles: plotting_data[candidate][n]['title'],
                news_co: n,
                pointRadius: 4,
                pointHitRadius: 6,
                pointBackgroundColor: LINE_COLORS[ALL_NEWS_GROUPS],
            });
        });

    });
    // chart.data.datasets = new_datasets;
}

function toggleView(btn_id) {
    chart.data.datasets.forEach(ds => {
        ds.hidden = true;
    });

    let active_btns = document.querySelectorAll('.selected-feature');
    let model;
    let candidate;
    let news_co;

    for (let i = 0; i < active_btns.length; i++) {
        if (active_btns[i].classList.contains('model-btn')) {
            model = LABEL_TO_KEY[active_btns[i].id];
        } else if (active_btns[i].classList.contains('candidate-btn')) {
            candidate = active_btns[i].id;
        } else if (active_btns[i].classList.contains('news-btn')) {
            news_co = LABEL_TO_KEY[active_btns[i].id];
        }
    }

    showDataset(candidate, news_co, model, false);
    chart.update();
}

let primary_button_ids = ['TextBlob', 'LSTM', 'VADER', 'all-models'];
let dark_button_ids = ['trump', 'biden', 'warren', 'harris', 'sanders', 'buttigieg'];
let success_button_ids = ['CNN', 'The-New-York-Times', 'Fox-News'];

function modifyButtons(btn_id) {
    let highlight = "btn-";
    let outline = "btn-outline-";
    let parentSelector = "";
    if (primary_button_ids.includes(btn_id)) {
        highlight += 'primary';
        outline += 'primary';
        parentSelector = '#model-selector';
    } else if (dark_button_ids.includes(btn_id)) {
        highlight += 'dark';
        outline += 'dark';
        parentSelector = '#candidate-selector';
    } else if (success_button_ids.includes(btn_id)) {
        highlight += 'success';
        outline += 'success';
        parentSelector = '#news-co-selector';
    }

    let buttons = document.querySelector(parentSelector).children;
    let add = [outline];
    let remove = [highlight, 'selected-feature'];
    for (let i = 0; i < buttons.length; i++) {
        add.forEach(a => {
            buttons[i].classList.add(a);
        });
        remove.forEach(r => {
            buttons[i].classList.remove(r);
        });
    }
    let btn = document.querySelector('#' + btn_id);
    btn.classList.add(highlight);
    btn.classList.add('selected-feature');
    btn.classList.remove(outline);
}

$(".filter-btn").click(function () {
    modifyButtons(this.id);
    toggleView(this.id);
});


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


//Get request gives list of dicts, want dict of lists
function turn_to_array(response) {
    let dict_of_lists = {};

    for (let [news_co, score_list] of Object.entries(response)) {

        let textblob_scores = [];
        let vader_scores = [];
        let lstm_scores = [];
        let dates = [];
        let titles = [];
        let urls = [];

        for (let i = 0; i < score_list.length; i++) {
            let article_scores = score_list[i];
            textblob_scores.push(article_scores['textblob_p_pos'] - article_scores['textblob_p_neg']);
            vader_scores.push(article_scores['vader_p_pos'] - article_scores['vader_p_neg']);
            lstm_scores.push(article_scores['lstm_p_pos'] - article_scores['lstm_p_neg']);
            dates.push(article_scores['datetime']);
            titles.push(article_scores['title']);
            urls.push(article_scores['url']);
        }

        dict_of_lists[news_co] = {
            'textblob_score': textblob_scores,
            'vader_score': vader_scores,
            'lstm_score': lstm_scores,
            'datetime': dates,
            'title': titles,
            'url': urls,
        };
    }
    return dict_of_lists;
}