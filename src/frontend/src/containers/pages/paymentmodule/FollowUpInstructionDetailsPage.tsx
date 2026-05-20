import withErrorBoundary from '@components/core/withErrorBoundary';
import { ChildPaymentPlansTable } from '@containers/pages/paymentmodule/FollowUpInstructions/ChildPaymentPlansTable';
import { FollowUpInstructionDetailsHeader } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionDetailsHeader';
import { FollowUpInstructionSummary } from '@containers/pages/paymentmodule/FollowUpInstructions/FollowUpInstructionSummary';
import { SomethingWentWrong } from '@containers/pages/somethingWentWrong/SomethingWentWrong';
import { LoadingComponent } from '@core/LoadingComponent';
import { PermissionDenied } from '@core/PermissionDenied';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { Box } from '@mui/material';
import { BackgroundActionStatusEnum } from '@restgenerated/models/BackgroundActionStatusEnum';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useParams } from 'react-router-dom';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';

const errorStatuses = [
  BackgroundActionStatusEnum.XLSX_EXPORT_ERROR,
  BackgroundActionStatusEnum.XLSX_IMPORT_ERROR,
];

const FollowUpInstructionDetailsPage = (): ReactElement => {
  const { instructionId } = useParams<{ instructionId: string }>();
  const permissions = usePermissions();
  const { businessArea, programId } = useBaseUrl();

  const {
    data: instruction,
    isLoading,
    error,
  } = useQuery<FollowUpInstructionDetail>({
    queryKey: ['followUpInstruction', businessArea, instructionId, programId],
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
        !errorStatuses.includes(
          data.backgroundActionStatus as BackgroundActionStatusEnum,
        )
      ) {
        return 3000;
      }
      return false;
    },
    refetchIntervalInBackground: true,
  });

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
    <Box display="flex" flexDirection="column">
      <FollowUpInstructionDetailsHeader
        instruction={instruction}
        permissions={permissions}
      />
      <FollowUpInstructionSummary instruction={instruction} />
      <ChildPaymentPlansTable paymentPlans={instruction.paymentPlans} />
    </Box>
  );
};

export default withErrorBoundary(
  FollowUpInstructionDetailsPage,
  'FollowUpInstructionDetailsPage',
);
