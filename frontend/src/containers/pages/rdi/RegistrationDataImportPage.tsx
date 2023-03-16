import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { PageHeader } from '../../../components/core/PageHeader';
import { RegistrationDataImportCreateDialog } from '../../../components/rdi/create/RegistrationDataImportCreateDialog';
import { RegistrationDataImportTable } from '../../tables/rdi/RegistrationDataImportTable';
import { useDebounce } from '../../../hooks/useDebounce';
import { usePermissions } from '../../../hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { RegistrationFilters } from '../../../components/rdi/RegistrationFilters';
import { getFilterFromQueryParams } from '../../../utils/utils';

const initialFilter = {
  search: '',
  importDate: null,
  importedBy: '',
  status: '',
};

export const RegistrationDataImportPage = (): React.ReactElement => {
  const location = useLocation();
  const permissions = usePermissions();
  const { t } = useTranslation();

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const debounceFilter = useDebounce(filter, 500);
  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      {hasPermissions(PERMISSIONS.RDI_IMPORT_DATA, permissions) && (
        <RegistrationDataImportCreateDialog />
      )}
    </PageHeader>
  );
  return (
    <div>
      {toolbar}
      <RegistrationFilters onFilterChange={setFilter} filter={filter} />
      <RegistrationDataImportTable
        filter={debounceFilter}
        canViewDetails={hasPermissions(
          PERMISSIONS.RDI_VIEW_DETAILS,
          permissions,
        )}
      />
    </div>
  );
};
