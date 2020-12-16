import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button } from '@material-ui/core';
import { useDebounce } from '../../hooks/useDebounce';
import { PageHeader } from '../../components/PageHeader';
import { UsersListTable } from '../tables/UsersListTable';
import { UsersListFilters } from '../../components/UserManagement/UsersListFilters';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { usePermissions } from '../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PermissionDenied } from '../../components/PermissionDenied';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

export function UsersList(): React.ReactElement {
  const businessArea = useBusinessArea();
  const permissions = usePermissions();
  const { t } = useTranslation();
  const [filter, setFilter] = useState({
    search: '',
    partner: '',
    roles: '',
    status: '',
  });
  const debouncedFilter = useDebounce(filter, 500);

  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.USER_MANAGEMENT_VIEW_LIST, permissions))
    return <PermissionDenied />;

  return (
    <div>
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
      <Container>
        <UsersListTable filter={debouncedFilter} />
      </Container>
    </div>
  );
}
