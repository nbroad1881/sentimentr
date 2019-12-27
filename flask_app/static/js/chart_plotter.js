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
console.log(getLSTMData)
let chart_data;
let chart;

$("#text-button").click(function () {
    let model = $('label.active').text().trim();
    let text_field = $('#text-field').val();
    $.post("/analyze/textblob", {text: text_field}, function (data) {
        console.log(data);
    });
});

getLSTMData.done(function (results) {
    console.log(results)
})


getData.done(function (results) {
    chart_data = results;
    const ctx = document.getElementById('myChart').getContext('2d');
    const dates = [];
    const titles = [];
    const news_companies = [];
    results.forEach(function (res) {
        dates.push(new Date(res['datetime']));
        titles.push(res['title']);
        news_companies.push(res['news_co']);
        lstm_data = {
            pos: res['lstm_p_pos'],
            neu: res['lstm_p_neu'],
            neg: res['lstm_p_neg'],
        }
        vader_data = {
            pos: res['vader_positive'],
            neu: res['vader_neutral'],
            neg: res['vader_negative'],
        }
        textblob_data = {
            pos: res['textblob_p_pos'],
            neu: 0,
            neg: res['textblob_p_neg'],
            }
    });
    const data = {
        labels: dates,
        datasets: createDatasets(TEXTBLOB)
    };
    const options = {
        // The type of chart we want to create
        type: 'line',

        // The data for our dataset
        data: data,
        aspectRatio: 2,

        // Configuration options go here
        options: {
            tooltips: {
                callbacks: {
                    title: function (tooltipItems) {
                        let index = tooltipItems[0].index;
                        let news_co = news_companies[index];
                        let score = tooltipItems[0].value;
                        let date = dates[index];
                        let minutes = date.getMinutes();
                        if (minutes < 10) {
                            minutes = '0' + String(minutes);
                        }
                        let hour_min = date.getHours() + ':' + minutes;

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
                    time: {
                        unit: 'day'
                    }
                }]
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
    }
    let new_data = classifiers[chartIdentifier];

    return [{
        label: new_label,
        fill: new_fill,
        borderColor: new_color,
        backgroundColor: new_color,
        data: new_data
    }];
}

function updateChart(chartNum) {
    chart.options.legend.display = false;
    switch (chartNum) {
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
        default:
            chart.options.title.text = 'TextBlob Scores';
            break;
    }
    chart.data.datasets = createDatasets(chartNum);
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
