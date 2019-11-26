
var getData = $.get('/data_test');
var chart_data;
var chart;


getData.done(function (results) {
    chart_data = results;
    const ctx = document.getElementById('myChart').getContext('2d');
    var dates = [];
    var titles = [];
    var news_companies = [];
    results.forEach(function (res) {
        dates.push(new Date(res['datetime']));
        titles.push(res['title']);
        news_companies.push(res['news_co']);
    });
    console.log(dates[0]);
    const data = {
        labels: dates,
        datasets: createDatasets(1)
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
                        if (minutes < 10){}
                            minutes = '0'+String(minutes)
                        let hour_min = date.getHours() + ':' + minutes;

                        return roundToTwo(score) + ' - ' + news_co + ' - ' + date.toDateString() + ' ' + hour_min;
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

function createDatasets(chartNum) {
    var datasets = [];
    switch (chartNum) {
        case (1):
            datasets.push({
                label: 'TextBlob Scores',
                fill: false,
                borderColor: "rgba(192, 57, 43, 1)",
                backgroundColor: "rgba(192, 57, 43, 1)",
                data: []
            });
            chart_data.forEach((row) => {
                datasets[0].data.push(row['textblob_polarity'])
            });
            return datasets;

        case (2):
            datasets.push({
                label: 'Vader Scores',
                fill: false,
                borderColor: "rgba(104, 192, 43, 1)",
                backgroundColor: "rgba(104, 192, 43, 1)",
                data: []
            });
            chart_data.forEach((row) => {
                datasets[0].data.push(row['vader_compound'])
            });
            return datasets;
        case (3):
            datasets.push({
                label: 'LSTM Scores',
                fill: false,
                borderColor: "rgba(43, 178, 192, 1)",
                backgroundColor: "rgba(43, 178, 192, 1)",
                data: []
            });
            chart_data.forEach((row) => {
                datasets[0].data.push(row['lstm_score'])
            });
            return datasets;
        case (4):
            color = "rgba(131, 43, 192, 1)";
            break;
        case (5):
            return [createDatasets(1)[0], createDatasets(2)[0], createDatasets(3)[0]]

    }
}

function updateChart(chartNum) {
    chart.options.legend.display = false;
    if (chartNum === 1) {
        chart.data.datasets = createDatasets(1);
        console.log(chart.data.datasets[0]);
        chart.options.title.text = 'TextBlob Scores';
    } else if (chartNum === 2) {
        chart.data.datasets = createDatasets(2);
        chart.options.title.text = 'Vader Scores';
    } else if (chartNum === 3) {
        chart.data.datasets = createDatasets(3);
        chart.options.title.text = 'LSTM Scores';
    } else if (chartNum === 5) {
        chart.data.datasets = createDatasets(5);
        chart.options.title.text = 'All Models';
        chart.options.legend.display = true;
    }
    chart.update();
}


$("#textblob").click(function () {
    console.log('1');
    updateChart(1);
});
$("#vader").click(function () {
    console.log('2');
    updateChart(2);
});
$("#lstm").click(function () {
    console.log('3');
    updateChart(3);
});
$("#all-models").click(function () {
    console.log('4');
    updateChart(5);
});
