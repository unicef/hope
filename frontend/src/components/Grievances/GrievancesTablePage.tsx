import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { PageHeader } from '../PageHeader';
import { GrievancesFilters } from './GrievancesTable/GrievancesFilters';
import { GrievancesTable } from './GrievancesTable/GrievancesTable';

export function GrievancesTablePage(): React.ReactElement {
  const businessArea = useBusinessArea();

  const [filter, setFilter] = useState({
    search: '',
    status: [],
    fsp: [],
    createdAtRange: '',
    admin: '',
  });
  const debouncedFilter = useDebounce(filter, 500);

  return (
    <>
      <PageHeader title='Grievance and Feedback'>
        <>
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${businessArea}/grievance-and-feedback/new-ticket`}
          >
            NEW TICKET
          </Button>
        </>
      </PageHeader>
      <GrievancesFilters filter={debouncedFilter} onFilterChange={setFilter} />
      <GrievancesTable filter={debouncedFilter} businessArea={businessArea} />
    </>
  );
}
