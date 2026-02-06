import { runDeduplicationDataImports } from '@api/rdiApi';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { RegistrationDataImportCreateDialog } from '@components/rdi/create/RegistrationDataImportCreateDialog';
import RegistrationFilters from '@components/rdi/RegistrationFilters';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQuery } from '@tanstack/react-query';
import { getFilterFromQueryParams, showApiErrorMessages } from '@utils/utils';
import { ReactElement, useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { RegistrationDataImportTable } from '../../tables/rdi/RegistrationDataImportTable';
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

function RegistrationDataImportPage(): ReactElement {
  const location = useLocation();
  const permissions = usePermissions();
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const { data: deduplicationFlags, isLoading: loading } = useQuery({
    queryKey: ['deduplicationFlags', businessArea, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsDeduplicationFlagsRetrieve({
        businessAreaSlug: businessArea,
        slug: programId,
      }),
  });
  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: ['businessArea', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({
        slug: businessArea,
      }),
  });

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

  const { mutateAsync } = useMutation({
    mutationFn: async () =>
      runDeduplicationDataImports(businessArea, programId),
    onSuccess: () => {
      showMessage('Deduplication process started');
    },
  });

  const runDeduplication = async () => {
    try {
      await mutateAsync();
    } catch (error) {
      showApiErrorMessages(error, showMessage);
    }
  };

  if (permissions === null || loading) return null;

  if (!hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions))
    return <PermissionDenied permission={PERMISSIONS.RDI_VIEW_LIST} />;

  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      <Box display="flex" alignItems="center">
        {deduplicationFlags?.canRunDeduplication && (
          <Box mr={3}>
            <ButtonTooltip
              variant="contained"
              color="primary"
              onClick={runDeduplication}
              disabled={deduplicationFlags?.isDeduplicationDisabled}
              title={t('Deduplication engine already in progress')}
            >
              {t('START DEDUPLICATION ENGINE')}
            </ButtonTooltip>
          </Box>
        )}
        {hasPermissions(PERMISSIONS.RDI_IMPORT_DATA, permissions) && (
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
      <RegistrationFilters
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
  RegistrationDataImportPage,
  'RegistrationDataImportPage',
);
