import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@material-ui/core';
import { useDebounce } from '../../../hooks/useDebounce';
import { PageHeader } from '../../../components/core/PageHeader';
import { UsersTable } from '../../tables/UsersTable';
import { UsersListFilters } from '../../../components/core/UsersListFilters';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { getFilterFromQueryParams } from '../../../utils/utils';

const initialFilter = {
  search: '',
  partner: '',
  roles: '',
  status: '',
};

export const UsersPage = (): React.ReactElement => {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { t } = useTranslation();
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const debouncedFilter = useDebounce(filter, 500);

  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.USER_MANAGEMENT_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <>
      <PageHeader title={t('User Management')}>
        <>
          <Button
            variant='contained'
            color='primary'
            onClick={() => null}
            component='a'
            href={`/api/download-exported-users/${businessArea}`}
            data-cy='button-target-population-create-new'
          >
            Export
          </Button>
        </>
      </PageHeader>
      <UsersListFilters filter={filter} onFilterChange={setFilter} />
      <UsersTable filter={debouncedFilter} />
    </>
  );
};
