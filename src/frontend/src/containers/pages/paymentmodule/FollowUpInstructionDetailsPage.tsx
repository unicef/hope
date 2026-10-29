import withErrorBoundary from '@components/core/withErrorBoundary';
import AcceptanceProcess from '@components/paymentmodule/PaymentPlanDetails/AcceptanceProcess/AcceptanceProcess';
import { ConversionToUsd } from '@components/paymentmodule/PaymentPlanDetails/ConversionToUsd';
import { ExportInstructionSummaryPdfButton } from '@containers/pages/paymentmodule/FollowUpInstructions/actions/ExportInstructionSummaryPdfButton';
import { ChildPaymentPlansTable } from '@containers/pages/paymentmodule/FollowUpInstructions/ChildPaymentPlansTable';
import { FollowUpInstructionDetailsHeader } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionDetailsHeader';
import { FollowUpInstructionSummary } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionSummary';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';
import { LoadingComponent } from '@core/LoadingComponent';
import { PermissionDenied } from '@core/PermissionDenied';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { FollowUpInstructionBackgroundActionStatusEnum } from '@restgenerated/models/FollowUpInstructionBackgroundActionStatusEnum';
import type { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { restQueryKey } from '@utils/queryKeys';
import { isPermissionDeniedError } from '@utils/utils';
import { useEffect, useRef, type ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

const errorStatuses = [
  FollowUpInstructionBackgroundActionStatusEnum.RECALCULATING_ERROR,
  FollowUpInstructionBackgroundActionStatusEnum.XLSX_EXPORT_ERROR,
  FollowUpInstructionBackgroundActionStatusEnum.XLSX_IMPORT_ERROR,
];

const FollowUpInstructionDetailsPage = (): ReactElement => {
  const { instructionId } = useParams<{ instructionId: string }>();
  const permissions = usePermissions();
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const queryClient = useQueryClient();
  const wasRateRecalculating = useRef(false);

  const {
    data: instruction,
    isLoading,
    error,
  } = useQuery<FollowUpInstructionDetail>({
    queryKey: restQueryKey(
      RestService.restBusinessAreasProgramsFollowUpInstructionsRetrieve,
      {
        businessAreaSlug: businessArea,
        id: instructionId,
        programCode: programId,
      },
    ),
    queryFn: () =>
      RestService.restBusinessAreasProgramsFollowUpInstructionsRetrieve({
        businessAreaSlug: businessArea,
        id: instructionId,
        programCode: programId,
      }),
    enabled: !!instructionId && !!businessArea && !!programId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (
        data?.backgroundActionStatus &&
        !errorStatuses.includes(data.backgroundActionStatus)
      ) {
        return 3000;
      }
      return false;
    },
    refetchIntervalInBackground: true,
  });

  useEffect(() => {
    const rateRecalculating =
      instruction?.backgroundActionStatus ===
      FollowUpInstructionBackgroundActionStatusEnum.RECALCULATING;
    if (wasRateRecalculating.current && !rateRecalculating) {
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasProgramsPaymentPlansList,
        ),
      });
    }
    wasRateRecalculating.current = rateRecalculating;
  }, [instruction, queryClient]);

  if (isLoading) return <LoadingComponent />;
  if (permissions === null) return null;

  if (
    !hasPermissions(PERMISSIONS.PM_VIEW_DETAILS, permissions) ||
    isPermissionDeniedError(error)
  )
    return <PermissionDenied permission={PERMISSIONS.PM_VIEW_DETAILS} />;

  if (!instruction) {
    return (
      <SomethingWentWrong
        specificError={
          error?.message === 'Not Found'
            ? 'Follow-up Instruction has been removed or does not exist'
            : undefined
        }
        errorMessage={error?.message}
        goBackAddress={`/${baseUrl}/payment-module/follow-up-instructions`}
      />
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <FollowUpInstructionDetailsHeader
        instruction={instruction}
        permissions={permissions}
      />
      <FollowUpInstructionSummary instruction={instruction} />
      <ConversionToUsd
        owner={instruction}
        ownerType="instruction"
        permissions={permissions}
      />
      <AcceptanceProcess
        approvalProcess={instruction.approvalProcess}
        closure={
          instruction.status === 'CLOSED'
            ? {
                closedBy: instruction.closedBy,
                closedDate: instruction.updatedAt,
              }
            : null
        }
        headerAction={
          <ExportInstructionSummaryPdfButton instruction={instruction} />
        }
      />
      <ChildPaymentPlansTable paymentPlans={instruction.paymentPlans} />
    </Box>
  );
};

export default withErrorBoundary(
  FollowUpInstructionDetailsPage,
  'FollowUpInstructionDetailsPage',
);
