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

    function createDashboard() {
      showSpinner('payments-by-fsp');
      showSpinner('payments-by-delivery');
      showSpinner('payments-by-sector');
      showSpinner('volume-by-program');

      d3.json(url).then(function(data) {
        let processedPayments = [];
        data.forEach(household => {
          household.payments.forEach(payment => {
            processedPayments.push({
              delivered_quantity: payment.delivered_quantity ? parseFloat(payment.delivered_quantity) : 0,
              delivered_quantity_usd: payment.delivered_quantity_usd ? parseFloat(payment.delivered_quantity_usd) : 0,
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
              children_count: household.children_count || 0,
              id: household.id,
              pwd_count: household.pwd_count || 0
            });
          });
        });

        const ndx = crossfilter(processedPayments);
        
        const fspDim = ndx.dimension(d => d.fsp);
        const deliveryDim = ndx.dimension(d => d.delivery_type);
        const sectorDim = ndx.dimension(d => d.sector);
        const volumeDim = ndx.dimension(d => d.program);
        const admin1Dim = ndx.dimension(d => d.admin1);
        const admin2Dim = ndx.dimension(d => d.admin2);
        const idDim = ndx.dimension(d => d.id);

        const fspGroup = fspDim.group().reduceSum(d => d.delivered_quantity_usd);
        const deliveryGroup = deliveryDim.group().reduceSum(d => d.delivered_quantity_usd);
        const sectorGroup = sectorDim.group().reduceSum(d => d.delivered_quantity_usd);
        const volumeGroup = volumeDim.group().reduceSum(d => d.delivered_quantity_usd);

        const admin1Group = admin1Dim.group();
        const admin2Group = admin2Dim.group();

        const admin1Select = d3.select("#admin1-filter")
          .append("select")
          .classed("block w-full mt-1 bg-white border border-gray-300 text-gray-700 py-2 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-blue-500", true)
          .on("change", updateAdmin2Options);

        admin1Select.append("option")
          .attr("value", "")
          .text("Select Admin1");

        admin1Select.selectAll("option.admin1-option")
          .data(admin1Group.all())
          .enter()
          .append("option")
          .classed("admin1-option", true)
          .attr("value", d => d.key)
          .text(d => d.key);

        const admin2Select = d3.select("#admin2-filter")
          .append("select")
          .classed("block w-full mt-1 bg-white border border-gray-300 text-gray-700 py-2 px-4 pr-8 rounded leading-tight focus:outline-none focus:bg-white focus:border-blue-500", true)
          .on("change", filterByAdmin2);

        admin2Select.append("option")
          .attr("value", "")
          .text("Select Admin2");

        function updateAdmin2Options() {
          const selectedAdmin1 = admin1Select.property("value");

          if (!selectedAdmin1) {
            admin1Dim.filterAll();
            admin2Dim.filterAll();
            admin2Select.property("value", "");

            admin2Select
              .selectAll("option.admin2-option")
              .data(admin2Group.all(), d => d.key)
              .join(
                enter => enter.append("option")
                  .classed("admin2-option", true)
                  .attr("value", d => d.key)
                  .text(d => d.key),
                update => update,
                exit => exit.remove()
              );

            dc.redrawAll();
            updateTopMetrics();
          } else {
            admin1Dim.filter(selectedAdmin1);
            const admin2Options = admin2Group.all().filter(d => d.value > 0);
            admin2Select
              .selectAll("option.admin2-option")
              .data(admin2Options, d => d.key)
              .join(
                enter => enter.append("option")
                  .classed("admin2-option", true)
                  .attr("value", d => d.key)
                  .text(d => d.key),
                update => update,
                exit => exit.remove()
              );

            dc.redrawAll();
            updateTopMetrics();
          }
        }

        function filterByAdmin2() {
          const selectedAdmin2 = admin2Select.property("value");
          admin2Dim.filter(selectedAdmin2 || null);
          dc.redrawAll(); 
        }

        const fspChart = dc.pieChart('#payments-by-fsp');
        fspChart
          .dimension(fspDim)
          .group(fspGroup)
          .radius(100)
          .innerRadius(40)
          .renderLabel(true)
          .useViewBoxResizing(true)
          .label(d => `${d.key}: ${(d.value / fspGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%`)
          .title(d => `${d.key}: ${numberFormatter(d.value)}`);

        const deliveryChart = dc.pieChart('#payments-by-delivery');
        deliveryChart
          .dimension(deliveryDim)
          .group(deliveryGroup)
          .radius(100)
          .innerRadius(30)
          .renderLabel(true)
          .useViewBoxResizing(true)
          .label(d => `${d.key} ${(d.value / deliveryGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%`)
          .title(d => `${d.key}: ${numberFormatter(d.value)}`);

        const sectorChart = dc.rowChart('#payments-by-sector');
        sectorChart
          .dimension(sectorDim)
          .group(sectorGroup)
          .elasticX(true)
          .height(300)
          .label(d => `${d.key}: ${numberFormatter(d.value)} (${(d.value / sectorGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%)`)
          .title(d => `${d.key}: ${numberFormatter(d.value)}`)
          .xAxis().ticks(4);

        const volumeChart = dc.rowChart('#volume-by-program');
        volumeChart
          .dimension(volumeDim)
          .group(volumeGroup)
          .elasticX(true)
          .height(300)
          .label(d => `${d.key}: ${numberFormatter(d.value)} (${(d.value / volumeGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%)`)
          .title(d => `${d.key}: ${numberFormatter(d.value)}`)
          .xAxis().ticks(4);

        function updateTopMetrics() {
          const totalPaymentsCount = ndx.groupAll().reduceCount().value();
          const successfulPaymentsGroup = ndx.groupAll().reduce(
            (p, v) => {
              if (["Transaction Successful", "Distribution Successful", "Partially Distributed"].includes(v.payment_status)) {
                p.count += 1;
                p.sum += v.delivered_quantity_usd || 0;
              }
              return p;
            },
            (p, v) => {
              if (["Transaction Successful", "Distribution Successful", "Partially Distributed"].includes(v.payment_status)) {
                p.count -= 1;
                p.sum -= v.delivered_quantity_usd || 0;
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
                p.sum += v.delivered_quantity_usd || 0;
              }
              return p;
            },
            (p, v) => {
              if (v.payment_status === "Pending") {
                p.count -= 1;
                p.sum -= v.delivered_quantity_usd || 0;
              }
              return p;
            },
            () => ({
              count: 0,
              sum: 0
            })
          ).value();

          const householdsReached = idDim.groupAll().reduceCount().value();
          const individualsReached = ndx.groupAll().reduceSum(d => d.size).value();
          const pwdReached = ndx.groupAll().reduceSum(d => d.pwd_count).value();
          const childrenReached = ndx.groupAll().reduce(
            (p, v) => p + (v.children_count || 0),
            (p, v) => p - (v.children_count || 0),
            () => 0
          ).value();

          document.getElementById("number-of-payments").innerHTML = `${successfulPaymentsCount}`;
          document.getElementById("total-amount-paid").innerHTML = `${numberFormatter(totalSuccessfulUSD)} USD`;
          document.getElementById("total-local-currency").innerHTML = `${numberFormatter(pendingPaymentsGroup.sum)} USD`;
          document.getElementById("households-reached").innerHTML = `${householdsReached}`;
          document.getElementById("pwd-reached").innerHTML = `${pwdReached}`;
          document.getElementById("individuals-reached").innerHTML = `${individualsReached}`;
          document.getElementById("children-reached").innerHTML = `${childrenReached}`;
          document.querySelector(".reconciliation-percentage").innerHTML = `${((successfulPaymentsCount / totalPaymentsCount) * 100).toFixed(2)}%`;
          document.querySelector(".pending-reconciliation-percentage").innerHTML = `${((pendingPaymentsGroup.count / totalPaymentsCount) * 100).toFixed(2)}%`;
        }

        [fspChart, deliveryChart, sectorChart, volumeChart].forEach(chart => {
          chart.on('filtered', () => {
            updateTopMetrics();
            dc.redrawAll();
          });
        });

        hideSpinner('payments-by-fsp');
        hideSpinner('payments-by-delivery');
        hideSpinner('payments-by-sector');
        hideSpinner('volume-by-program');

        dc.renderAll();
        updateTopMetrics();
      });
    }
    createDashboard();
  }
  fetchDataForCountry();
});
