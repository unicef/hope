import React, { useState } from 'react';
import { Button } from '@material-ui/core';
import styled from 'styled-components';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { ReportingFilters } from '../tables/ReportingTable/ReportingFilters';
import { ReportingTable } from '../tables/ReportingTable/ReportingTable';
import { NewReportForm } from '../../components/Reporting/NewReportForm';

export const ReportingPage = () => {
  const businessArea = useBusinessArea();

  const [filter, setFilter] = useState({
    type: '',
    createdAtRange: '',
    status: '',
    onlyMy: false,
  });
  const debouncedFilter = useDebounce(filter, 500);
  return (
    <>
      <PageHeader title='Reporting'>
        <>
          <NewReportForm />
        </>
      </PageHeader>
      <ReportingFilters filter={debouncedFilter} onFilterChange={setFilter} />
      <ReportingTable filter={debouncedFilter} businessArea={businessArea} />
    </>
  );
};
