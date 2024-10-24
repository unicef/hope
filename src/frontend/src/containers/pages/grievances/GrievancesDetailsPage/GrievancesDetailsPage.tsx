import { Grid } from '@mui/material';
import * as React from 'react';
import { useParams } from 'react-router-dom';
import {
  useGrievancesChoiceDataQuery,
  useGrievanceTicketQuery,
  useMeQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { GrievanceDetailsToolbar } from '@components/grievances/GrievanceDetailsToolbar';
import { GrievancesApproveSection } from '@components/grievances/GrievancesApproveSection/GrievancesApproveSection';
import { GrievancesDetails } from '@components/grievances/GrievancesDetails/GrievancesDetails';
import { GrievancesSidebar } from '@components/grievances/GrievancesSidebar/GrievancesSidebar';
import { Notes } from '@components/grievances/Notes/Notes';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { grievancePermissions } from './grievancePermissions';

export const GrievancesDetailsPage = (): React.ReactElement => {
  const { id } = useParams();
  const permissions = usePermissions();
  const { data: currentUserData, loading: currentUserDataLoading } =
    useMeQuery();
  const { data, loading, error } = useGrievanceTicketQuery({
    variables: { id },
    fetchPolicy: 'network-only',
  });

  const { baseUrl } = useBaseUrl();
  const { data: choicesData, loading: choicesLoading } =
    useGrievancesChoiceDataQuery();

  if (choicesLoading || loading || currentUserDataLoading)
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !data?.grievanceTicket ||
    !choicesData ||
    !currentUserData ||
    permissions === null
  )
    return null;

  const ticket = data?.grievanceTicket;
  const currentUserId = currentUserData?.me?.id;
  const isCreator = currentUserId === ticket?.createdBy?.id;
  const isOwner = currentUserId === ticket?.assignedTo?.id;

  const {
    canViewHouseholdDetails,
    canViewIndividualDetails,
    canEdit,
    canAddNote,
    canSetInProgress,
    canSetOnHold,
    canSendForApproval,
    canSendBack,
    canClose,
    canApproveDataChange,
    canApproveFlagAndAdjudication,
    canApprovePaymentVerification,
    canAssign,
  } = grievancePermissions(isCreator, isOwner, ticket, permissions);

  return (
    <>
      <GrievanceDetailsToolbar
        ticket={ticket}
        canEdit={canEdit}
        canSetInProgress={canSetInProgress}
        canSetOnHold={canSetOnHold}
        canSendForApproval={canSendForApproval}
        canSendBack={canSendBack}
        canClose={canClose}
        canAssign={canAssign}
      />
      <Grid container>
        <GrievancesDetails
          ticket={ticket}
          choicesData={choicesData}
          baseUrl={baseUrl}
          canViewHouseholdDetails={canViewHouseholdDetails}
          canViewIndividualDetails={canViewIndividualDetails}
        />
        <GrievancesApproveSection
          ticket={ticket}
          baseUrl={baseUrl}
          canApproveFlagAndAdjudication={canApproveFlagAndAdjudication}
          canApproveDataChange={canApproveDataChange}
          canApprovePaymentVerification={canApprovePaymentVerification}
        />
        <Notes notes={ticket.ticketNotes} canAddNote={canAddNote} />
        <GrievancesSidebar ticket={ticket} />
      </Grid>
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={ticket.id} />
      )}
    </>
  );
};
