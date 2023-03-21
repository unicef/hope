import { Paper } from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { LoadingComponent } from '../../../components/core/LoadingComponent';
import { PageHeader } from '../../../components/core/PageHeader';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { getFilterFromQueryParams } from '../../../utils/utils';
import { useProgrammeChoiceDataQuery } from '../../../__generated__/graphql';
import { CreateProgram } from '../../dialogs/programs/CreateProgram';
import { ProgrammesTable } from '../../tables/ProgrammesTable';
import { ProgrammesFilters } from '../../tables/ProgrammesTable/ProgrammesFilter';

const Container = styled(Paper)`
  display: flex;
  flex: 1;
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(8)}px
    ${({ theme }) => theme.spacing(11)}px;
  flex-direction: row;
  align-items: center;
  && > div {
    margin: 5px;
  }
`;

const initialFilter = {
  search: '',
  startDate: undefined,
  endDate: undefined,
  status: '',
  sector: [],
  numberOfHouseholdsMin: '',
  numberOfHouseholdsMax: '',
  budgetMin: '',
  budgetMax: '',
};

export const ProgramsPage = (): React.ReactElement => {
  const location = useLocation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const debouncedFilter = useDebounce(filter, 500);
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useProgrammeChoiceDataQuery();
  const { t } = useTranslation();

  if (choicesLoading) return <LoadingComponent />;

  if (permissions === null || !choicesData) return null;

  if (
    !hasPermissions(PERMISSIONS.PRORGRAMME_VIEW_LIST_AND_DETAILS, permissions)
  )
    return <PermissionDenied />;

  const toolbar = (
    <PageHeader title={t('Programme Management')}>
      <CreateProgram />
    </PageHeader>
  );

  return (
    <div>
      {hasPermissions(PERMISSIONS.PROGRAMME_CREATE, permissions) && toolbar}
      <Container>
        <ProgrammesFilters
          filter={filter}
          onFilterChange={setFilter}
          choicesData={choicesData}
        />
      </Container>
      <ProgrammesTable
        businessArea={businessArea}
        choicesData={choicesData}
        filter={debouncedFilter}
      />
    </div>
  );
};
