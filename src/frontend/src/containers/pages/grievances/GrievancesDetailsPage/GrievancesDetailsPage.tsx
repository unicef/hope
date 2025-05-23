import { Grid2 as Grid } from '@mui/material';
import { useParams } from 'react-router-dom';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { PermissionDenied } from '@components/core/PermissionDenied';
import { GrievanceDetailsToolbar } from '@components/grievances/GrievanceDetailsToolbar';
import { GrievancesSidebar } from '@components/grievances/GrievancesSidebar/GrievancesSidebar';
import { Notes } from '@components/grievances/Notes/Notes';
import { hasPermissions, PERMISSIONS } from '../../../../config/permissions';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { isPermissionDeniedError } from '@utils/utils';
import { UniversalActivityLogTable } from '../../../tables/UniversalActivityLogTable';
import { grievancePermissions } from './grievancePermissions';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import GrievancesApproveSection from '@components/grievances/GrievancesApproveSection/GrievancesApproveSection';
import GrievancesDetails from '@components/grievances/GrievancesDetails/GrievancesDetails';
import { useQuery } from '@tanstack/react-query';
import { RestService } from '@restgenerated/services/RestService';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

const GrievancesDetailsPage = (): ReactElement => {
  const { id } = useParams();
  const { businessAreaSlug, programSlug } = useBaseUrl();
  const permissions = usePermissions();
  const { data: currentUserData, isLoading: currentUserDataLoading } = useQuery(
    {
      queryKey: ['profile', businessAreaSlug, programSlug],
      queryFn: () => {
        return RestService.restBusinessAreasUsersProfileRetrieve({
          businessAreaSlug: businessAreaSlug,
          program: programSlug === 'all' ? undefined : programSlug,
        });
      },
      staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
      gcTime: 30 * 60 * 1000, // Keep unused data in cache for 30 minutes
      refetchOnWindowFocus: false, // Don't refetch when window regains focus
    },
  );

  const {
    data: grievanceTicket,
    isLoading: loading,
    error,
  } = useQuery<GrievanceTicketDetail>({
    queryKey: ['businessAreaProgram', businessAreaSlug, id],
    queryFn: () =>
      RestService.restBusinessAreasGrievanceTicketsRetrieve({
        businessAreaSlug,
        id: id,
      }),
  });

  const { baseUrl } = useBaseUrl();

  const { data: choicesData, isLoading: choicesLoading } =
    useQuery<GrievanceTicketDetail>({
      queryKey: ['businessAreasGrievanceTicketsChoices', businessAreaSlug],
      queryFn: () =>
        RestService.restBusinessAreasGrievanceTicketsChoicesRetrieve({
          businessAreaSlug,
        }),
    });

  if (choicesLoading || loading || currentUserDataLoading)
    return <LoadingComponent />;
  if (isPermissionDeniedError(error)) return <PermissionDenied />;

  if (
    !grievanceTicket ||
    !choicesData ||
    !currentUserData ||
    permissions === null
  )
    return null;

  const ticket = grievanceTicket;
  const currentUserId = currentUserData?.id;
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
export default withErrorBoundary(
  GrievancesDetailsPage,
  'GrievancesDetailsPage',
);
