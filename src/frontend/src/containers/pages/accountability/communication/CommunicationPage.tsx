import { CommunicationFilters } from '@components/accountability/Communication/CommunicationTable/CommunicationFilters';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import CommunicationTable from '@containers/tables/Communication/CommunicationTable/CommunicationTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { GrievanceChoices } from '@restgenerated/models/GrievanceChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import {
  PERMISSIONS,
  hasPermissionInModule,
} from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';

export const CommunicationPage = (): ReactElement => {
  const { baseUrl, businessArea } = useBaseUrl();
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

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<GrievanceChoices>({
      queryKey: ['businessAreasGrievanceTicketsChoices', businessArea],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
          businessAreaSlug: businessArea,
        }),
    });

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
};

export default withErrorBoundary(CommunicationPage, 'CommunicationPage');
