import { CommunicationFilters } from '@components/accountability/Communication/CommunicationTable/CommunicationFilters';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import CommunicationTable from '@containers/tables/Communication/CommunicationTable/CommunicationTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { useProgramContext } from '../../../../programContext';

export const CommunicationPage = (): ReactElement => {
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
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  if (permissions === null) return null;
  if (
    !hasPermissions(
      PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
      permissions,
    )
  )
    return (
      <PermissionDenied
        permission={PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST}
      />
    );

  return (
    <>
      <PageHeader title={t('Communication')}>
        <ButtonTooltip
          variant="contained"
          color="primary"
          component={Link}
          to={`/${baseUrl}/accountability/communication/create`}
          data-cy="button-communication-create-new"
          dataPerm={`${PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST}, ${PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_LIST}, ${PERMISSIONS.TARGETING_VIEW_LIST}, ${PERMISSIONS.RDI_VIEW_LIST}`}
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
        setAppliedFilter={(f) => {
          setAppliedFilter(f);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <CommunicationTable
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
            permissions,
          )}
        />
      </div>
    </>
  );
};

export default withErrorBoundary(CommunicationPage, 'CommunicationPage');
