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
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { ProgrammesTable } from '../../tables/ProgrammesTable';
import ProgrammesFilter from '@containers/tables/ProgrammesTable/ProgrammesFilter';

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
  const { baseUrl, businessArea } = useBaseUrl();
  const permissions = usePermissions();

  const { data: choicesData } = useQuery<ProgramChoices>({
    queryKey: ['programChoices', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasProgramsChoicesRetrieve({
        businessAreaSlug: businessArea,
      }),
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
    <>
      {hasPermissions(PERMISSIONS.PROGRAMME_CREATE, permissions) && toolbar}
      <ProgrammesFilter
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
    </>
  );
}
export default withErrorBoundary(ProgramsPage, 'ProgramsPage');
