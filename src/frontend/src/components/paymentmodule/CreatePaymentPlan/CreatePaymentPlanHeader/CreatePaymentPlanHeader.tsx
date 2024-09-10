import { Box, Button } from '@mui/material';
import { Link, useParams } from 'react-router-dom';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { PageHeader } from '@core/PageHeader';
import { LoadingButton } from '@core/LoadingButton';
import { decodeIdString } from '@utils/utils';
import { useQuery } from '@tanstack/react-query';
import { fetchProgramCycle } from '@api/programCycleApi';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface CreatePaymentPlanHeaderProps {
  handleSubmit: () => Promise<void>;
  permissions: string[];
  loadingCreate: boolean;
}

export function CreatePaymentPlanHeader({
  handleSubmit,
  permissions,
  loadingCreate,
}: CreatePaymentPlanHeaderProps): React.ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { programCycleId } = useParams();

  const decodedProgramCycleId = decodeIdString(programCycleId);

  const { data: programCycleData, isLoading: isLoadingProgramCycle } = useQuery(
    {
      queryKey: [
        'programCyclesDetails',
        businessArea,
        programId,
        decodedProgramCycleId,
      ],
      queryFn: async () => {
        return fetchProgramCycle(
          businessArea,
          programId,
          decodedProgramCycleId,
        );
      },
    },
  );

  if (isLoadingProgramCycle) {
    return null;
  }

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Payment Module'),
      to: '../../..',
    },
    {
      title: `${programCycleData.title}`,
      to: '../..',
    },
  ];

  return (
    <PageHeader
      title={t('New Payment Plan')}
      breadCrumbs={
        hasPermissions(PERMISSIONS.PM_VIEW_LIST, permissions)
          ? breadCrumbsItems
          : null
      }
    >
      <Box display="flex" mt={2} mb={2}>
        <Box mr={3}>
          <Button component={Link} to={'..'}>
            {t('Cancel')}
          </Button>
        </Box>
        <LoadingButton
          loading={loadingCreate}
          variant="contained"
          color="primary"
          onClick={handleSubmit}
          data-cy="button-save-payment-plan"
        >
          {t('Save')}
        </LoadingButton>
      </Box>
    </PageHeader>
  );
}
