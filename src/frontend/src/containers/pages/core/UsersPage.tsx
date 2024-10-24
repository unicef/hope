import { Button } from '@mui/material';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { UsersListFilters } from '@components/core/UsersListFilters';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { getFilterFromQueryParams } from '@utils/utils';
import { UsersTable } from '../../tables/UsersTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';

const initialFilter = {
  search: '',
  partner: '',
  roles: '',
  status: '',
};

export function UsersPage(): ReactElement {
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const { t } = useTranslation();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.USER_MANAGEMENT_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <UniversalErrorBoundary
      location={location}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname);
        scope.setTag('component', 'UsersPage.tsx');
      }}
      componentName="UsersPage"
    >
      <PageHeader title={t('Programme Users')}>
        <>
          <Button
            variant="contained"
            color="primary"
            onClick={() => null}
            component="a"
            href={`/api/download-exported-users/${businessArea}`}
            data-cy="button-target-population-create-new"
          >
            Export
          </Button>
        </>
      </PageHeader>
      <UsersListFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <UsersTable filter={appliedFilter} />
    </UniversalErrorBoundary>
  );
}
