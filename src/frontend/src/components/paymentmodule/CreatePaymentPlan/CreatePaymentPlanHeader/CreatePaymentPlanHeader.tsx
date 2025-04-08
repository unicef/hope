import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { LoadingButton } from '@core/LoadingButton';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { Box, Button } from '@mui/material';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { decodeIdString } from '@utils/utils';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';

interface CreatePaymentPlanHeaderProps {
  handleSubmit: () => Promise<void>;
  permissions: string[];
  loadingCreate: boolean;
}

export function CreatePaymentPlanHeader({
  handleSubmit,
  permissions,
  loadingCreate,
}: CreatePaymentPlanHeaderProps): ReactElement {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { programCycleId } = useParams();

  const decodedProgramCycleId = decodeIdString(programCycleId);

  const { data: programCycleData, isLoading: isLoadingProgramCycle } =
    useQuery<ProgramCycleList>({
      queryKey: [
        'programCyclesDetails',
        businessArea,
        decodedProgramCycleId,
        programId,
      ],
      queryFn: () => {
        return RestService.restBusinessAreasProgramsCyclesRetrieve({
          businessAreaSlug: businessArea,
          id: decodedProgramCycleId,
          programSlug: programId,
        });
      },
    });

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
          <Button component={Link} to={'../..'}>
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
