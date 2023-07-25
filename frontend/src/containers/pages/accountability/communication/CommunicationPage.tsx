import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { useGrievancesChoiceDataQuery } from '../../../../__generated__/graphql';
import { CommunicationFilters } from '../../../../components/accountability/Communication/CommunicationTable/CommunicationFilters';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PageHeader } from '../../../../components/core/PageHeader';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import {
  PERMISSIONS,
  hasPermissionInModule,
} from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../../utils/utils';
import { CommunicationTable } from '../../../tables/Communication/CommunicationTable';

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
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
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
      <CommunicationFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <CommunicationTable
        filter={appliedFilter}
        canViewDetails={hasPermissionInModule(
          PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
          permissions,
        )}
      />
    </>
  );
};
