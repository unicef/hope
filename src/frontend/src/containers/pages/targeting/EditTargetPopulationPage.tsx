import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import withErrorBoundary from '@components/core/withErrorBoundary';
import EditTargetPopulation from '@components/targeting/EditTargetPopulation/EditTargetPopulation';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { isPermissionDeniedError } from '@utils/utils';
import { ReactElement } from 'react';
import { useParams } from 'react-router-dom';

const EditTargetPopulationPage = (): ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const { businessArea, programId } = useBaseUrl();

  const {
    data: paymentPlan,
    isLoading: loading,
    error,
  } = useQuery<TargetPopulationDetail>({
    queryKey: ['targetPopulation', businessArea, id, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsTargetPopulationsRetrieve({
        businessAreaSlug: businessArea,
        id: id,
        programSlug: programId,
      }),
  });

  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: ['businessArea', businessArea],
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({
        slug: businessArea,
      }),
  });

  if (loading && !paymentPlan) return <LoadingComponent />;

  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!paymentPlan || permissions === null || !businessAreaData) return null;

  return (
    <EditTargetPopulation
      paymentPlan={paymentPlan}
      screenBeneficiary={businessAreaData?.screenBeneficiary}
    />
  );
};

export default withErrorBoundary(
  EditTargetPopulationPage,
  'EditTargetPopulationPage',
);
