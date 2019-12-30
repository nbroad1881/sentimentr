const NOCHANGE = 0;
const TEXTBLOB = 1;
const VADER = 2;
const LSTM = 3;
const BERT = 4;
const ALL_MODELS = 9;

const TEXTBLOB_COLOR = "rgba(192, 57, 43, 1)";
const VADER_COLOR = "rgba(104, 192, 43, 1)";
const LSTM_COLOR = "rgba(43, 178, 192, 1)";
const BERT_COLOR = "rgba(131, 43, 192, 1)";

const DEFAULT_NUM_DAYS = 180;

let getData = $.get('/data/');

let getLSTMData = $.post('/analyze/lstm', {text: 'Great win for Bernie Sanders'})
let classifiers = {};
let titles = [];
let classifier_labels = [];
let news_companies = [];
let chart;
let dates = [];
let dates_averaged = [];
let first_index = 0;
let second_index = -1;
let current_classifier = TEXTBLOB;



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
    set_arrays(results, false);

    const data = {
        labels: classifier_labels,
        datasets: createDatasets(TEXTBLOB)
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

//todo: make scales correct, add lstm
function createDatasets(chartIdentifier) {
    let new_label;
    let new_color;
    let new_fill = false;
    let new_data;

    switch (chartIdentifier) {
        case (TEXTBLOB):
            new_label = 'TextBlob Scores';
            new_color = TEXTBLOB_COLOR;
            break;
        case (VADER):
            new_label = 'Vader Scores';
            new_color = VADER_COLOR;
            break;
        case (LSTM):
            new_label = 'LSTM Scores';
            new_color = LSTM_COLOR;
            break;

        case (BERT):
            new_color = BERT_COLOR;
            break;
        case (ALL_MODELS):
            return [createDatasets(TEXTBLOB)[0], createDatasets(VADER)[0], createDatasets(LSTM)[0]];
        case(NOCHANGE):
            return createDatasets(current_classifier);
    }
    if (chartIdentifier !== NOCHANGE){
        new_data = classifiers[chartIdentifier];
    }

    return [{
        label: new_label,
        fill: new_fill,
        borderColor: new_color,
        backgroundColor: new_color,
        data: new_data.slice(first_index, second_index)
    }];
}

function updateChart(chartIdentifier) {
    chart.options.legend.display = false;
    switch (chartIdentifier) {
        case(TEXTBLOB):
            chart.options.title.text = 'TextBlob Scores';
            current_classifier = TEXTBLOB;
            break;
        case(VADER):
            chart.options.title.text = 'Vader Scores';
            current_classifier = VADER;
            break;
        case(LSTM):
            chart.options.title.text = 'LSTM Scores';
            current_classifier = LSTM;
            break;
        case(ALL_MODELS):
            chart.options.title.text = 'All Models';
            chart.options.legend.display = true;
            current_classifier = ALL_MODELS;
            break;
        case(NOCHANGE):
            if (chart.data.datasets.length > 1) {
                chart.options.legend.display = true;
            }
            break;
        default:
            break;
    }
    chart.data.labels = classifier_labels.slice(first_index, second_index);
    chart.data.datasets = createDatasets(chartIdentifier);
    chart.update();
    console.log(chart);
}


function score(positive, negative) {
    return positive - negative;
}


$("#textblob").click(function () {
    console.log('1');
    updateChart(TEXTBLOB);
});
$("#vader").click(function () {
    console.log('2');
    updateChart(VADER);
});
$("#lstm").click(function () {
    console.log('3');
    updateChart(LSTM);
});
$("#all-models").click(function () {
    updateChart(ALL_MODELS);
});


$(".period").click(function () {
    let period = this.id;
    let indices = [0, dates.length];
    switch (period) {
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
        updateChart(NOCHANGE);
    }

});

// todo: handle data nicely for frequent requests
function set_arrays(results) {
    titles = results['titles'];
    news_companies = results['news_co'];
    console.log(new Date(results['dates_array'][0]));
    console.log(new Date(results['dates_array'][0]));
    console.log(results['dates_array'][0]);
    start_date = new Date();
    // start_date.setUTCDate(results['dates_array'][0])
    dates = make_date_list(new Date(), DEFAULT_NUM_DAYS);
    dates_averaged = results['dates_array'];
    classifiers[TEXTBLOB] = results['textblob_averaged'];
    classifiers[VADER] = results['vader_averaged'];
    classifiers[LSTM] = results['lstm_averaged'];
    classifier_labels = dates;
}

function set_index_window(first_ind, second_ind) {
    first_index = first_ind;
    second_index = second_ind;
    updateChart(NOCHANGE);
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

// # todo: put zeros in the array

function get_date_indices(starting_date, date_array, num_days) {
    let first_index = -1;
    let second_index = date_array.length;
    let second_date = new Date();
    second_date.setUTCDate(starting_date.getUTCDate() - num_days);
    console.log(starting_date);
    console.log(date_array[0], date_array[170]);
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
        last_date = date_array[date_array.length-1];
        //if last date is within range of requested days
        if (last_date < second_date) {
            second_index = first_index + num_days;
        }

    }
    console.log(first_index, second_index);
    return [first_index, second_index];
}
