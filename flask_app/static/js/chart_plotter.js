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
            break;
    }
    if(chartIdentifier === NOCHANGE){
        return chart.data.datasets;
    }

    let new_data = classifiers[chartIdentifier];

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
            break;
        case(VADER):
            chart.options.title.text = 'Vader Scores';
            break;
        case(LSTM):
            chart.options.title.text = 'LSTM Scores';
            break;
        case(ALL_MODELS):
            chart.options.title.text = 'All Models';
            chart.options.legend.display = true;
            break;
        case(NOCHANGE):
            if (chart.data.datasets.length > 1){
                chart.options.legend.display = true;
            }
            break;
        default:
            break;
    }
    chart.data.labels = classifier_labels.slice(first_index, second_index);
    chart.data.datasets = createDatasets(chartIdentifier);
    chart.update();
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
