import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Button } from '@mui/material';
import { ProgramChoices } from '@restgenerated/models/ProgramChoices';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { ProgrammesTable } from '../../tables/ProgrammesTable';
import ProgrammesFilter from '@containers/tables/ProgrammesTable/ProgrammesFilter';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';

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

function ProgramsPage(): ReactElement {
  const location = useLocation();

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
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();

  const { data: choicesData } = useQuery<ProgramChoices>({
    queryKey: ['programChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasProgramsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
    staleTime: 1000 * 60 * 10,
    gcTime: 1000 * 60 * 30,
  });
  const { t } = useTranslation();

  if (!permissions || !choicesData) return null;
  if (
    !hasPermissions(
      [
        PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS,
        PERMISSIONS.PROGRAMME_MANAGEMENT_VIEW,
      ],
      permissions,
    )
  )
    return (
      <PermissionDenied
        permission={[
          PERMISSIONS.PROGRAMME_VIEW_LIST_AND_DETAILS,
          PERMISSIONS.PROGRAMME_MANAGEMENT_VIEW,
        ]}
      />
    );

  const toolbar = (
    <PageHeader title={t('Programme Management')}>
      <Button
        variant="contained"
        color="primary"
        component={Link}
        to={`/${baseUrl}/create`}
        data-cy="button-new-program"
        data-perm={PERMISSIONS.PROGRAMME_CREATE}
      >
        {t('Create Programme')}
      </Button>
    </PageHeader>
  );

  return (
    <>
      {hasPermissions(PERMISSIONS.PROGRAMME_CREATE, permissions) && toolbar}
      <ProgrammesFilter
        filter={filter}
        choicesData={choicesData}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(newFilter) => {
          setAppliedFilter(newFilter);
          setShouldScroll(true);
        }}
      />
      <div ref={tableRef}>
        <ProgrammesTable
          businessArea={businessArea}
          choicesData={choicesData}
          filter={appliedFilter}
        />
      </div>
    </>
  );
}
export default withErrorBoundary(ProgramsPage, 'ProgramsPage');
