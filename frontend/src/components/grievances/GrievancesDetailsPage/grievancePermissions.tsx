import {
  hasCreatorOrOwnerPermissions,
  PERMISSIONS,
  hasPermissions,
} from '../../../config/permissions';
import { GRIEVANCE_CATEGORIES } from '../../../utils/constants';
import { AllGrievanceTicketQuery } from '../../../__generated__/graphql';

export const grievancePermissions = (
  isCreator: boolean,
  isOwner: boolean,
  ticket: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'],
  permissions: string[],
): { [key: string]: boolean } => {
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

  const canEdit = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_UPDATE,
    isCreator,
    PERMISSIONS.GRIEVANCES_UPDATE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_UPDATE_AS_OWNER,
    permissions,
  );

  const canAddNote = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_ADD_NOTE,
    isCreator,
    PERMISSIONS.GRIEVANCES_ADD_NOTE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_ADD_NOTE_AS_OWNER,
    permissions,
  );

  const canSetInProgress = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SET_IN_PROGRESS,
    isCreator,
    PERMISSIONS.GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SET_IN_PROGRESS_AS_OWNER,
    permissions,
  );

  const canSetOnHold = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SET_ON_HOLD,
    isCreator,
    PERMISSIONS.GRIEVANCES_SET_ON_HOLD_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SET_ON_HOLD_AS_OWNER,
    permissions,
  );

  const canSendForApproval = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SEND_FOR_APPROVAL,
    isCreator,
    PERMISSIONS.GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER,
    permissions,
  );
  const canSendBack = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_SEND_BACK,
    isCreator,
    PERMISSIONS.GRIEVANCES_SEND_BACK_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_SEND_BACK_AS_OWNER,
    permissions,
  );
  const isFeedbackType = [
    GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK,
    GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK,
    GRIEVANCE_CATEGORIES.REFERRAL,
  ].includes(ticket.category.toString());
  const canClose =
    (isFeedbackType &&
      hasCreatorOrOwnerPermissions(
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_FEEDBACK,
        isCreator,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR,
        isOwner,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER,
        permissions,
      )) ||
    (!isFeedbackType &&
      hasCreatorOrOwnerPermissions(
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        isCreator,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
        isOwner,
        PERMISSIONS.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
        permissions,
      ));

  const canApproveDataChange = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE,
    isCreator,
    PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
    permissions,
  );

  const canApproveFlagAndAdjudication = hasCreatorOrOwnerPermissions(
    PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
    isCreator,
    PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
    isOwner,
    PERMISSIONS.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
    permissions,
  );

  const canAssign = hasPermissions(PERMISSIONS.GRIEVANCES_ASSIGN, permissions);

  return {
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
    canAssign,
  };
};
