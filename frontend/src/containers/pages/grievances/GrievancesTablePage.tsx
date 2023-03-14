import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useParams } from 'react-router-dom';
import {
  hasPermissionInModule,
  hasPermissions,
  PERMISSIONS,
} from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { useGrievancesChoiceDataQuery } from '../../../__generated__/graphql';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { GrievancesFilters } from '../../../components/grievances/GrievancesTable/GrievancesFilters';
import { GrievancesTable } from '../../../components/grievances/GrievancesTable/GrievancesTable';
import { getFilterFromQueryParams } from '../../../utils/utils';

export const GrievancesTablePage = (): React.ReactElement => {
  const { t } = useTranslation();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { id, cashPlanId } = useParams();
  const location = useLocation();

  const initialFilter = {
    search: '',
    status: '',
    fsp: '',
    createdAtRangeMin: undefined,
    createdAtRangeMax: undefined,
    category: '',
    issueType: '',
    assignedTo: '',
    admin: null,
    registrationDataImport: id,
    cashPlan: cashPlanId,
    scoreMin: '',
    scoreMax: '',
    preferredLanguage: '',
  };
  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
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
            {t('NEW TICKET')}
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
};
