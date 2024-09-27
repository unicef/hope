import React, { useEffect, useRef, useState } from 'react';
import { Typography, Box, Grid, Paper } from '@mui/material';
import * as dc from 'dc';
import * as d3 from 'd3';
import crossfilter from 'crossfilter2';

export function DashboardYearPage({ data }) {
  dc.config.defaultColors(d3.schemeTableau10);
  const numberFormatter = d3.format(',.2f');

  const fspChartRef = useRef<HTMLDivElement>(null);
  const deliveryChartRef = useRef<HTMLDivElement>(null);
  const sectorChartRef = useRef<HTMLDivElement>(null);
  const volumeChartRef = useRef<HTMLDivElement>(null);

  const [totals, setTotals] = useState({
    totalAmountPaid: 0,
    numberOfPayments: 0,
    outstandingPayments: 0,
    householdsReached: 0,
    pwdReached: 0,
    childrenReached: 0,
    individualsReached: 0,
  });

  useEffect(() => {
    if (!data || data.length === 0) return;

    const processedPayments = data.map((household) => {
      return household.payments.map((payment) => ({
        business_area: household.business_area,
        delivered_quantity: payment.delivered_quantity ? parseFloat(payment.delivered_quantity) : 0,
        delivered_quantity_usd: payment.delivered_quantity_usd ? parseFloat(payment.delivered_quantity_usd) : 0,
        payment_status: payment.status,
        program: household.program,
        admin1: household.admin1,
        admin2: household.admin2,
        sector: household.sector,
        fsp: payment.fsp,
        delivery_type: payment.delivery_type,
        size: household.size,
        children_count: household.children_count ? household.children_count : 0,
        id: household.id,
        delivery_date: new Date(payment.delivery_date),
      }));
    }).flat();

    const ndx = crossfilter(processedPayments);

    // Define Dimensions and Groups
    const fspDim = ndx.dimension((d) => d.fsp);
    const fspGroup = fspDim.group().reduceSum((d) => d.delivered_quantity_usd);

    const deliveryDim = ndx.dimension((d) => d.delivery_type);
    const deliveryGroup = deliveryDim.group().reduceSum((d) => d.delivered_quantity_usd);

    const sectorDim = ndx.dimension((d) => d.sector);
    const sectorGroup = sectorDim.group().reduceSum((d) => d.delivered_quantity);

    const volumeDim = ndx.dimension((d) => d.program);
    const volumeGroup = volumeDim.group().reduceSum((d) => d.delivered_quantity);

    // Update Totals
    const updateTotals = () => {
      const totalAmountPaid = ndx.groupAll().reduceSum((d) => d.delivered_quantity_usd).value() as number;
      const numberOfPayments = ndx.groupAll().reduceCount().value();
      const outstandingPayments = ndx.dimension(d => d.currency).group().reduceSum((d) => d.delivered_quantity).all()
        .filter(d => d.key)  // Filter valid currencies
        .reduce((acc, { key: currency, value }) => {
          acc[currency] = value;
          return acc;
        }, {});
      const householdsReached = ndx.dimension((d) => d.id).group().all().length;
      const individualsReached = ndx.groupAll().reduceSum((d) => d.size).value();
      const pwdReached = householdsReached;
      const childrenReached = ndx.groupAll().reduceSum((d) => d.children_count).value();

      setTotals({
        totalAmountPaid,
        numberOfPayments,
        outstandingPayments,
        householdsReached,
        individualsReached,
        pwdReached,
        childrenReached,
      });
    };

    updateTotals(); // Call initially to set totals

    // Initialize charts
    const fspChart = dc.pieChart(fspChartRef.current as unknown as HTMLElement);
    fspChart
      .dimension(fspDim)
      .group(fspGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .label(d => `${d.key}: ${numberFormatter((d.value / totals.totalAmountPaid) * 100)}%`)
      .title(d => `${d.key}: ${numberFormatter(d.value)} USD`);

    const deliveryChart = dc.pieChart(deliveryChartRef.current as unknown as HTMLElement);
    deliveryChart
      .dimension(deliveryDim)
      .group(deliveryGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .label(d => `${d.key}: ${numberFormatter((d.value / totals.totalAmountPaid) * 100)}%`)
      .title(d => `${d.key}: ${numberFormatter(d.value)} USD`);

    const sectorChart = dc.rowChart(sectorChartRef.current as unknown as HTMLElement);
    sectorChart
      .dimension(sectorDim)
      .group(sectorGroup)
      .elasticX(true)
      .height(300)
      .label(d => `${d.key}: ${numberFormatter(d.value)} USD`)
      .title(d => `${d.key}: ${numberFormatter(d.value)} USD`)
      .xAxis().ticks(4);

    const volumeChart = dc.rowChart(volumeChartRef.current as unknown as HTMLElement);
    volumeChart
      .dimension(volumeDim)
      .group(volumeGroup)
      .elasticX(true)
      .height(300)
      .label(d => `${d.key}: ${numberFormatter(d.value)} USD`)
      .title(d => `${d.key}: ${numberFormatter(d.value)} USD`)
      .xAxis().ticks(4);

    // Register global listener for filtering
    dc.chartRegistry.list().forEach((chart) => {
      chart.on('filtered', () => {
        updateTotals();
        dc.redrawAll();
      });
    });

    dc.renderAll();
  }, [data]);

  return (
    <Box p={4}>
      <Grid container spacing={3}>
        {/* Year in a Glance Section */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Year in a Glance</Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography>Total Amount Paid</Typography>
                <Typography variant="h5">{numberFormatter(totals.totalAmountPaid)} USD</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>Total No. of Payments</Typography>
                <Typography variant="h5">{totals.numberOfPayments}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>Outstanding Payments Amounts</Typography>
                {/* Display multiple currencies if applicable */}
                <Typography variant="h5">
                  {Object.entries(totals.outstandingPayments).map(([currency, amount]) => (
                    <div key={currency}>{numberFormatter(amount)} {currency}</div>
                  ))}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Payment Reach Section */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Payment Reach</Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography>Total No. of Households Reached</Typography>
                <Typography variant="h5">{totals.householdsReached}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>Total No. of PWD Reached</Typography>
                <Typography variant="h5">{totals.pwdReached}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>Total No. of Children Reached</Typography>
                <Typography variant="h5">{totals.childrenReached}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Charts Section (FSP, Delivery Mechanism, Donor, Sector) */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Payments by FSP</Typography>
            <Box id="fsp-chart" ref={fspChartRef} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Payments by Delivery Mechanism</Typography>
            <Box id="delivery-chart" ref={deliveryChartRef} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Payments by Sector</Typography>
            <Box id="sector-chart" ref={sectorChartRef} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Volume by Programme Structure</Typography>
            <Box id="volume-chart" ref={volumeChartRef} />
          </Paper>
        </Grid>

        {/* Reconciliation and Verification Section */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">Reconciliation and Verification</Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Typography>Payments Reconciled</Typography>
                <Typography variant="h5">82%</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography>Pending Reconciliation</Typography>
                <Typography variant="h5">6%</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography>Payments Verified</Typography>
                <Typography variant="h5">62%</Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography>Sites Verified</Typography>
                <Typography variant="h5">72%</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
