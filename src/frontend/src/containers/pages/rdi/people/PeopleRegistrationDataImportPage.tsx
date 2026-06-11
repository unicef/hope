import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { RegistrationDataImportCreateDialog } from '@components/rdi/create/RegistrationDataImportCreateDialog';
import RegistrationPeopleFilters from '@components/rdi/RegistrationPeopleFilters';
import RegistrationDataImportTable from '@containers/tables/rdi/RegistrationDataImportTable/RegistrationDataImportTable';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useScrollToRefOnChange } from '@hooks/useScrollToRefOnChange';
import { BusinessArea } from '@restgenerated/models/BusinessArea';

const initialFilter = {
  search: '',
  importedBy: '',
  status: '',
  sizeMin: '',
  sizeMax: '',
  importDateRangeMin: '',
  importDateRangeMax: '',
};

function PeopleRegistrationDataImportPage(): ReactElement {
  const location = useLocation();
  const permissions = usePermissions();
  const { t } = useTranslation();
  const { businessAreaSlug } = useBaseUrl();
  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: ['businessArea', businessAreaSlug],
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({
        slug: businessAreaSlug,
      }),
  });
  const isManualIngest = businessAreaData?.isManualIngest;

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [shouldScroll, setShouldScroll] = useState(false);
  const tableRef = useRef<HTMLDivElement>(null);
  useScrollToRefOnChange(tableRef, shouldScroll, appliedFilter, () =>
    setShouldScroll(false),
  );

  if (permissions === null) return null;

  if (!hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions))
    return <PermissionDenied permission={PERMISSIONS.RDI_VIEW_LIST} />;

  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      <Box display="flex" alignItems="center">
        {isManualIngest &&
          hasPermissions(PERMISSIONS.RDI_IMPORT_DATA, permissions) && (
            <Box>
              <RegistrationDataImportCreateDialog
                rdiImportXlsxDisabled={businessAreaData?.rdiImportXlsxDisabled}
              />
            </Box>
          )}
      </Box>
    </PageHeader>
  );
  return (
    <>
      {toolbar}
      <RegistrationPeopleFilters
        filter={filter}
        setFilter={setFilter}
        initialFilter={initialFilter}
        appliedFilter={appliedFilter}
        setAppliedFilter={(newFilter) => {
          setAppliedFilter(newFilter);
          setShouldScroll(true);
        }}
      />
      <Box ref={tableRef}>
        <RegistrationDataImportTable
          filter={appliedFilter}
          canViewDetails={hasPermissions(
            PERMISSIONS.RDI_VIEW_DETAILS,
            permissions,
          )}
        />
      </Box>
    </>
  );
}
export default withErrorBoundary(
  PeopleRegistrationDataImportPage,
  'PeopleRegistrationDataImportPage',
);
