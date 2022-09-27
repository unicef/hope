import { Grid } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import { FeedbackDetails } from '../../../../components/accountability/Feedback/FeedbackDetails/FeedbackDetails';
import { FeedbackDetailsToolbar } from '../../../../components/accountability/Feedback/FeedbackDetailsToolbar';
import { LinkedGrievance } from '../../../../components/accountability/Feedback/LinkedGrievance/LinkedGrievance';
import { Messages } from '../../../../components/accountability/Feedback/Messages';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../../utils/utils';
import { useFeedbackQuery } from '../../../../__generated__/graphql';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';

export const FeedbackDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();

  const { data, loading, error } = useFeedbackQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });

  const feedback = data?.feedback;

  const canEdit = hasPermissions(
    PERMISSIONS.ACCOUNTABILITY_FEEDBACK_VIEW_UPDATE,
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
  //TODO: do we need another permission?
  const canAddMessage = hasPermissions(
    PERMISSIONS.ACCOUNTABILITY_FEEDBACK_VIEW_UPDATE,
    permissions,
  );

  if (loading) return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || permissions === null) return null;

  return (
    <>
      <FeedbackDetailsToolbar canEdit={canEdit} feedback={feedback} />
      <Grid container>
        <FeedbackDetails
          feedback={feedback}
          businessArea={businessArea}
          canViewHouseholdDetails={canViewHouseholdDetails}
          canViewIndividualDetails={canViewIndividualDetails}
        />
        {/* <Messages messages={feedback.messages} canAddMessage={canAddMessage} /> */}
        <LinkedGrievance businessArea={businessArea} feedback={feedback} />
      </Grid>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={feedback.id} />
      )}
    </>
  );
};
