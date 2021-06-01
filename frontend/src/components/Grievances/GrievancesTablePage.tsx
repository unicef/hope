import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import {
  hasPermissionInModule,
  hasPermissions,
  PERMISSIONS,
} from '../../config/permissions';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useDebounce } from '../../hooks/useDebounce';
import { usePermissions } from '../../hooks/usePermissions';
import { useGrievancesChoiceDataQuery } from '../../__generated__/graphql';
import { LoadingComponent } from '../LoadingComponent';
import { PageHeader } from '../PageHeader';
import { PermissionDenied } from '../PermissionDenied';
import { GrievancesFilters } from './GrievancesTable/GrievancesFilters';
import { GrievancesTable } from './GrievancesTable/GrievancesTable';

export function GrievancesTablePage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const { id } = useParams();
  const [filter, setFilter] = useState({
    search: '',
    status: '',
    fsp: '',
    createdAtRange: '',
    admin: null,
    registrationDataImport: id,
  });
  const debouncedFilter = useDebounce(filter, 500);
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  if (choicesLoading) return <LoadingComponent />;
  if (permissions === null) return null;
  if (!hasPermissionInModule('GRIEVANCES_VIEW_LIST', permissions))
    return <PermissionDenied />;
  if (!choicesData) return null;

  return (
    <>
      <PageHeader title='Grievance and Feedback'>
        {hasPermissions(PERMISSIONS.GRIEVANCES_CREATE, permissions) && (
          <Button
            variant='contained'
            color='primary'
            component={Link}
            to={`/${businessArea}/grievance-and-feedback/new-ticket`}
          >
            NEW TICKET
          </Button>
        )}
      </PageHeader>
      <GrievancesFilters
        choicesData={choicesData}
        filter={filter}
        onFilterChange={setFilter}
      />
      <GrievancesTable filter={debouncedFilter} businessArea={businessArea} />
    </>
  );
}
