"use strict";

!function (NioApp, $) {
    "use strict";

    var salesRevenue = {
        labels: [translate("January"), translate("February"), translate("March"), translate("April"), translate("May"), translate("June"), translate("July"), translate("August"), translate("September"), translate("October"), translate("November"), translate("December")],
        dataUnit: '',
        stacked: true,
        datasets: [{
            label: "هزینه ها",
            data: JSON.parse(document.getElementById('salesRevenue').getAttribute('data-chart'))
        }]
    };

    var incomeRevenue = {
        labels: [translate("January"), translate("February"), translate("March"), translate("April"), translate("May"), translate("June"), translate("July"), translate("August"), translate("September"), translate("October"), translate("November"), translate("December")],
        dataUnit: '',
        stacked: true,
        datasets: [{
            label: "درآمد",
            data: JSON.parse(document.getElementById('incomeRevenue').getAttribute('data-chart'))
        }]
    };

    function incomeBarChart(selector, set_data) {
        var $selector = selector ? $(selector) : $('.income-bar-chart');

        $selector.each(function () {

            var monthLabels = incomeRevenue.labels;
            var nowUTC = new Date();
            var currentMonthName = monthLabels[nowUTC.getUTCMonth() + 2];
            var currentMonthIndex = monthLabels.indexOf(currentMonthName);

            var colors = [];
            for (var i = 0; i < monthLabels.length; i++) {
                colors.push(
                    i === currentMonthIndex
                        ? NioApp.hexRGB("#53daa2", 1)
                        : NioApp.hexRGB("#53daa2", 0.2)
                );
            }

            incomeRevenue.datasets[0].color = colors;

            var $self = $(this),
                _self_id = $self.attr('id'),
                _get_data = typeof set_data === 'undefined' ? eval(_self_id) : set_data,
                _d_legend = typeof _get_data.legend === 'undefined' ? false : _get_data.legend;
            var selectCanvas = document.getElementById(_self_id).getContext("2d");
            var chart_data = [];
            for (var i = 0; i < _get_data.datasets.length; i++) {
                chart_data.push({
                    label: _get_data.datasets[i].label,
                    data: _get_data.datasets[i].data,
                    // Styles
                    backgroundColor: _get_data.datasets[i].color,
                    borderWidth: 2,
                    borderColor: 'transparent',
                    hoverBorderColor: 'transparent',
                    borderSkipped: 'bottom',
                    barPercentage: .7,
                    categoryPercentage: .7
                });
            }
            var chart = new Chart(selectCanvas, {
                type: 'bar',
                data: {
                    labels: _get_data.labels,
                    datasets: chart_data
                },
                options: {
                    plugins: {
                        legend: {
                            display: _get_data.legend ? _get_data.legend : false,
                            rtl: NioApp.State.isRTL,
                            labels: {
                                boxWidth: 30,
                                padding: 20,
                                color: '#6783b8'
                            }
                        },
                        tooltip: {
                            enabled: true,
                            rtl: NioApp.State.isRTL,
                            callbacks: {
                                title: function title() {
                                    return false;
                                },
                                label: function label(context) {
                                    return "".concat(context.parsed.y, " ").concat(_get_data.dataUnit);
                                }
                            },
                            backgroundColor: '#1c2b46',
                            titleFont: {
                                size: 13
                            },
                            titleColor: '#fff',
                            titleMarginBottom: 4,
                            bodyColor: '#fff',
                            bodyFont: {
                                size: 12
                            },
                            bodySpacing: 10,
                            padding: 12,
                            footerMarginTop: 0,
                            displayColors: false
                        }
                    },
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            display: false,
                            stacked: _get_data.stacked ? _get_data.stacked : false,
                            grid: {
                                display: false,
                                drawBorder: false
                            }
                        },
                        x: {
                            display: true,
                            stacked: _get_data.stacked ? _get_data.stacked : false,

                            grid: {
                                display: false,
                                drawBorder: false
                            },
                            ticks: {
                                display: true,
                                reverse: NioApp.State.isRTL,
                                font: {
                                    size: 9
                                },
                            }
                        }
                    }
                }
            });
        });
    }

    function salesBarChart(selector, set_data) {
        var $selector = selector ? $(selector) : $('.sales-bar-chart');

        $selector.each(function () {

            var monthLabels = salesRevenue.labels;
            var nowUTC = new Date();
            var currentMonthName = monthLabels[nowUTC.getUTCMonth() + 2];
            var currentMonthIndex = monthLabels.indexOf(currentMonthName);

            var colors = [];
            for (var i = 0; i < monthLabels.length; i++) {
                colors.push(
                    i === currentMonthIndex
                        ? NioApp.hexRGB("#f15e80", 1)
                        : NioApp.hexRGB("#f15e80", 0.2)
                );
            }

            salesRevenue.datasets[0].color = colors;

            var $self = $(this),
                _self_id = $self.attr('id'),
                _get_data = typeof set_data === 'undefined' ? eval(_self_id) : set_data,
                _d_legend = typeof _get_data.legend === 'undefined' ? false : _get_data.legend;
            var selectCanvas = document.getElementById(_self_id).getContext("2d");
            var chart_data = [];
            for (var i = 0; i < _get_data.datasets.length; i++) {
                chart_data.push({
                    label: _get_data.datasets[i].label,
                    data: _get_data.datasets[i].data,
                    // Styles
                    backgroundColor: _get_data.datasets[i].color,
                    borderWidth: 2,
                    borderColor: 'transparent',
                    hoverBorderColor: 'transparent',
                    borderSkipped: 'bottom',
                    barPercentage: .7,
                    categoryPercentage: .7
                });
            }
            var chart = new Chart(selectCanvas, {
                type: 'bar',
                data: {
                    labels: _get_data.labels,
                    datasets: chart_data
                },
                options: {
                    plugins: {
                        legend: {
                            display: _get_data.legend ? _get_data.legend : false,
                            rtl: NioApp.State.isRTL,
                            labels: {
                                boxWidth: 30,
                                padding: 20,
                                color: '#6783b8'
                            }
                        },
                        tooltip: {
                            enabled: true,
                            rtl: NioApp.State.isRTL,
                            callbacks: {
                                title: function title() {
                                    return false;
                                },
                                label: function label(context) {
                                    return "".concat(context.parsed.y, " ").concat(_get_data.dataUnit);
                                }
                            },
                            backgroundColor: '#1c2b46',
                            titleFont: {
                                size: 13
                            },
                            titleColor: '#fff',
                            titleMarginBottom: 4,
                            bodyColor: '#fff',
                            bodyFont: {
                                size: 12
                            },
                            bodySpacing: 10,
                            padding: 12,
                            footerMarginTop: 0,
                            displayColors: false
                        }
                    },
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            display: false,
                            stacked: _get_data.stacked ? _get_data.stacked : false,
                            grid: {
                                display: false,
                                drawBorder: false
                            }
                        },
                        x: {
                            display: true,
                            stacked: _get_data.stacked ? _get_data.stacked : false,

                            grid: {
                                display: false,
                                drawBorder: false
                            },
                            ticks: {
                                display: true,
                                reverse: NioApp.State.isRTL,
                                font: {
                                    size: 9
                                },
                            }
                        }
                    }
                }
            });
        });
    }

    // init chart
    NioApp.coms.docReady.push(function () {
        salesBarChart();
        incomeBarChart();
    });
}(NioApp, jQuery);