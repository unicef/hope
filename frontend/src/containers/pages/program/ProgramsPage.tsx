import { Button } from '@mui/material';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { useProgrammeChoiceDataQuery } from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { ProgrammesTable } from '../../tables/ProgrammesTable';
import { ProgrammesFilters } from '../../tables/ProgrammesTable/ProgrammesFilter';

const initialFilter = {
  search: '',
  startDate: '',
  endDate: '',
  status: '',
  sector: [],
  numberOfHouseholdsMin: '',
  numberOfHouseholdsMax: '',
  budgetMin: '',
  budgetMax: '',
  dataCollectingType: '',
};

export const ProgramsPage = (): React.ReactElement => {
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();

  const { data: choicesData } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  if (permissions === null || !choicesData) return null;
  if (
    !hasPermissions(
      [
        PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS,
        PERMISSIONS.PROGRAMME_MANAGEMENT_VIEW,
      ],
      permissions,
    )
  )
    return <PermissionDenied />;

  const toolbar = (
    <PageHeader title={t('Programme Management')}>
      <Button
        variant="contained"
        color="primary"
        component={Link}
        to={`/${baseUrl}/create`}
        data-cy="button-new-program"
      >
        {t('Create Programme')}
      </Button>
    </PageHeader>
  );

  return (
    <div>
      {hasPermissions(PERMISSIONS.PROGRAMME_CREATE, permissions) && toolbar}
      <ProgrammesFilters
        filter={filter}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <ProgrammesTable
        businessArea={businessArea}
        choicesData={choicesData}
        filter={appliedFilter}
      />
    </div>
  );
};
