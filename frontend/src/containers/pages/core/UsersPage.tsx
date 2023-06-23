import { Button } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { UsersListFilters } from '../../../components/core/UsersListFilters';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { UsersTable } from '../../tables/UsersTable';

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
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
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
      <UsersListFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={setAppliedFilter}
      />
      <UsersTable filter={appliedFilter} />
    </>
  );
};
