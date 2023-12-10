// base js support file

function drawChart(chartdata) {
    var data = new google.visualization.DataTable(); //arrayToDataTable([
    header = chartdata[0];
    datalines = chartdata.slice(1).map(item => {
        return [new Date(item[0]), item[1], item[2]];
    });
    data.addColumn("date", header[0]);
    data.addColumn("number", header[1]);
    data.addColumn("number", header[2]);
    data.addRows(datalines);

    var options = {
        title: 'Orders history',
        hAxis: { 
            title: 'Date', 
            titleTextStyle: { color: '#333' },
            format: "M-Y" 
        },
        vAxis: { minValue: 0 }
    };

    var chart = new google.visualization.SteppedAreaChart(document.getElementById('trading_history_chart_div'));
    chart.draw(data, options);
}

window.addEventListener("load", () => {
    google.charts.load('current', { 'packages': ['corechart'] });
    var XHR = new XMLHttpRequest();
    XHR.addEventListener('load', function () {
        const responseData = JSON.parse(XHR.responseText);
        drawChart(responseData.data);
    });
    XHR.addEventListener('error', function () {
        console.log("Error loading tradinghistory");
    });
    XHR.open("GET", "/tradinglog/tradinghistory");
    XHR.send();
});