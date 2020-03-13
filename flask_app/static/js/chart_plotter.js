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
LINE_COLORS[ALL_NEWS_GROUPS] = "rgba(248, 51, 60, 1)";
LINE_COLORS[TEXTBLOB] = "rgba(248, 51, 60, 1)";
LINE_COLORS[VADER] = "rgba(104, 192, 43, 1)";
LINE_COLORS[LSTM] = "rgba(43, 178, 192, 1)";
LINE_COLORS[BERT] = "rgba(131, 43, 192, 1)";

const CNN_KEY = 'cnn';
const FOX_KEY = 'fox news';
const NYT_KEY = 'the new york times';

const NEWS_KEYS = [CNN_KEY, FOX_KEY, NYT_KEY];
const NEWS_KEYS_TO_NAMES = {};
NEWS_KEYS_TO_NAMES[CNN_KEY] = CNN;
NEWS_KEYS_TO_NAMES[NYT_KEY] = NYT;
NEWS_KEYS_TO_NAMES[FOX_KEY] = FOX;


const DATETIME_KEY = 'datetime';
const LSTM_SCORE_KEY = 'lstm';
const TEXTBLOB_SCORE_KEY = 'textblob';
const VADER_SCORE_KEY = 'vader';
const BERT_SCORE_KEY = 'bert';
const NEWS_CO_KEY = 'news_co';
const URL_KEY = 'url';
const TITLE_KEY = 'title';

const LABEL_TO_KEY = {};
LABEL_TO_KEY['TextBlob'] = TEXTBLOB_SCORE_KEY;
LABEL_TO_KEY['VADER'] = VADER_SCORE_KEY;
LABEL_TO_KEY['LSTM'] = LSTM_SCORE_KEY;
LABEL_TO_KEY['BERT'] = BERT_SCORE_KEY;
LABEL_TO_KEY['CNN'] = CNN_KEY;
LABEL_TO_KEY['Fox-News'] = FOX_KEY;
LABEL_TO_KEY['The-New-York-Times'] = NYT_KEY;


const NEWS_COMPANY_KEYS = [CNN_KEY, FOX_KEY, NYT_KEY];
const MODEL_KEYS = [LSTM_SCORE_KEY, TEXTBLOB_SCORE_KEY, VADER_SCORE_KEY, BERT_SCORE_KEY];

let chart;
let plotting_data = {};

document.addEventListener('DOMContentLoaded', (event) => {
    const ctx = document.getElementById('myChart').getContext('2d');
    let chartOptions = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{}],
        },

        options: {

            spanGaps:true,
            maintainAspectRatio: false,

            tooltips: {
                callbacks: {
                    title: function (tooltipItem, data) {
                        return round_to_three(tooltipItem[0].value);
                    },
                    label: function (tooltipItem, data) {
                        let date = new Date(tooltipItem.label);
                        return date.toDateString();
                    },
                },
                titleFontSize: 18,
                bodyFontSize: 16,
                footerFontSize: 16,
                mode: 'nearest',
                intersect: false,

            },
            title: {
                display: true,
                fontSize: 30,
                text: "Average Weekly Score over Time"
            },
            legend: {
                display: false,
            },
            scaleShowValues: true,
            scales: {
                xAxes: [{
                    distribution:'linear',
                    type: 'time',
                    time: {
                        displayFormats: {
                            month: 'MMM YYYY'
                        },

                    },
                    display: true,
                    ticks: {
                        min: new Date('2019-06-01'),
                        max: new Date(),
                        autoSkip: true,
                        maxTicksLimit: 20,
                        maxRotation: 45,
                        minRotation: 45,
                        source: 'auto',
                        fontFamily: "Merriweather Sans",
                        fontSize: 16,
                    }
                }],
                yAxes: [{
                    display: true,
                    ticks: {
                        min: -1,
                        max: 1,
                        fontFamily: "Merriweather Sans",
                        fontSize: 18,
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Sentiment Score',
                        fontSize: 20,
                        fontFamily: "Merriweather Sans"
                    },
                }]
            },
        }


    };
    chart = new Chart(ctx, chartOptions);

    btns = document.querySelectorAll('.filter-btn');

    for (let i = 0; i < btns.length; i++) {
        btns[i].addEventListener('click', function (event) {
            modifyButtons(btns[i].id);
            toggleView(btns[i].id);
        });
    }


    set_candidates_data('trump', 'cnn', showDataset);
    CANDIDATES.forEach(candidate => {
        plotting_data[candidate] = {};
        NEWS_KEYS.forEach(news => {
            set_candidates_data(candidate, news);
        })
    });

    generate_table();

});

function set_candidates_data(candidate, news_group, callback_) {
    axios.get('/weekly?candidate=' + candidate + "&news_co=" + news_group)
        .then(function (response) {

            plotting_data[candidate][news_group] = response.data;
            let dt_arr = [];
            response.data[DATETIME_KEY].forEach( dt => {
                let new_dt = new Date(dt);
                dt_arr.push(new_dt);
            });

            plotting_data[candidate][news_group][DATETIME_KEY] = dt_arr;

            add_datasets(candidate, news_group);
            if (callback_) {
                callback_(candidate, news_group);
            }
        });
}

function round_to_three(num) {
    return +(Math.round(num + "e+3") + "e-3");
}

function set_labels(candidate, news_co_key) {
    chart.data.labels = plotting_data[candidate][news_co_key][DATETIME_KEY];
}

function showDataset(candidate, news_co, model, toggle) {
    if (!model) {
        model = 'bert'
    }

    news_co = news_co.replace(/-/g, ' ');
    if (candidate.includes('-')) {
        candidate = candidate.slice(0, candidate.indexOf('-'));
    }
    set_labels(candidate, news_co);

    chart.data.datasets = [{
        data: plotting_data[candidate][news_co][model],
        borderColor: "rgba(248, 51, 60, 1)",
        hidden: false,
        fill: false,
        pointRadius: 4,
        pointHitRadius: 6,
        pointBackgroundColor: LINE_COLORS[ALL_NEWS_GROUPS],
    }];


    chart.update({
        duration: 800,
    });
}

function add_datasets(candidate, news_group) {
    MODEL_KEYS.forEach(m => {
        chart.data.datasets.push({
            data: plotting_data[candidate][news_group][m],
            borderColor: "rgba(248, 51, 60, 1)",
            hidden: true,
            fill: false,
            pointRadius: 4,
            pointHitRadius: 6,
            pointBackgroundColor: LINE_COLORS[ALL_NEWS_GROUPS],
        });

    });
    // chart.data.datasets = new_datasets;
}

function toggleView(btn_id) {

    if (btn_id.includes('table')) {
        let candidate = btn_id.slice(0, btn_id.indexOf('-'));
        switch_table_candidate(candidate);
        return
    }

    chart.data.datasets.forEach(ds => {
        ds.hidden = true;
    });

    let model = document.querySelector(".filter-btn.selected-feature.model-btn").id;
    let candidate = document.querySelector(".filter-btn.selected-feature.candidate-btn").id;
    let news_co = document.querySelector(".filter-btn.selected-feature.news-btn").id;

    showDataset(candidate, news_co, model, false);
}

let primary_button_ids = ['textblob', 'lstm', 'vader', 'bert'];
let candidate_chart_ids = ['trump-chart', 'biden-chart', 'warren-chart', 'harris-chart', 'sanders-chart', 'buttigieg-chart'];
let candidate_table_ids = ['trump-table', 'biden-table', 'warren-table', 'harris-table', 'sanders-table', 'buttigieg-table'];
let success_button_ids = ['cnn', 'the-new-york-times', 'fox-news'];

function modifyButtons(btn_id) {
    let highlight = "btn-";
    let outline = "btn-outline-";
    let parentSelector = "";
    if (primary_button_ids.includes(btn_id)) {
        highlight += 'primary';
        outline += 'primary';
        parentSelector = '#model-selector';
    } else if (candidate_chart_ids.includes(btn_id)) {
        highlight += 'secondary';
        outline += 'secondary';
        parentSelector = '#candidate-selector-chart';
    } else if (success_button_ids.includes(btn_id)) {
        highlight += 'success';
        outline += 'success';
        parentSelector = '#news-co-selector';
    } else if (candidate_table_ids.includes(btn_id)) {
        highlight += 'secondary';
        outline += 'secondary';
        parentSelector = '#candidate-selector-table';
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

function generate_table() {
    let table = document.querySelector('.table').getElementsByTagName('tbody')[0];
    axios.get('/table')
        .then(function (response) {
            table_data = response.data;
            for (let element of table_data) {
                if (element['candidate'] !== 'Trump') {
                    continue;
                }
                let row = table.insertRow();
                const columns = ['candidate', 'news_co', 'title', 'datetime', 'textblob', 'vader', 'lstm', 'bert'];
                columns.forEach(col_name => {
                    let cell = row.insertCell();
                    let text;
                    if (col_name === 'datetime') {
                        let dt = new Date(element[col_name]);
                        text = document.createTextNode(dt.toDateString().slice(3));
                    } else {
                        text = document.createTextNode(element[col_name]);
                    }
                    cell.appendChild(text);
                });
            }
        });
}

function switch_table_candidate(candidate) {
    let whole_table = document.querySelector('table');

    let table = document.querySelector('.table').getElementsByTagName('tbody')[0];
    for (let i = 0; i < 5; i++) {
        table.deleteRow(0);
    }
    for (let element of table_data) {
        if (element['candidate'].toLowerCase() !== candidate) {
            continue;
        }

        let row = table.insertRow();
        const columns = ['candidate', 'news_co', 'title', 'datetime', 'textblob', 'vader', 'lstm', 'bert'];
        columns.forEach(col_name => {
            let cell = row.insertCell();
            let text;
            if (col_name === 'datetime') {
                let dt = new Date(element[col_name]);
                text = document.createTextNode(dt.toDateString().slice(3));
            } else {
                text = document.createTextNode(element[col_name]);
            }
            cell.appendChild(text);
        });


    }

}

