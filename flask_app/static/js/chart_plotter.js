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
let options = {
    type: 'line',
    data: {
        labels: [],
        datasets: [{}],
    },
    scales: {
        xAxes: [{
            type: 'time',
            display: true,
            time: {
                unit: 'day',
            },
            scaleLabel: {
                display: true,
                labelString: 'Date'
            }
        }],
    },
    options: {
        tooltips:{
            callbacks:{
                // todo: figure out how to put title of article for tooltip
                // title: function(tooltipItem, data){
                //     return data.datasets[tooltipItem.datasetIndex].titles[tooltipItem['index']] || '';
                // },
                label: function(tooltipItem, data){
                    return data.datasets[tooltipItem.datasetIndex].news_co || '';
                },
                afterLabel: function(tooltipItem, data){
                    return data.labels[tooltipItem['index']]
                }
            }
        },
        title: {
            display: true,
            text: 'plz work',
            fontSize: 30

        },
        legend: {
            display: false,
        },
    }


};
let chart = new Chart(ctx, options);


// let getData = $.get('/data/');
// let allData = $.get('/data/');
let candidateData = $.get('/candidate/all');
let newsData = $.get('/news_company/all');
let getLSTMData = $.post('/analyze/lstm', {text: 'Great win for Bernie Sanders'});
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

getLSTMData.done(function (results) {
    console.log(results)
});

candidateData.done(function (results) {
    console.log(results);
    CANDIDATES.forEach(function (c) {
        plotting_data[c] = {};
        NEWS_KEYS.forEach(function (n) {
            plotting_data[c][n] = results[c][n];
        });
    });
    console.log(plotting_data);
    setDatasets();
    showDataset(BIDEN, CNN_KEY, TEXTBLOB_SCORE_KEY, false);
    chart.update()
});

// newsData.done(function (results) {
//     plotting_data[CNN] = results[CNN_KEY];
//     plotting_data[NYT] = results[NYT_KEY];
//     plotting_data[FOX] = results[FOX_KEY];
// });


function roundToTwo(num) {
    return +(Math.round(num + "e+3") + "e-3");
}

function setLabels(candidate, news_co_key, model_key) {
    chart.data.labels = plotting_data[candidate][news_co_key][DATETIME_KEY];
}

function showDataset(candidate, news_co, model, toggle) {
    news_co = news_co.replace('-', ' ');
    model = model.replace('-', ' ');
    setLabels(candidate, news_co, model);

    chart.data.datasets.forEach(ds => {
        if (ds.label === candidate + '-' + news_co + '-' + model) {
            if (toggle) {
                ds['hidden'] = !ds['hidden'];
            } else {
                ds.hidden = false;
            }
        }
    });
}

function setDatasets() {
    let new_datasets = [];

    CANDIDATES.forEach(c => {
        NEWS_COMPANY_KEYS.forEach(n => {
            MODEL_KEYS.forEach(m => {
                new_datasets.push({
                    label: c + '-' + n + '-' + m,
                    data: plotting_data[c][n][m],
                    borderColor: "rgba(192, 57, 43, 1)",
                    hidden: true,
                    fill: false,
                    titles: plotting_data[c][n]['title'],
                    news_co: n,
                });
            });

        });
    });

    //     [{
    //     label: LABEL_KEY[LSTM_SCORE_KEY],
    //     data: plotting_data[candidate][news_co][LSTM_SCORE_KEY],
    //     borderColor: LINE_COLORS[LSTM],
    //     hidden:false,
    //     fill:false,
    // },{
    //     label: LABEL_KEY[TEXTBLOB_SCORE_KEY],
    //     data: plotting_data[candidate][news_co][TEXTBLOB_SCORE_KEY],
    //     borderColor: LINE_COLORS[TEXTBLOB],
    //     hidden:false,
    //     fill:false,
    // },{
    //     label: LABEL_KEY[VADER_SCORE_KEY],
    //     data: plotting_data[candidate][news_co][VADER_SCORE_KEY],
    //     borderColor: LINE_COLORS[VADER],
    //     hidden:false,
    //     fill:false,
    // }];

    chart.data.datasets = new_datasets;
}

function createDataset(chartIdentifier, news_co) {
    if (chartIdentifier === ALL_MODELS) {
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
        pointRadius: 0,
        pointBorderWidth: 4,
        borderWidth: 2,
        tension: 0.2,
        data: new_data.slice(first_index, second_index)
    }];
}


function toggleView(btn_id) {
    chart.data.datasets.forEach(ds =>{
        ds.hidden = true;
    });

    let active_btns = document.querySelectorAll('.selected-feature');
    let model;
    let candidate;
    let news_co;

    for (let i=0; i < active_btns.length; i++){
        if(active_btns[i].classList.contains('model-btn')){
            model = LABEL_TO_KEY[active_btns[i].id];
        }
        else if(active_btns[i].classList.contains('candidate-btn')){
            candidate = active_btns[i].id;
        }
        else if(active_btns[i].classList.contains('news-btn')){
            news_co = LABEL_TO_KEY[active_btns[i].id];
        }
    }

    showDataset(candidate, news_co, model, false);

    // let key = btn_id.replace('-', ' '); // html id has dashes, these keys have spaces
    // if (key.includes('all')) {
    //     chart.data.datasets.forEach((ds) => {
    //         ds['hidden'] = false;
    //     });
    // } else {
    //     chart.data.datasets.forEach((ds) => {
    //         if (ds['label'] === key) {
    //             ds['hidden'] = !ds['hidden'];
    //         }
    //     });
    // }

    // else if(CANDIDATES.includes(key)){
    //
    // }else if(NEWS_COMPANIES.includes(key)){
    //
    // }

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