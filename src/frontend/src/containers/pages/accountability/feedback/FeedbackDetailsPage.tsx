import { Grid2 as Grid } from '@mui/material';
import { useParams } from 'react-router-dom';
import FeedbackDetailsToolbar from '@components/accountability/Feedback/FeedbackDetailsToolbar';
import LinkedGrievance from '@components/accountability/Feedback/LinkedGrievance/LinkedGrievance';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import FeedbackDetails from '@components/accountability/Feedback/FeedbackDetails/FeedbackDetails';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { FeedbackDetail } from '@restgenerated/models/FeedbackDetail';

function FeedbackDetailsPage(): ReactElement {
  const { id } = useParams();
  const permissions = usePermissions();
  const { businessAreaSlug } = useBaseUrl();

  const {
    data: feedback,
    isLoading,
    error,
  } = useQuery<FeedbackDetail>({
    queryKey: ['businessAreasFeedbacksRetrieve', businessAreaSlug, id],
    queryFn: () =>
      RestService.restBusinessAreasFeedbacksRetrieve({
        businessAreaSlug,
        id: id,
      }),
  });

  if (isLoading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!feedback || permissions === null) return null;

  const canEdit = hasPermissions(
    PERMISSIONS.GRIEVANCES_FEEDBACK_VIEW_UPDATE,
    permissions,
  );
  const canViewHouseholdDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
    permissions,
  );

  const canViewIndividualDetails = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUALS_DETAILS,
    permissions,
  );
  return (
    <>
      <FeedbackDetailsToolbar canEdit={canEdit} feedback={feedback} />
      <Grid container>
        <FeedbackDetails
          feedback={feedback}
          canViewHouseholdDetails={canViewHouseholdDetails}
          canViewIndividualDetails={canViewIndividualDetails}
        />
        <LinkedGrievance feedback={feedback} />
      </Grid>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={feedback.id} />
      )}
    </>
  );
}
export default withErrorBoundary(FeedbackDetailsPage, 'FeedbackDetailsPage');
