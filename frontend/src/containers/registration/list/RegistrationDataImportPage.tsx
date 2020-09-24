import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/PageHeader';
import { RegistrationDataImport } from '../import/RegistrationDataImport';
import { RegistrationDataImportTable } from '../tables/RegistrationdDataImportTable';
import { useDebounce } from '../../../hooks/useDebounce';
import { RegistrationFilters } from './RegistrationFilter';
import { useMeQuery } from '../../../__generated__/graphql';
import { usePermissions } from '../../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';


export function RegistrationDataImportPage(): React.ReactElement {
  const permissions = usePermissions();
  const { t } = useTranslation();
  const [filter, setFilter] = useState({});
  const debounceFilter = useDebounce(filter, 500);
  if (permissions === null) {
    return null;
  }
  if (!hasPermissions([PERMISSIONS.RDI_LIST, PERMISSIONS.READ], permissions)) {
    return <div>NO PERMISSIONS</div>;
  }
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
