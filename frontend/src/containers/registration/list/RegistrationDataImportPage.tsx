import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/PageHeader';
import { RegistrationDataImport } from '../import/RegistrationDataImport';
import { RegistrationDataImportTable } from '../tables/RegistrationdDataImportTable';
import { useDebounce } from '../../../hooks/useDebounce';
import { RegistrationFilters } from './RegistrationFilter';

export function RegistrationDataImportPage(): React.ReactElement {
  const { t } = useTranslation();
  const [filter, setFilter] = useState({});
  const debounceFilter = useDebounce(filter, 500);
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
