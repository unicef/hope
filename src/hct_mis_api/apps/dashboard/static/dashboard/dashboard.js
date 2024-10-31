document.addEventListener("DOMContentLoaded", function() {
        function fetchDataForCountry() {

            dc.config.defaultColors(d3.schemeTableau10);
            const numberFormatter = d3.format(",.2f");

            function showSpinner(chartId) {
                document.getElementById(chartId).innerHTML =
                    `<div class="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full text-blue-500 border-t-transparent"></div>`;
            }

            function hideSpinner(chartId) {
                document.getElementById(chartId).innerHTML = '';
            }

            const url = householdDataUrl;

            function updateTotals(ndx, successfulPaymentsCount, totalPaymentsCount, pendingPaymentsCount) {
                const totalLocal = ndx.groupAll().reduceSum(d => d.delivered_quantity).value();
                const totalUSD = ndx.groupAll().reduceSum(d => d.delivered_quantity_usd).value();
                const householdsReached = ndx.dimension(d => d.id).group().all().length;
                const individualsReached = ndx.groupAll().reduceSum(d => d.size).value();
                const reconciliationPercentage = (successfulPaymentsCount / totalPaymentsCount) * 100;
                const pendingReconciliationPercentage = (pendingPaymentsCount / totalPaymentsCount) * 100;


                // Update the UI
                document.getElementById("total-amount-paid").innerHTML = `${totalUSD.toFixed(2)} USD`;
                document.getElementById("households-reached").innerHTML = `${householdsReached}`;
                document.getElementById("individuals-reached").innerHTML = `${individualsReached}`;
                document.getElementById("pwd-reached").innerHTML = `${householdsReached}`;
                document.getElementById("total-local-currency").innerHTML = `${totalLocal.toFixed(2)} AFN`;
                document.querySelector(".reconciliation-percentage").innerHTML =
                    `${reconciliationPercentage.toFixed(2)}%`;
                document.querySelector(".pending-reconciliation-percentage").innerHTML =
                    `${pendingReconciliationPercentage.toFixed(2)}%`;
            }

            function createDashboard() {
                // Set up charts
                const fspChart = dc.pieChart('#payments-by-fsp');
                const deliveryChart = dc.pieChart('#payments-by-delivery');
                const sectorChart = dc.rowChart('#payments-by-sector');
                const volumeChart = dc.rowChart('#volume-by-program');


                showSpinner('payments-by-fsp');
                showSpinner('payments-by-delivery');
                showSpinner('payments-by-sector');
                showSpinner('volume-by-program');

                d3.json(url).then(function (data) {
                    let processedPayments = [];

                    data.forEach(household => {
                        household.payments.forEach(payment => {
                            processedPayments.push({
                                business_area: household.business_area,
                                delivered_quantity: payment.delivered_quantity ?
                                    parseFloat(payment.delivered_quantity) : 0,
                                delivered_quantity_usd: payment.delivered_quantity_usd ?
                                    parseFloat(payment.delivered_quantity_usd) : 0,
                                payment_status: payment.status,
                                delivery_date: new Date(payment.delivery_date),
                                year: new Date(payment.delivery_date).getFullYear(),
                                month: new Date(payment.delivery_date).getMonth(),
                                program: household.program,
                                admin1: household.admin1,
                                admin2: household.admin2,
                                sector: household.sector,
                                fsp: payment.fsp,
                                delivery_type: payment.delivery_type,
                                size: household.size,
                                children_count: household.children_count ? household
                                    .children_count : 0,
                                id: household.id
                            });
                        });
                    });

                    processedPayments.sort(function (a, b) {
                        return a.delivery_date - b.delivery_date;
                    });

                    const ndx = crossfilter(processedPayments);
                    const all = ndx.groupAll();

                    function updateTopMetrics() {
                        const totalPaymentsCount = ndx.groupAll().reduceCount().value();
                        const successfulPaymentsGroup = ndx.groupAll().reduce(
                            (p, v) => {
                                if (["Transaction Successful", "Distribution Successful",
                                        "Partially Distributed"
                                    ].includes(v.payment_status)) {
                                    p.count += 1;
                                    p.sum += v.delivered_quantity_usd ? parseFloat(v
                                        .delivered_quantity_usd) : 0;
                                }
                                return p;
                            },
                            (p, v) => {
                                if (["Transaction Successful", "Distribution Successful",
                                        "Partially Distributed"
                                    ].includes(v.payment_status)) {
                                    p.count -= 1;
                                    p.sum -= v.delivered_quantity_usd ? parseFloat(v
                                        .delivered_quantity_usd) : 0;
                                }
                                return p;
                            },
                            () => ({
                                count: 0,
                                sum: 0
                            })
                        ).value();

                        const totalSuccessfulUSD = successfulPaymentsGroup.sum;
                        const successfulPaymentsCount = successfulPaymentsGroup.count;
                        const pendingPaymentsGroup = ndx.groupAll().reduce(
                            (p, v) => {
                                if (v.payment_status === "Pending") {
                                    p.count += 1;
                                    p.sum += v.delivered_quantity_usd ? parseFloat(v
                                        .delivered_quantity_usd) : 0;
                                }
                                return p;
                            },
                            (p, v) => {
                                if (v.payment_status === "Pending") {
                                    p.count -= 1;
                                    p.sum -= v.delivered_quantity_usd ? parseFloat(v
                                        .delivered_quantity_usd) : 0;
                                }
                                return p;
                            },
                            () => ({
                                count: 0,
                                sum: 0
                            })
                        ).value();

                        const totalPendingUSD = pendingPaymentsGroup.sum;
                        const pendingPaymentsCount = pendingPaymentsGroup.count;
                        const householdsReached = ndx.dimension(d => d.id).group().all().length;
                        const individualsReached = ndx.groupAll().reduceSum(d => d.size).value();
                        const childrenReached = ndx.groupAll().reduce(
                            (p, v) => {
                                p += v.children_count ? v.children_count : 0;
                                return p;
                            },
                            (p, v) => {
                                p -= v.children_count ? v.children_count : 0;
                                return p;
                            },
                            () => 0
                        ).value();

                        document.getElementById("number-of-payments").innerHTML =
                            `${numberFormatter(successfulPaymentsCount)}`;
                        document.getElementById("total-amount-paid").innerHTML =
                            `${numberFormatter(totalSuccessfulUSD)} USD`;
                        document.getElementById("total-local-currency").innerHTML =
                            `${numberFormatter(totalPendingUSD)} USD`;
                        document.getElementById("households-reached").innerHTML = `${householdsReached}`;
                        document.getElementById("individuals-reached").innerHTML = `${individualsReached}`;
                        document.getElementById("children-reached").innerHTML = `${childrenReached}`;
                        const reconciliationPercentage = (successfulPaymentsCount / totalPaymentsCount) * 100;
                        const pendingReconciliationPercentage = (pendingPaymentsCount / totalPaymentsCount) *
                            100;

                        document.querySelector(".reconciliation-percentage").innerHTML =
                            `${reconciliationPercentage.toFixed(2)}%`;
                        document.querySelector(".pending-reconciliation-percentage").innerHTML =
                            `${pendingReconciliationPercentage.toFixed(2)}%`;
                    }
                    const dateExtent = d3.extent(processedPayments, function (d) {
                        return d.delivery_date;
                    });

                    const fspDim = ndx.dimension(d => d.fsp);
                    const fspGroup = fspDim.group().reduceSum(d => d.delivered_quantity);
                    fspChart
                        .dimension(fspDim)
                        .group(fspGroup)
                        .radius(100)
                        .innerRadius(30)
                        .renderLabel(true)
                        .useViewBoxResizing(true)
                        .label(function (d) {
                            const percentage = (d.value / fspGroup.all().reduce((sum, g) => sum + g.value,
                                0)) * 100;
                            return `${d.key}:  ${percentage.toFixed(0)}%`;
                        })
                        .title(function (d) {
                            return `${d.key}: ${numberFormatter(d.value)}`;
                        });

                    const deliveryDim = ndx.dimension(d => d.delivery_type);
                    const deliveryGroup = deliveryDim.group().reduceSum(d => d.delivered_quantity);
                    deliveryChart
                        .dimension(deliveryDim)
                        .group(deliveryGroup)
                        .radius(100)
                        .innerRadius(30)
                        .renderLabel(true)
                        .useViewBoxResizing(true)
                        .label(function (d) {
                            const percentage = (d.value / deliveryGroup.all().reduce((sum, g) => sum + g
                                .value, 0)) * 100;
                            return `${d.key} ${percentage.toFixed(0)}%`;
                        })
                        .title(function (d) {
                            return `${d.key}: ${numberFormatter(d.value)}`;
                        });

                    const sectorDim = ndx.dimension(d => d.sector);
                    const sectorGroup = sectorDim.group().reduceSum(d => d.delivered_quantity);
                    sectorChart
                        .dimension(sectorDim)
                        .group(sectorGroup)
                        .elasticX(true)
                        .height(300)
                        .label(function (d) {
                            const total = sectorGroup.all().reduce((sum, g) => sum + g.value, 0);
                            const percentage = (d.value / total) * 100;
                            return `${d.key}: ${numberFormatter(d.value)} (${percentage.toFixed(0)}%)`;
                        })
                        .title(function (d) {
                            return `${d.key}: ${numberFormatter(d.value)}`;
                        })
                        .xAxis().ticks(4);

                    const volumeDim = ndx.dimension(d => d.program);
                    const volumeGroup = volumeDim.group().reduceSum(d => d.delivered_quantity);
                    volumeChart
                        .dimension(volumeDim)
                        .group(volumeGroup)
                        .elasticX(true)
                        .height(300)
                        .label(function (d) {
                            const total = volumeGroup.all().reduce((sum, g) => sum + g.value, 0);
                            const percentage = (d.value / total) * 100;
                            return `${d.key}: ${numberFormatter(d.value)} (${percentage.toFixed(0)}%)`;
                        })
                        .title(function (d) {
                            return `${d.key}: ${numberFormatter(d.value)}`;
                        })
                        .xAxis().ticks(4);

                    hideSpinner('payments-by-fsp');
                    hideSpinner('payments-by-delivery');
                    hideSpinner('payments-by-sector');
                    hideSpinner('volume-by-program');

                    const dcCharts = [fspChart, deliveryChart, sectorChart, volumeChart];
                    dcCharts.forEach(chart => {
                        chart.on('filtered', () => {
                            updateTopMetrics();
                            dc.redrawAll();
                        });
                    });

                    dc.renderAll();

                    updateTopMetrics();
                });
            }
            createDashboard();
        }
        fetchDataForCountry();
    });