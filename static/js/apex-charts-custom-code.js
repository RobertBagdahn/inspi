console.log('test')

if (document.getElementById('visitors_per_day')) {
  console.log('visitors_per_day exists')
  let visitors_per_day = document.getElementById('visitors_per_day').textContent;


  // trim
  visitors_per_day = visitors_per_day.trim()

  // replace single quotes with double quotes
  visitors_per_day = visitors_per_day.replace(/'/g, '"')

  // parse json data
  visitors_per_day = JSON.parse(visitors_per_day)



  const options = {
    chart: {
      height: "100%",
      maxWidth: "100%",
      type: "area",
      fontFamily: "Inter, sans-serif",
      dropShadow: {
        enabled: false,
      },
      toolbar: {
        show: false,
      },
    },
    tooltip: {
      enabled: true,
      x: {
        show: false,
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        opacityFrom: 0.55,
        opacityTo: 0,
        shade: "#1C64F2",
        gradientToColors: ["#1C64F2"],
      },
    },
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 6,
    },
    grid: {
      show: false,
      strokeDashArray: 4,
      padding: {
        left: 2,
        right: 2,
        top: 0
      },
    },
    series: [
      {
        name: "New users",
        data: Object.values(visitors_per_day),
        color: "#1A56DB",
      },
    ],
    xaxis: {
      categories: Object.keys(visitors_per_day),
      labels: {
        show: true,
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      show: false,
    },
  }

  if (document.getElementById("area-chart") && typeof ApexCharts !== 'undefined') {
    const chart = new ApexCharts(document.getElementById("area-chart"), options);
    chart.render();
  }
}