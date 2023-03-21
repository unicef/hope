import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  hasPermissionInModule,
  PERMISSIONS,
} from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { useDebounce } from '../../../../hooks/useDebounce';
import { usePermissions } from '../../../../hooks/usePermissions';
import { useGrievancesChoiceDataQuery } from '../../../../__generated__/graphql';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { CommunicationFilters } from '../../../../components/accountability/Communication/CommunicationTable/CommunicationFilters';
import { CommunicationTable } from '../../../tables/Communication/CommunicationTable';
import { getFilterFromQueryParams } from '../../../../utils/utils';

const initialFilter = {
  createdBy: '',
  createdAtRangeMin: null,
  createdAtRangeMax: null,
  program: '',
  targetPopulation: '',
};

export const CommunicationPage = (): React.ReactElement => {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const location = useLocation();
  const { t } = useTranslation();

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
  if (
    !hasPermissionInModule(
      PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
      permissions,
    )
  )
    return <PermissionDenied />;
  if (!choicesData) return null;

  return (
    <>
      <PageHeader title={t('Communication')}>
        <Button
          variant='contained'
          color='primary'
          component={Link}
          to={`/${businessArea}/accountability/communication/create`}
          data-cy='button-communication-create-new'
        >
          {t('New message')}
        </Button>
      </PageHeader>
      <CommunicationFilters filter={filter} onFilterChange={setFilter} />
      <CommunicationTable
        filter={debouncedFilter}
        canViewDetails={hasPermissionInModule(
          PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
          permissions,
        )}
      />
    </>
  );
};
