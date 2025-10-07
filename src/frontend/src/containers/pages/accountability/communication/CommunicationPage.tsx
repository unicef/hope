import { CommunicationFilters } from '@components/accountability/Communication/CommunicationTable/CommunicationFilters';
import { ButtonTooltip } from '@components/core/ButtonTooltip';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import CommunicationTable from '@containers/tables/Communication/CommunicationTable/CommunicationTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
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
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  if (permissions === null) return null;
  if (
    !hasPermissionInModule(
      PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
      permissions,
    )
  )
    return <PermissionDenied />;

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
        setAppliedFilter={(f) => {
          setAppliedFilter(f);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <CommunicationTable
          filter={appliedFilter}
          canViewDetails={hasPermissionInModule(
            PERMISSIONS.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST,
            permissions,
          )}
        />
      </div>
    </>
  );
};

export default withErrorBoundary(CommunicationPage, 'CommunicationPage');
