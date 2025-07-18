import { ReactElement } from 'react';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import EditTargetPopulation from '@components/targeting/EditTargetPopulation/EditTargetPopulation';
import { usePermissions } from '@hooks/usePermissions';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { useParams } from 'react-router-dom';
import { useBaseUrl } from '@hooks/useBaseUrl';

const EditTargetPopulationPage = (): ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const { businessArea, programSlug } = useBaseUrl();

  const {
    data: paymentPlan,
    isLoading: loading,
    error,
  } = useQuery<TargetPopulationDetail>({
    queryKey: ['targetPopulation', businessArea, id, programSlug],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsRetrieve({
        businessAreaSlug: businessArea,
        id: id,
        programSlug,
      }),
  });

  if (loading && !paymentPlan) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!paymentPlan || permissions === null) return null;


  return (
    <EditTargetPopulation
      paymentPlan={paymentPlan}
      screenBeneficiary={paymentPlan?.program?.screenBeneficiary}
    />
  );
};

export default withErrorBoundary(
  EditTargetPopulationPage,
  'EditTargetPopulationPage',
);
