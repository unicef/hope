import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Button } from '@material-ui/core';
import { useDebounce } from '../../hooks/useDebounce';
import { PageHeader } from '../../components/PageHeader';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { UsersListTable } from '../tables/UsersListTable';
import { UsersListFilters } from '../../components/UserManagement/UsersListFilters';

const Container = styled.div`
  && {
    display: flex;
    flex-direction: column;
    min-width: 100%;
  }
`;

export function UsersList(): React.ReactElement {
  const { t } = useTranslation();
  const [filter, setFilter] = useState({
    fullName: '',
  });
  const debouncedFilter = useDebounce(filter, 500);

  return (
    <div>
      <PageHeader title={t('User Management')}>
        <>
          <Button
            variant='contained'
            color='primary'
            onClick={() => console.log('SEND TO CASHASSIST')}
            data-cy='button-target-population-create-new'
          >
            Send to CashAssist
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
