import React, { useEffect, useState, useMemo } from 'react';
import { Typography, Box, Grid, Paper } from '@mui/material';
import * as dc from 'dc';
import * as d3 from 'd3';
import crossfilter from 'crossfilter2';
import { useTranslation } from 'react-i18next';
import { Household, HouseholdPayment } from '@api/dashboardApi';

export function DashboardYearPage({ year, data }: { year: string; data: Household[] }) {
  dc.config.defaultColors([...d3.schemeTableau10]);
  const numberFormatter = d3.format(',.2f');
  const { t } = useTranslation();
  console.log(year);
  const [totals, setTotals] = useState({
    totalAmountPaid: 0,
    numberOfPayments: 0,
    outstandingPayments: 0,
    householdsReached: 0,
    pwdReached: 0,
    childrenReached: 0,
    individualsReached: 0,
  });

  const ndx = useMemo(() => {
    if (!data || data.length === 0) return null;

    const processedPayments: HouseholdPayment[] = data
      .flatMap((household: Household) =>
        household.payments.map((payment) => ({
          business_area: household.business_area,
          delivered_quantity: payment.delivered_quantity ? parseFloat(String(payment.delivered_quantity)) : 0,
          delivered_quantity_usd: payment.delivered_quantity_usd ? parseFloat(String(payment.delivered_quantity_usd)) : 0,
          payment_status: payment.status,
          program: household.program,
          admin1: household.admin1,
          admin2: household.admin2,
          sector: household.sector,
          status: payment.status,
          currency: payment.currency,
          fsp: payment.fsp,
          delivery_type: payment.delivery_type,
          size: household.size,
          children_count: household.children_count ? household.children_count : 0,
          id: household.id,
          delivery_date: new Date(payment.delivery_date),
        })),
      );

    return crossfilter(processedPayments);
  }, [data]);

  useEffect(() => {
    if (!ndx) return;

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
      const totalAmountPaid = ndx.groupAll().reduceSum((d: any) => {
        if (['Transaction Successful', 'Distribution Successful', 'Partially Distributed'].includes(d.payment_status)) {
          return d.delivered_quantity_usd;
        }
        return 0;
      }).value() as number;
      const numberOfPayments = ndx.groupAll().reduceCount().value() as number;
      const outstandingPayments = ndx.groupAll().reduceSum((d: any) => {
        if (d.payment_status === 'Pending') {
          return d.delivered_quantity_usd;
        }
        return 0;
      }).value() as number;
      const householdsReached = ndx.dimension((d) => d.id).group().all().length;
      const individualsReached = ndx.groupAll().reduceSum((d) => d.size).value() as  number;
      const pwdReached = householdsReached;
      const childrenReached = ndx.groupAll().reduceSum((d) => d.children_count).value() as number;

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
    const fspChart = dc.pieChart('#fsp-chart');
    fspChart
      .dimension(fspDim)
      .group(fspGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .label(d => `${d.key}: ${numberFormatter((d.value / totals.totalAmountPaid) * 100)}%`)
      .title(d => `${d.key}: ${numberFormatter(d.value)} USD`);

    const deliveryChart = dc.pieChart('#delivery-chart');
    deliveryChart
      .dimension(deliveryDim)
      .group(deliveryGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .label(d => `${d.key}: ${numberFormatter((d.value / totals.totalAmountPaid) * 100)}%`)
      .title(d => `${d.key}: ${numberFormatter(d.value)} USD`);

    const sectorChart = dc.rowChart('#sector-chart');
    sectorChart
      .dimension(sectorDim)
      .group(sectorGroup)
      .elasticX(true)
      .height(300)
      .label(d => `${d.key}: ${numberFormatter(d.value)} USD`)
      .title(d => `${d.key}: ${numberFormatter(d.value)} USD`)
      .xAxis().ticks(4);

    const volumeChart = dc.rowChart('volume-chart');
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
  },  [data, numberFormatter, totals.totalAmountPaid, ndx]);

  return (
    <Box p={4}>
      <Grid container spacing={3}>
        {/* Year in a Glance Section */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography>{t('Total Amount Paid')}</Typography>
                <Typography variant="h5">{numberFormatter(totals.totalAmountPaid)} USD</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>{t('Total No. of Payments')}</Typography>
                <Typography variant="h5">{totals.numberOfPayments}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>{t('Outstanding Payments Amounts')}</Typography>
                <Typography variant="h5">{numberFormatter(totals.outstandingPayments)} USD</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Payment Reach')}</Typography>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography>{t('Total No. of Households Reached')}</Typography>
                <Typography variant="h5">{totals.householdsReached}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>{t('Total No. of PWD Reached')}</Typography>
                <Typography variant="h5">{totals.pwdReached}</Typography>
              </Grid>
              <Grid item xs={4}>
                <Typography>{t('Total No. of Children Reached')}</Typography>
                <Typography variant="h5">{totals.childrenReached}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Payments by FSP')}</Typography>
            <Box id="fsp-chart" />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Payments by Delivery Mechanism')}</Typography>
            <Box id="delivery-chart" />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{('Payments by Sector')}</Typography>
            <Box id="sector-chart" />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Volume by Programme Structure')}</Typography>
            <Box id="volume-chart"/>
          </Paper>
        </Grid>

        {/* Reconciliation and Verification Section */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 2 }}>
            <Typography variant="h6">{t('Reconciliation and Verification')}</Typography>
            <Grid container spacing={2}>
              <Grid item xs={3}>
                <Typography>{t('Payments Reconciled')}</Typography>
                <Typography variant="h5"></Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography>{t('Pending Reconciliation')}</Typography>
                <Typography variant="h5"></Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography>{t('Payments Verified')}</Typography>
                <Typography variant="h5"></Typography>
              </Grid>
              <Grid item xs={3}>
                <Typography>{t('Sites Verified')}</Typography>
                <Typography variant="h5"></Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}