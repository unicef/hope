import { Grid } from '@material-ui/core';
import React from 'react';
import { useParams } from 'react-router-dom';
import { FeedbackDetails } from '../../../../components/accountability/Feedback/FeedbackDetails/FeedbackDetails';
import { FeedbackDetailsToolbar } from '../../../../components/accountability/Feedback/FeedbackDetailsToolbar';
import { LinkedGrievance } from '../../../../components/accountability/Feedback/LinkedGrievance/LinkedGrievance';
import { Messages } from '../../../../components/accountability/Feedback/Messages';
import { LoadingComponent } from '../../../../components/core/LoadingComponent';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import {
  hasCreatorOrOwnerPermissions,
  hasPermissions,
  PERMISSIONS,
} from '../../../../config/permissions';
import { useBusinessArea } from '../../../../hooks/useBusinessArea';
import { usePermissions } from '../../../../hooks/usePermissions';
import { isPermissionDeniedError } from '../../../../utils/utils';
import {
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
  useMeQuery,
} from '../../../../__generated__/graphql';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';

export const FeedbackDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const businessArea = useBusinessArea();
  const {
    data: currentUserData,
    loading: currentUserDataLoading,
  } = useMeQuery();
  const { data, loading, error } = useGrievanceTicketQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });
  const ticket = data?.grievanceTicket;
  const currentUserId = currentUserData?.me?.id;
  const isCreator = currentUserId === ticket?.createdBy?.id;
  const isOwner = currentUserId === ticket?.assignedTo?.id;
  // TODO: add real permission
  const canEdit = true;
  const canAddMessage = true;
  const canViewHouseholdDetails = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS,
    isCreator,
    PERMISSIONS.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER,
    permissions,
  );

  const canViewIndividualDetails = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS,
    isCreator,
    PERMISSIONS.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER,
    permissions,
  );

  const {
    data: choicesData,
    loading: choicesLoading,
  } = useGrievancesChoiceDataQuery();

  if (choicesLoading || loading || currentUserDataLoading)
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (!data || !choicesData || !currentUserData || permissions === null)
    return null;

  return (
    <>
      <FeedbackDetailsToolbar canEdit={canEdit} ticket={ticket} />
      <Grid container>
        <FeedbackDetails
          ticket={ticket}
          choicesData={choicesData}
          businessArea={businessArea}
          canViewHouseholdDetails={canViewHouseholdDetails}
          canViewIndividualDetails={canViewIndividualDetails}
        />
        <Messages messages={ticket.ticketNotes} canAddMessage={canAddMessage} />
        <LinkedGrievance ticket={ticket} />
      </Grid>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={ticket.id} />
      )}
    </>
  );
};
