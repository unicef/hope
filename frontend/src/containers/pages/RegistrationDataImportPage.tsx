import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { Snackbar, SnackbarContent } from '@material-ui/core';
import { ProgramCard } from '../../components/programs/ProgramCard';
import { PageHeader } from '../../components/PageHeader';
import {
  ProgramNode,
  useAllProgramsQuery,
  useProgrammeChoiceDataQuery,
} from '../../__generated__/graphql';
import { CreateProgram } from '../dialogs/programs/CreateProgram';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../../components/LoadingComponent';
import { useSnackbarHelper } from '../../hooks/useBreadcrumbHelper';
import { RegistrationDataImport } from '../dialogs/registration/RegistrationDataImport';
import { RegistrationDataImportTable } from '../tables/RegistrationdDataImportTable';
import { RegistrationFilters } from '../../components/registration/RegistrationFilter';
import { useDebounce } from '../../hooks/useDebounce';

const PageContainer = styled.div`
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  margin-top: 20px;
  justify-content: center;
`;
export function RegistrationDataImportPage(): React.ReactElement {
  const businessArea = useBusinessArea();
  const { t } = useTranslation();
  const [filter, setFilter] = useState({});
  const debounceFilter = useDebounce(filter,500);
  const location = useLocation();
  const history = useHistory();

  useEffect(() => {
    const query = new URLSearchParams(location.search);
    const filterQuery = {};
    query.forEach((value, name) => {
      filterQuery[name] = value;
    });
    setFilter(filterQuery);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  useEffect(() => {
    if (Object.keys(filter).length === 0) {
      return;
    }
    const encoded = Object.keys(filter).map(
      (key) => `${encodeURIComponent(key)}=${encodeURIComponent(filter[key])}`,
    );
    const query = encoded.join('&');
    history.push(`${location.pathname}?${query}`);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounceFilter]);
  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      <RegistrationDataImport />
    </PageHeader>
  );
  // if (loading || choicesLoading) {
  //   return <LoadingComponent />;
  // }
  // if (!data || !data.allPrograms || !choices) {
  //   return <div>{toolbar}</div>;
  // }
  return (
    <div>
      {toolbar}
      <RegistrationFilters onFilterChange={setFilter} filter={filter} />
      <RegistrationDataImportTable filter={debounceFilter} />
    </div>
  );
}
