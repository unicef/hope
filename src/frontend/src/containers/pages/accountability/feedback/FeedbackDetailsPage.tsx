import { Grid } from '@mui/material';
import * as React from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { useFeedbackQuery } from '@generated/graphql';
import { FeedbackDetails } from '@components/accountability/Feedback/FeedbackDetails/FeedbackDetails';
import { FeedbackDetailsToolbar } from '@components/accountability/Feedback/FeedbackDetailsToolbar';
import { LinkedGrievance } from '@components/accountability/Feedback/LinkedGrievance/LinkedGrievance';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { UniversalErrorBoundary } from '@components/core/UniversalErrorBoundary';

export function FeedbackDetailsPage(): React.ReactElement {
  const { id } = useParams();
  const location = useLocation();
  const permissions = usePermissions();

  const { data, loading, error } = useFeedbackQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });

  const feedback = data?.feedback;

  if (loading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

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
    <UniversalErrorBoundary
      location={location}
      beforeCapture={(scope) => {
        scope.setTag('location', location.pathname);
        scope.setTag('component', 'FeedbackDetailsPage.tsx');
      }}
      componentName="FeedbackDetailsPage"
    >
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
    </UniversalErrorBoundary>
  );
}
