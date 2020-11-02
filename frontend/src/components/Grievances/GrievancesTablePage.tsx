import { Button, Typography } from '@material-ui/core';
import React from 'react';
import { Link } from 'react-router-dom';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { PageHeader } from '../PageHeader';
import { GrievancesTable } from './GrievancesTable/GrievancesTable';

export function GrievancesTablePage(): React.ReactElement {
  const businessArea = useBusinessArea();

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
      <GrievancesTable businessArea={businessArea} />
    </>
  );
}
