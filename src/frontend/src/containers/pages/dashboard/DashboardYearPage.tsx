import React, { useEffect, useRef, useState } from 'react';
import { Typography, Box, Grid, Paper } from '@mui/material';
import * as dc from 'dc';
import * as d3 from 'd3';
import crossfilter from 'crossfilter2';
import { useTranslation } from 'react-i18next';
import { Household, HouseholdPayment } from '@api/dashboardApi'; // Use the defined types

export function DashboardYearPage({ year, data }: { year: string, data: Household[] }) {
  const { t } = useTranslation();
  dc.config.defaultColors(d3.schemeTableau10);
  const numberFormatter = d3.format(',.2f');

  const fspChartRef = useRef<HTMLDivElement>(null);
  const deliveryChartRef = useRef<HTMLDivElement>(null);
  const sectorChartRef = useRef<HTMLDivElement>(null);
  const volumeChartRef = useRef<HTMLDivElement>(null);

  const [totals, setTotals] = useState({
    totalAmountPaidUsd: 0,
    totalAmountPaidLocal: 0,
    numberOfPayments: 0,
    outstandingPaymentsUsd: 0,
    outstandingPaymentsLocal: 0,
    householdsReached: 0,
    pwdReached: 0,
    childrenReached: 0,
    individualsReached: 0,
  });

  useEffect(() => {
    if (!data || data.length === 0) return;

    // Process payments and define Payment type
    const processedPayments: HouseholdPayment[] = data.map((household: Household) => {
      return household.payments.map((payment: HouseholdPayment) => ({
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
        delivery_date: payment.delivery_date,
        currency: payment.currency,
        status: payment.status,
      }));
    }).flat();

    const ndx = crossfilter(processedPayments);

    // Dimensions
    const fspDim = ndx.dimension((d: any) => d.fsp);
    const deliveryDim = ndx.dimension((d: any) => d.delivery_type);
    const sectorDim = ndx.dimension((d: any) => d.sector);
    const volumeDim = ndx.dimension((d: any) => d.program);

    // Groups
    const fspGroup = fspDim.group().reduceSum((d: any) => d.delivered_quantity);
    const deliveryGroup = deliveryDim.group().reduceSum((d: any) => d.delivered_quantity);
    const sectorGroup = sectorDim.group().reduceSum((d: any) => d.delivered_quantity);
    const volumeGroup = volumeDim.group().reduceSum((d: any) => d.delivered_quantity);

    // Update Totals
    const updateTotals = () => {
      const totalAmountPaidUsd = ndx.groupAll().reduceSum((d: any) => {
        if (['Transaction Successful', 'Distribution Successful', 'Partially Distributed'].includes(d.payment_status)) {
          return d.delivered_quantity_usd;
        }
        return 0;
      }).value() as number;

      const totalAmountPaidLocal = ndx.groupAll().reduceSum((d: any) => {
        if (['Transaction Successful', 'Distribution Successful', 'Partially Distributed'].includes(d.payment_status)) {
          return d.delivered_quantity;
        }
        return 0;
      }).value() as number;

      const outstandingPaymentsUsd = ndx.groupAll().reduceSum((d: any) => {
        if (d.payment_status === 'Pending') {
          return d.delivered_quantity_usd;
        }
        return 0;
      }).value() as number;

      const outstandingPaymentsLocal = ndx.groupAll().reduceSum((d: any) => {
        if (d.payment_status === 'Pending') {
          return d.delivered_quantity;
        }
        return 0;
      }).value() as number;

      const numberOfPayments = ndx.groupAll().reduceCount().value() as number;
      const householdsReached = ndx.dimension((d: any) => d.size).group().all().length;
      const pwdReached = householdsReached;
      const childrenReached = ndx.groupAll().reduceSum((d: any) => d.children_count).value() as number;

      setTotals({
        totalAmountPaidUsd,
        totalAmountPaidLocal,
        outstandingPaymentsUsd,
        outstandingPaymentsLocal,
        numberOfPayments,
        householdsReached,
        pwdReached,
        childrenReached,
        individualsReached: householdsReached, // Assuming households represent individuals here.
      });
    };

    updateTotals();
    console.log(year);
    // FSP Pie Chart
    const fspChart = dc.pieChart(fspChartRef.current as unknown as HTMLElement);
    fspChart
      .dimension(fspDim)
      .group(fspGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .render();

    // Volume Bar Chart (Fixing the missing x attribute error)
    const volumeChart = dc.barChart(volumeChartRef.current as unknown as HTMLElement);
    volumeChart
      .dimension(volumeDim)
      .group(volumeGroup)
      .x(d3.scaleBand()) // Correctly define the x axis
      .xUnits(dc.units.ordinal) // Use ordinal units for categorical data
      .elasticX(true)
      .height(300)
      .label((d) => `${d.key}: ${d.value}`)
      .title((d) => `${d.key}: ${d.value}`)
      .xAxis().ticks(4);

    // Sector Bar Chart (Fixing the missing x attribute error)
    const sectorChart = dc.barChart(sectorChartRef.current as unknown as HTMLElement);
    sectorChart
      .dimension(sectorDim)
      .group(sectorGroup)
      .x(d3.scaleBand()) // Correctly define the x axis
      .xUnits(dc.units.ordinal) // Use ordinal units for categorical data
      .elasticX(true)
      .height(300)
      .label((d) => `${d.key}: ${(d.value || 0).toFixed(2)}`)
      .title((d) => `${d.key}: ${(d.value || 0).toFixed(2)}`)
      .xAxis().ticks(4);

    // Delivery Pie Chart
    const deliveryChart = dc.pieChart(deliveryChartRef.current as unknown as HTMLElement);
    deliveryChart
      .dimension(deliveryDim)
      .group(deliveryGroup)
      .radius(100)
      .innerRadius(30)
      .renderLabel(true)
      .useViewBoxResizing(true)
      .title((d) => `${d.key}: ${numberFormatter(d.value)} USD`)
      .label((d) => `${d.key}: ${numberFormatter((d.value / totals.totalAmountPaidUsd) * 100)}%`)
      .render();

    dc.renderAll();
  }, [data, numberFormatter, totals.totalAmountPaidUsd]);

  return (
    <Box p={4}>
      {/* Year in a Glance */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 3 }}>
            <Typography variant="h5" align="center">
              {t('Year in a Glance')}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ padding: 2 }}>
                  <Typography variant="subtitle1">{t('Total Amount Paid in USD')}</Typography>
                  <Typography variant="h6">{numberFormatter(totals.totalAmountPaidUsd)} USD</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ padding: 2 }}>
                  <Typography variant="subtitle1">{t('Total Amount Paid in Local Currency')}</Typography>
                  <Typography variant="h6">{numberFormatter(totals.totalAmountPaidLocal)} AFN</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ padding: 2 }}>
                  <Typography variant="subtitle1">{t('Outstanding Payments in USD')}</Typography>
                  <Typography variant="h6">{numberFormatter(totals.outstandingPaymentsUsd)} USD</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Paper elevation={1} sx={{ padding: 2 }}>
                  <Typography variant="subtitle1">{t('Outstanding Payments in Local Currency')}</Typography>
                  <Typography variant="h6">{numberFormatter(totals.outstandingPaymentsLocal)} AFN</Typography>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Payment Charts */}
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
