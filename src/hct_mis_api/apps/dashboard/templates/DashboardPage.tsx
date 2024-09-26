import React, { useEffect, useState, useRef } from 'react';
import { Typography, Box, Grid, Paper } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import * as dc from 'dc';
import * as d3 from 'd3';
import crossfilter from 'crossfilter2';

export function DashboardPage(): React.ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

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

  // Fetch data from REST API
  const fetchData = async () => {
    try {
      const response = await fetch(`/api/dashboard/household-data/${businessArea}`);
      const result = await response.json();
      setData(result);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [businessArea]);

  // Function to update totals
  const updateTotals = (ndx) => {
    const totalAmountPaid = ndx.groupAll().reduceSum(d => d.delivered_quantity_usd).value();
    const numberOfPayments = ndx.groupAll().reduceCount().value();
    const outstandingPayments = ndx.groupAll().reduceSum(d => d.delivered_quantity).value();
    const householdsReached = ndx.dimension(d => d.id).group().all().length;
    const individualsReached = ndx.groupAll().reduceSum(d => d.size).value();
    const pwdReached = householdsReached; // Assuming PWD Reached same as householdsReached
    const childrenReached = ndx.groupAll().reduceSum(d => d.children_count).value();

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

  useEffect(() => {
    if (data.length === 0) return;

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
      }));
    }).flat();
    dc.config.defaultColors(d3.schemeSet3);
    // Crossfilter Setup
    const ndx = crossfilter(processedPayments);

    // Define Dimension and Groups
    const fspDim = ndx.dimension(d => d.fsp);
    const fspGroup = fspDim.group().reduceSum(d => d.delivered_quantity_usd);

    const deliveryDim = ndx.dimension(d => d.delivery_type);
    const deliveryGroup = deliveryDim.group().reduceSum(d => d.delivered_quantity_usd);

    const sectorDim = ndx.dimension(d => d.sector);
    const sectorGroup = sectorDim.group().reduceSum(d => d.delivered_quantity);

    const volumeDim = ndx.dimension(d => d.program);
    const volumeGroup = volumeDim.group().reduceSum(d => d.delivered_quantity);

    // Update Totals initially
    updateTotals(ndx);

    // Render FSP Chart
    const fspChart = dc.pieChart(fspChartRef.current as unknown as HTMLElement);
    fspChart
      .dimension(fspDim)
      .group(fspGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .label(d => `${d.key}: ${((d.value / totals.totalAmountPaid) * 100).toFixed(0)}%`)
      .title(d => `${d.key}: ${d.value.toFixed(2)} USD`)
      .on('filtered', () => {
        updateTotals(ndx);
        dc.redrawAll();
      });

    // Render Delivery Mechanism Chart
    const deliveryChart = dc.pieChart(deliveryChartRef.current as unknown as HTMLElement);
    deliveryChart
      .dimension(deliveryDim)
      .group(deliveryGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .label(d => `${d.key}: ${((d.value / totals.totalAmountPaid) * 100).toFixed(0)}%`)
      .title(d => `${d.key}: ${d.value.toFixed(2)} USD`);

    // Render Sector Chart
    const sectorChart = dc.rowChart(sectorChartRef.current as unknown as HTMLElement);
    sectorChart
      .dimension(sectorDim)
      .group(sectorGroup)
      .elasticX(true)
      .height(300)
      .label(d => `${d.key}: ${d.value.toFixed(2)}`)
      .title(d => `${d.key}: ${d.value.toFixed(2)}`)
      .xAxis().ticks(4);

    // Render Volume Chart
    const volumeChart = dc.rowChart(volumeChartRef.current as unknown as HTMLElement);
    volumeChart
      .dimension(volumeDim)
      .group(volumeGroup)
      .elasticX(true)
      .height(300)
      .label(d => `${d.key}: ${d.value.toFixed(2)}`)
      .title(d => `${d.key}: ${d.value.toFixed(2)}`)
      .xAxis().ticks(4);

    // Finally, render all charts
    dc.renderAll();
  }, [data]);

  if (loading) return <Typography>Loading...</Typography>;

  return (
    <Box p={4}>
      <Typography variant="h4">{t('Payment Dashboard')}</Typography>

      {/* Metrics Section */}
      <Grid container spacing={3} mt={4}>
        <Grid item xs={12} sm={6} md={4}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Total Amount Paid')}</Typography>
            <Typography variant="h4">{totals.totalAmountPaid.toFixed(2)} USD</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Number of Payments')}</Typography>
            <Typography variant="h4">{totals.numberOfPayments}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Outstanding Payment Amounts')}</Typography>
            <Typography variant="h4">{totals.outstandingPayments.toFixed(2)} USD</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Households Reached')}</Typography>
            <Typography variant="h4">{totals.householdsReached}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('PWD Reached')}</Typography>
            <Typography variant="h4">{totals.pwdReached}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Children Reached')}</Typography>
            <Typography variant="h4">{totals.childrenReached}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Individuals Reached')}</Typography>
            <Typography variant="h4">{totals.individualsReached}</Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} mt={4}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Payments by FSP')}</Typography>
            <Box id="fsp-chart" ref={fspChartRef} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Payments by Delivery Mechanism')}</Typography>
            <Box id="delivery-chart" ref={deliveryChartRef} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Payments by Sector')}</Typography>
            <Box id="sector-chart" ref={sectorChartRef} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Volume by Programme Structure')}</Typography>
            <Box id="volume-chart" ref={volumeChartRef} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
