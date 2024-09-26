import React, { useEffect, useState } from 'react';
import { Typography, Box, Tabs, Tab, Paper } from '@mui/material'; 
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { DashboardYearPage } from './DashboardYearPage'; 
import styled from 'styled-components'; 
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useDashboardYearsChoiceDataQuery } from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { DashboardFilters } from '@components/dashboard/DashboardFilters';

const StyledPaper = styled(
  ({ noMarginTop, extraPaddingLeft, color, ...props }) => <Paper {...props} />,
)`
  padding: 18px 24px;
  padding-left: ${(props) => (props.extraPaddingLeft ? '46px' : '24px')};
  margin-top: ${(props) => (props.noMarginTop ? '0' : '20px')};
  font-size: 18px;
  font-weight: normal;
  
  && > p {
    color: ${(props) => props.color || 'inherit'}
  }

  /* Add chart deselection styles here */
  .dc-chart path.deselected,
  .dc-chart rect.deselected,
  .dc-chart .pie-slice.deselected {
    opacity: 0.2;
  }

  .dc-chart path.selected,
  .dc-chart rect.selected,
  .dc-chart .pie-slice.selected {
    opacity: 1;
  }
`;

export function DashboardPage(): React.ReactElement {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [selectedYear, setSelectedYear] = useState<string | null>(null); // Manage selected year
  const [availableYears, setAvailableYears] = useState<string[]>([]); // Store available years

  // Fetch data from REST API
  const fetchData = async () => {
    try {
      const response = await fetch(`/api/dashboard/${businessArea}`);
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

  useEffect(() => {
    if (data.length === 0) return;

    // Extract unique years from the data
    const years = Array.from(
      new Set(
        data
          .map(household => household.payments.map(payment => new Date(payment.delivery_date).getFullYear()))
          .flat()
      )
    ).sort((a, b) => b - a); // Sort years in descending order

    setAvailableYears(years);
    setSelectedYear(years[0] || null); // Set the highest year (first in the sorted array) as default
  }, [data]);

  if (loading) return <Typography>Loading...</Typography>;
  if (!selectedYear) return <Typography>No data available</Typography>;

  return (
    <Box p={4}>
      <Typography variant="h4">{t('Dashboard')}</Typography>

      {/* Year selection Tabs */}
      <Tabs
        value={selectedYear}
        onChange={(event, newValue) => setSelectedYear(newValue)}
        indicatorColor="primary"
        textColor="primary"
      >
        {availableYears.map((year) => (
          <Tab key={year} value={year} label={year} />
        ))}
      </Tabs>

      {/* Render year-specific data in DashboardYearPage */}
      <DashboardYearPage
        year={selectedYear}
        data={data.filter(household =>
          household.payments.some(payment => new Date(payment.delivery_date).getFullYear() === selectedYear)
        )}
      />
    </Box>
  );
}
