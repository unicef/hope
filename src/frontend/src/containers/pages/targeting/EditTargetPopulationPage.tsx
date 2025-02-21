import { ReactElement, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  PaymentPlanBuildStatus,
  useBusinessAreaDataQuery,
  usePaymentPlanQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import EditTargetPopulation from '@components/targeting/EditTargetPopulation/EditTargetPopulation';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import withErrorBoundary from '@components/core/withErrorBoundary';

const EditTargetPopulationPage = (): ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();

  const { data, loading, error, startPolling, stopPolling } =
    usePaymentPlanQuery({
      variables: { id },
      fetchPolicy: 'cache-and-network',
    });
  const { businessArea } = useBaseUrl();

  const { data: businessAreaData } = useBusinessAreaDataQuery({
    variables: { businessAreaSlug: businessArea },
  });
  const buildStatus = data?.paymentPlan?.buildStatus;
  useEffect(() => {
    if (
      [
        PaymentPlanBuildStatus.Building,
        PaymentPlanBuildStatus.Pending,
      ].includes(buildStatus)
    ) {
      startPolling(3000);
    } else {
      stopPolling();
    }
    return () => stopPolling();
  }, [buildStatus, id, startPolling, stopPolling]);

  if (loading && !data) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null || !businessAreaData) return null;

  const { paymentPlan } = data;

  return (
    <EditTargetPopulation
      paymentPlan={paymentPlan}
      screenBeneficiary={businessAreaData?.businessArea?.screenBeneficiary}
    />
  );
};

export default withErrorBoundary(
  EditTargetPopulationPage,
  'EditTargetPopulationPage',
);
