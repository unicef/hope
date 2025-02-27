import { runDeduplicationDataImports } from '@api/rdiApi';
import { PageHeader } from '@components/core/PageHeader';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { RegistrationDataImportCreateDialog } from '@components/rdi/create/RegistrationDataImportCreateDialog';
import { ButtonTooltip } from '@core/ButtonTooltip';
import { useDeduplicationFlagsQuery } from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import { Box } from '@mui/material';
import { useMutation } from '@tanstack/react-query';
import { getFilterFromQueryParams } from '@utils/utils';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { RegistrationDataImportTable } from '../../tables/rdi/RegistrationDataImportTable';
import RegistrationFilters from '@components/rdi/RegistrationFilters';

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
  const { data: deduplicationFlags, loading } = useDeduplicationFlagsQuery({
    fetchPolicy: 'cache-and-network',
  });

  const [filter, setFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );
  const [appliedFilter, setAppliedFilter] = useState(
    getFilterFromQueryParams(location, initialFilter),
  );

  const { mutateAsync } = useMutation({
    mutationFn: async () =>
      runDeduplicationDataImports(businessArea, programId),
    onSuccess: ({ data }) => {
      showMessage(data.message);
    },
  });

  const runDeduplication = async () => {
    try {
      await mutateAsync();
    } catch (error) {
      showMessage(error.message);
    }
  };

  if (permissions === null || loading) return null;

  if (!hasPermissions(PERMISSIONS.RDI_VIEW_LIST, permissions))
    return <PermissionDenied />;

  const toolbar = (
    <PageHeader title={t('Registration Data Import')}>
      <Box display="flex" alignItems="center">
        {deduplicationFlags.canRunDeduplication && (
          <Box mr={3}>
            <ButtonTooltip
              variant="contained"
              color="primary"
              onClick={runDeduplication}
              disabled={deduplicationFlags.isDeduplicationDisabled}
              title={t('Deduplication engine already in progress')}
            >
              {t('START DEDUPLICATION ENGINE')}
            </ButtonTooltip>
          </Box>
        )}
        {hasPermissions(PERMISSIONS.RDI_IMPORT_DATA, permissions) && (
          <Box>
            <RegistrationDataImportCreateDialog />
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
        setAppliedFilter={setAppliedFilter}
      />
      <RegistrationDataImportTable
        filter={appliedFilter}
        canViewDetails={hasPermissions(
          PERMISSIONS.RDI_VIEW_DETAILS,
          permissions,
        )}
      />
    </>
  );
}
export default withErrorBoundary(
  RegistrationDataImportPage,
  'RegistrationDataImportPage',
);
