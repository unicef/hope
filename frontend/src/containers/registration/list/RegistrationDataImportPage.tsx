import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { PageHeader } from '../../../components/PageHeader';
import { RegistrationDataImport } from '../import/RegistrationDataImport';
import { RegistrationDataImportTable } from '../tables/RegistrationdDataImportTable';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/PermissionDenied';
import { RegistrationFilters } from './RegistrationFilter';

export function RegistrationDataImportPage(): React.ReactElement {
  const permissions = usePermissions();
  const { t } = useTranslation();
  const [filter, setFilter] = useState({});
  const debounceFilter = useDebounce(filter, 500);
  if (permissions === null) {
    return null;
  }
  if (!hasPermissions([PERMISSIONS.RDI_LIST, PERMISSIONS.READ], permissions)) {
    return <PermissionDenied />;
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
