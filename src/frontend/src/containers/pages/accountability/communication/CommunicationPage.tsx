import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { useGrievancesChoiceDataQuery } from '@generated/graphql';
import { CommunicationFilters } from '@components/accountability/Communication/CommunicationTable/CommunicationFilters';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import {
  PERMISSIONS,
  hasPermissionInModule,
} from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { CommunicationTable } from '../../../tables/Communication/CommunicationTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { useProgramContext } from '../../../../programContext';

export function CommunicationPage(): React.ReactElement {
  const { baseUrl } = useBaseUrl();
  const permissions = usePermissions();
  const location = useLocation();
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();

  const initialFilter = {
    createdBy: '',
    createdAtRangeMin: null,
    createdAtRangeMax: null,
    targetPopulation: '',
  };

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const { data: choicesData, loading: choicesLoading } =
    useGrievancesChoiceDataQuery();

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
        <ButtonTooltip
          variant="contained"
          color="primary"
          component={Link}
          to={`/${baseUrl}/accountability/communication/create`}
          data-cy="button-communication-create-new"
          title={t('Programme has to be active to create new Message')}
          disabled={!isActiveProgram}
        >
          {t('New message')}
        </ButtonTooltip>
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
}
