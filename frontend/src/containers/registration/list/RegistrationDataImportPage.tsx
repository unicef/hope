import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';
import { PageHeader } from '../../../components/PageHeader';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { RegistrationDataImport } from '../import/RegistrationDataImport';
import { RegistrationDataImportTable } from '../tables/RegistrationdDataImportTable';
import { RegistrationFilters } from './RegistrationFilter';
import { useDebounce } from '../../../hooks/useDebounce';

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
  const debounceFilter = useDebounce(filter, 500);
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
    // history.push(`${location.pathname}?${query}`);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounceFilter]);
  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      <RegistrationDataImport />
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <RegistrationFilters onFilterChange={setFilter} filter={filter} />
      <RegistrationDataImportTable filter={debounceFilter} />
    </div>
  );
}
