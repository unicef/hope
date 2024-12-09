import { ReactElement, useEffect } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import {
  useBusinessAreaDataQuery,
  usePaymentPlanQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { EditTargetPopulation } from '@components/targeting/EditTargetPopulation/EditTargetPopulation';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';

export const EditTargetPopulationPage = (): ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const location = useLocation();

  const { data, loading, error, startPolling, stopPolling } =
    usePaymentPlanQuery({
      variables: { id },
      fetchPolicy: 'cache-and-network',
    });
  const { businessArea } = useBaseUrl();

  const { data: businessAreaData } = useBusinessAreaDataQuery({
    variables: { businessAreaSlug: businessArea },
  });
  const buildStatus = data?.targetPopulation?.buildStatus;
  useEffect(() => {
    if (
      [
        TargetPopulationBuildStatus.Building,
        TargetPopulationBuildStatus.Pending,
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
    <UniversalErrorBoundary
      location={location}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname);
        scope.setTag('component', 'EditTargetPopulationPage.tsx');
      }}
      componentName="EditTargetPopulationPage"
    >
      <EditTargetPopulation
        targetPopulation={paymentPlan}
        screenBeneficiary={businessAreaData?.businessArea?.screenBeneficiary}
      />
    </UniversalErrorBoundary>
  );
};
