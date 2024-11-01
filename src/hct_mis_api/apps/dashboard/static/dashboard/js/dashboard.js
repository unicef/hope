document.addEventListener("DOMContentLoaded", function() {
  const currentYear = new Date().getFullYear();
  let isChartsInitialized = false;

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
    console.log(url);

    function createDashboard() {
      ["payments-by-fsp", "payments-by-delivery", "payments-by-sector", "volume-by-program", "payments-by-quarter", "payments-by-month"].forEach(showSpinner);

      d3.json(url).then(function(data) {
        if (!data || data.length === 0) {
          console.error("No data available or data is undefined.");
          return;
        }

        let processedPayments = data.flatMap(household =>
          household.payments.map(payment => {
            const deliveryDate = payment.delivery_date ? new Date(payment.delivery_date) : null;
            return {
            delivered_quantity: payment.delivered_quantity ? parseFloat(payment.delivered_quantity) : 0,
            delivered_quantity_usd: payment.delivered_quantity_usd ? parseFloat(payment.delivered_quantity_usd) : 0,
            payment_status: payment.status,
            delivery_date: payment.delivery_date ? new Date(payment.delivery_date) : null,
            year: deliveryDate ? deliveryDate.getFullYear() : 'Unknown',
            month: deliveryDate ? deliveryDate.getMonth() : 'Unknown',
            quarter: deliveryDate ? Math.floor(deliveryDate.getMonth() / 3) + 1 : 'Unknown',
            program: household.program,
            sector: household.sector,
            fsp: payment.fsp,
            delivery_type: payment.delivery_type,
            size: household.size,
            children_count: household.children_count || 0,
            id: household.id,
            pwd_count: household.pwd_count || 0
          }})
        );

        const ndx = crossfilter(processedPayments);

        // Define dimensions and groups
        const yearDim = ndx.dimension(d => d.year);
        const fspDim = ndx.dimension(d => d.fsp);
        const deliveryDim = ndx.dimension(d => d.delivery_type);
        const sectorDim = ndx.dimension(d => d.sector);
        const volumeDim = ndx.dimension(d => d.program);
        const idDim = ndx.dimension(d => d.id);
        const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        const monthDim = ndx.dimension(d => monthNames[d.month]);
        const quarterDim = ndx.dimension(d => `Q${d.quarter}`);

        const fspGroup = fspDim.group().reduceSum(d => d.delivered_quantity_usd);
        const deliveryGroup = deliveryDim.group().reduceSum(d => d.delivered_quantity_usd);
        const sectorGroup = sectorDim.group().reduceSum(d => d.delivered_quantity_usd);
        const volumeGroup = volumeDim.group().reduceSum(d => d.delivered_quantity_usd);
        const quarterGroup = quarterDim.group().reduceSum(d => d.delivered_quantity_usd);
        const monthGroup = monthDim.group().reduceSum(d => d.delivered_quantity_usd);

        // Define charts
        const fspChart = dc.pieChart('#payments-by-fsp')
          .dimension(fspDim)
          .group(fspGroup)
          .radius(100)
          .innerRadius(40)
          .renderLabel(true)
          .useViewBoxResizing(true)
          .label(d => `${d.key}: ${(d.value / fspGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%`)
          .title(d => `${d.key}: ${numberFormatter(d.value)}`);

        const deliveryChart = dc.pieChart('#payments-by-delivery')
          .dimension(deliveryDim)
          .group(deliveryGroup)
          .radius(100)
          .innerRadius(30)
          .renderLabel(true)
          .useViewBoxResizing(true)
          .label(d => `${d.key} ${(d.value / deliveryGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%`)
          .title(d => `${d.key}: ${numberFormatter(d.value)}`);

        const sectorChart = dc.rowChart('#payments-by-sector')
          .dimension(sectorDim)
          .group(sectorGroup)
          .elasticX(true)
          .height(300)
          .label(d => `${d.key}: ${numberFormatter(d.value)} USD (${(d.value / sectorGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%)`)
          .title(d => `${d.key}: ${numberFormatter(d.value)} USD`)
          .xAxis().ticks(4);

        const volumeChart = dc.rowChart('#volume-by-program')
          .dimension(volumeDim)
          .group(volumeGroup)
          .elasticX(true)
          .height(300)
          .label(d => `${d.key}: ${numberFormatter(d.value)} USD (${(d.value / volumeGroup.all().reduce((sum, g) => sum + g.value, 0) * 100).toFixed(0)}%)`)
          .title(d => `${d.key}: ${numberFormatter(d.value)} USD`)
          .xAxis().ticks(4);

        const monthChart = dc.pieChart("#payments-by-month")
          .dimension(monthDim)
          .group(monthGroup)
          .radius(100)
          .innerRadius(40)
          .renderLabel(true)
          .useViewBoxResizing(true)
          .label(d => `${d.key}`)
          .title(d => `${d.key}: ${numberFormatter(d.value)} USD`);
        
        const quarterChart = dc.pieChart("#payments-by-quarter")
          .dimension(quarterDim)
          .group(quarterGroup)
          .radius(100)
          .innerRadius(40)
          .renderLabel(true)
          .useViewBoxResizing(true)
          .label(d => `${d.key}`)
          .title(d => `${d.key}: ${numberFormatter(d.value)} USD`);
            

        function updateTopMetrics() {
          const totalPaymentsCount = ndx.groupAll().reduceCount().value();
          const successfulPaymentsGroupUSD = ndx.groupAll().reduce(
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
            () => ({ count: 0, sum: 0 })
          ).value();

          const totalSuccessfulUSD = successfulPaymentsGroupUSD.sum;
          console.log(totalSuccessfulUSD);
          const successfulPaymentsCountUSD = successfulPaymentsGroupUSD.count;
          const pendingPaymentsGroupUSD = ndx.groupAll().reduce(
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
          console.log( successfulPaymentsCountUSD.sum, totalPaymentsCount, pendingPaymentsGroupUSD.count);
          
          document.getElementById("number-of-payments").innerHTML = `${successfulPaymentsCountUSD}`;
          document.getElementById("outstanding-payments").innerHTML = `${numberFormatter(pendingPaymentsGroupUSD.sum)} USD`;
          document.getElementById("total-amount-paid").innerHTML = `${numberFormatter(totalSuccessfulUSD)} USD`;
          document.getElementById("households-reached").innerHTML = `${householdsReached}`;
          document.getElementById("individuals-reached").innerHTML = `${individualsReached}`;
          document.getElementById("pwd-reached").innerHTML = `${pwdReached}`;
          document.getElementById("children-reached").innerHTML = `${childrenReached}`;
          document.querySelector(".reconciliation-percentage").innerHTML = `${((successfulPaymentsCountUSD / totalPaymentsCount) * 100).toFixed(2)}%`;
          document.querySelector(".pending-reconciliation-percentage").innerHTML = `${((pendingPaymentsGroupUSD / totalPaymentsCount) * 100).toFixed(2)}%`;
        }

        function filterByYear(year) {
          yearDim.filter(year);
          updateTopMetrics();
          if (isChartsInitialized) dc.redrawAll();
        }

        function setActiveTab(year) {
          document.querySelectorAll(".tab-link").forEach(tab => tab.classList.remove("active"));
          document.getElementById(`tab-${year}`).classList.add("active");
        }

        window.changeYear = function(year) {
          setActiveTab(year);
          filterByYear(year);
        };

        const uniqueYears = Array.from(new Set(processedPayments.map(d => d.year))).sort((a, b) => b - a);
        const tabListContainer = document.querySelector("#year-tabs .tab-list");

        uniqueYears.forEach(year => {
          const yearTab = document.createElement("button");
          yearTab.className = "tab-link py-2 px-4 font-semibold";
          yearTab.id = `tab-${year}`;
          yearTab.textContent = year;
          yearTab.onclick = () => changeYear(year);
          tabListContainer.appendChild(yearTab);
        });

        if (uniqueYears.includes(currentYear)) changeYear(currentYear);
        else if (uniqueYears.length > 0) changeYear(uniqueYears[0]);

        const dcCharts = [fspChart, deliveryChart, sectorChart, volumeChart, quarterChart, monthChart];
        dcCharts.forEach(chart => {
          if (chart.on) chart.on('filtered', updateTopMetrics);
        });

        hideSpinner("payments-by-fsp");
        hideSpinner("payments-by-delivery");
        hideSpinner("payments-by-sector");
        hideSpinner("volume-by-program");
        hideSpinner("payments-by-quarter");
        hideSpinner("payments-by-month");

        dc.renderAll();
        isChartsInitialized = true;
      });
    }

    createDashboard();
  }

  fetchDataForCountry();
});
