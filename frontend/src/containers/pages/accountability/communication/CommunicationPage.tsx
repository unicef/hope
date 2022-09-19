import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { hasPermissionInModule } from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { useDebounce } from '../../../../hooks/useDebounce';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useGrievancesChoiceDataQuery } from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { CommunicationFilters } from '../../../../components/accountability/Communication/CommunicationTable/CommunicationFilters';
import { GrievancesTable } from '../../../../components/grievances/GrievancesTable/GrievancesTable';

export function CommunicationPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { t } = useTranslation();

  const [filter, setFilter] = useState({
    createdAtRange: '',
    program: '',
    targetPopulation: '',

    search: '',
    status: '',
    fsp: '',
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
      <PageHeader title={t('Communication')}>
        <Button
          variant='contained'
          color='primary'
          component={Link}
          to={`/${businessArea}/target-population/create`}
          data-cy='button-target-population-create-new'
        >
          {t('new message')}
        </Button>
      </PageHeader>
      <CommunicationFilters filter={filter} onFilterChange={setFilter} />
      <GrievancesTable
        filter={debouncedFilter}
        businessArea={businessArea}
        selectedTab={undefined}
      />
    </>
  );
}
