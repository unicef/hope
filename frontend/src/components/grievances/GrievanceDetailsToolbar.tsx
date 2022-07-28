import { Box, Button } from '@material-ui/core';
import EditIcon from '@material-ui/icons/EditRounded';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useSnackbar } from '../../hooks/useSnackBar';
import { MiśTheme } from '../../theme';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../utils/constants';
import {
  GrievanceTicketDocument,
  GrievanceTicketQuery,
  useGrievanceTicketStatusChangeMutation,
} from '../../__generated__/graphql';
import { BreadCrumbsItem } from '../core/BreadCrumbs';
import { PageHeader } from '../core/PageHeader';
import { useConfirmation } from '../core/ConfirmationDialog';
import { ButtonDialog } from '../core/ButtonDialog';
import { LoadingButton } from '../core/LoadingButton';

const Separator = styled.div`
  width: 1px;
  height: 28px;
  border: 1px solid
    ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.lightGray};
  margin: 0 28px;
`;

const countApprovedAndUnapproved = (
  data,
): { approved: number; notApproved: number } => {
  let approved = 0;
  let notApproved = 0;
  const flattenArray = data.flat(2);
  flattenArray.forEach((item) => {
    if (item.approve_status === true) {
      approved += 1;
    } else {
      notApproved += 1;
    }
  });

  return { approved, notApproved };
};

export const GrievanceDetailsToolbar = ({
  ticket,
  canEdit,
  canSetInProgress,
  canSetOnHold,
  canSendForApproval,
  canSendBack,
  canClose,
  canAssign,
}: {
  ticket: GrievanceTicketQuery['grievanceTicket'];
  canEdit: boolean;
  canSetInProgress: boolean;
  canSetOnHold: boolean;
  canSendForApproval: boolean;
  canSendBack: boolean;
  canClose: boolean;
  canAssign: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const confirm = useConfirmation();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: `/${businessArea}/grievance-and-feedback/`,
    },
  ];
  const [mutate, { loading }] = useGrievanceTicketStatusChangeMutation();

  const isNew = ticket.status === GRIEVANCE_TICKET_STATES.NEW;
  const isAssigned = ticket.status === GRIEVANCE_TICKET_STATES.ASSIGNED;
  const isInProgress = ticket.status === GRIEVANCE_TICKET_STATES.IN_PROGRESS;
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const isOnHold = ticket.status === GRIEVANCE_TICKET_STATES.ON_HOLD;
  const isClosed = ticket.status === GRIEVANCE_TICKET_STATES.CLOSED;
  const isEditable = !isClosed;

  const isFeedbackType =
    ticket.category.toString() === GRIEVANCE_CATEGORIES.POSITIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.NEGATIVE_FEEDBACK ||
    ticket.category.toString() === GRIEVANCE_CATEGORIES.REFERRAL;

  const getClosingConfirmationExtraTextForIndividualAndHouseholdDataChange =
    (): string => {
      const householdData =
        ticket.householdDataUpdateTicketDetails?.householdData || {};
      const individualData =
        ticket.individualDataUpdateTicketDetails?.individualData || {};
      const allData = {
        ...householdData,
        ...individualData,
        ...householdData?.flex_fields,
        ...individualData?.flex_fields,
      };
      delete allData.previous_documents;
      delete allData.previous_identities;
      delete allData.flex_fields;

      const { approved, notApproved } = countApprovedAndUnapproved(
        Object.values(allData),
      );
      // all changes were approved
      if (!notApproved) return '';

      // no changes were approved
      if (!approved)
        return t(
          `You approved 0 changes, remaining proposed changes will be automatically rejected upon ticket closure.`,
        );

      // some changes were approved
      return `You approved ${approved} change${
        approved > 1 ? 's' : ''
      }. Remaining change requests (${notApproved}) will be automatically rejected.`;
    };

  const getClosingConfirmationExtraTextForOtherTypes = (): string => {
    const hasApproveOption =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE ||
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION ||
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING;

    if (!hasApproveOption) {
      return '';
    }

    const notApprovedDeleteIndividualChanges =
      ticket.issueType?.toString() ===
        GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL &&
      ticket.deleteIndividualTicketDetails?.approveStatus === false;

    const notApprovedAddIndividualChanges =
      ticket.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL &&
      ticket.addIndividualTicketDetails?.approveStatus === false;

    const notApprovedSystemFlaggingChanges =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING &&
      ticket.systemFlaggingTicketDetails?.approveStatus === false;

    const noDuplicatesFound =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
      !ticket.needsAdjudicationTicketDetails?.selectedIndividual &&
      !ticket.needsAdjudicationTicketDetails?.isMultipleDuplicatesVersion;

    const noDuplicatesFoundMultiple =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
      ticket.needsAdjudicationTicketDetails?.isMultipleDuplicatesVersion &&
      !ticket.needsAdjudicationTicketDetails?.selectedIndividuals.length;

    // added msg handling for
    let confirmationMessage = '';
    if (notApprovedDeleteIndividualChanges) {
      confirmationMessage = t(
        'You did not approve any changes. Are you sure you want to close the ticket?',
      );
    } else if (notApprovedAddIndividualChanges) {
      confirmationMessage = t('You did not approve any changes.');
    } else if (notApprovedSystemFlaggingChanges) {
      confirmationMessage = '';
    } else if (noDuplicatesFound) {
      confirmationMessage = t(
        'By continuing you acknowledge that individuals in this ticket were reviewed and all were deemed unique to the system. No duplicates were found',
      );
    } else if (noDuplicatesFoundMultiple) {
      confirmationMessage = t(
        'By continuing you acknowledge that individuals in this ticket were reviewed and all were deemed unique to the system. No duplicates were found',
      );
    }
    return confirmationMessage;
  };

  const getClosingConfirmationExtraText = (): string => {
    switch (ticket.issueType?.toString()) {
      case GRIEVANCE_ISSUE_TYPES.EDIT_HOUSEHOLD:
        return getClosingConfirmationExtraTextForIndividualAndHouseholdDataChange();
      case GRIEVANCE_ISSUE_TYPES.EDIT_INDIVIDUAL:
        return getClosingConfirmationExtraTextForIndividualAndHouseholdDataChange();

      default:
        return getClosingConfirmationExtraTextForOtherTypes();
    }
  };

  let closingConfirmationText = t(
    'Are you sure you want to close the ticket?',
  );

  if (ticket?.postponeDeduplication === true) {
    closingConfirmationText = `${closingConfirmationText} ${t(
     'This ticket will be closed without running the deduplication process.'
    )}`;
  }

  const changeState = async (status): Promise<void> => {
    try {
      await mutate({
        variables: {
          grievanceTicketId: ticket.id,
          status,
        },
        refetchQueries: () => [
          {
            query: GrievanceTicketDocument,
            variables: { id: ticket.id },
          },
        ],
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const getClosingConfirmationText = (): string => {
    if (ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION) {
      return getClosingConfirmationExtraText();
    }
    let additionalContent = '';
    const notApprovedSystemFlaggingChanges =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING &&
      ticket.systemFlaggingTicketDetails?.approveStatus === false;

    if (notApprovedSystemFlaggingChanges) {
      additionalContent = t(
        ' By continuing you acknowledge that individuals in this ticket was compared with sanction list. No matches were found',
      );
    }

    const householdHasOneIndividual =
      ticket.household?.activeIndividualsCount === 1;
    if (householdHasOneIndividual) {
      additionalContent = t(
        ' When you close this ticket, the household that this Individual is a member of will be deactivated.',
      );
    }
    return `${closingConfirmationText}${additionalContent}`;
  };

  let closeButton = (
    <Button
      color='primary'
      variant='contained'
      onClick={() =>
        confirm({
          title: t('Close ticket'),
          extraContent:
            ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION
              ? closingConfirmationText
              : getClosingConfirmationExtraText(),
          content: getClosingConfirmationText(),
          continueText: t('close ticket'),
        }).then(() => {
          changeState(GRIEVANCE_TICKET_STATES.CLOSED);
        })
      }
    >
      {t('Close Ticket')}
    </Button>
  );
  if (
    ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
    ticket?.needsAdjudicationTicketDetails?.hasDuplicatedDocument &&
    !ticket?.needsAdjudicationTicketDetails?.isMultipleDuplicatesVersion &&
    !!ticket?.needsAdjudicationTicketDetails?.selectedIndividual
  ) {
    closeButton = (
      <ButtonDialog
        title={t('Duplicate Document Conflict')}
        buttonText={t('Close Ticket')}
        message={t(
          'The individuals have matching document numbers. HOPE requires that document numbers are unique. Please resolve before closing the ticket.',
        )}
      />
    );
  }

  if (
    ticket.category.toString() === GRIEVANCE_CATEGORIES.DEDUPLICATION &&
    ticket?.needsAdjudicationTicketDetails?.hasDuplicatedDocument &&
    ticket?.needsAdjudicationTicketDetails?.isMultipleDuplicatesVersion &&
    !!ticket?.needsAdjudicationTicketDetails?.selectedIndividuals.length
  ) {
    closeButton = (
      <ButtonDialog
        title={t('Duplicate Document Conflict')}
        buttonText={t('Close Ticket')}
        message={t(
          'The individuals have matching document numbers. HOPE requires that document numbers are unique. Please resolve before closing the ticket.',
        )}
      />
    );
  }

  return (
    <PageHeader
      title={`Ticket ID: ${ticket.unicefId}`}
      breadCrumbs={breadCrumbsItems}
    >
      <Box display='flex' alignItems='center'>
        {isEditable && canEdit && (
          <Box mr={3}>
            <Button
              color='primary'
              variant='outlined'
              component={Link}
              to={`/${businessArea}/grievance-and-feedback/edit-ticket/${id}`}
              startIcon={<EditIcon />}
            >
              {t('Edit')}
            </Button>
          </Box>
        )}
        {isNew && canEdit && canAssign && <Separator />}
        {isNew && canEdit && canAssign && (
          <>
            <LoadingButton
              loading={loading}
              color='primary'
              variant='contained'
              onClick={() => changeState(GRIEVANCE_TICKET_STATES.ASSIGNED)}
            >
              {t('ASSIGN TO ME')}
            </LoadingButton>
          </>
        )}
        {isAssigned && canSetInProgress && (
          <Box mr={3}>
            <LoadingButton
              loading={loading}
              color='primary'
              variant='contained'
              onClick={() => changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)}
            >
              {t('Set to in progress')}
            </LoadingButton>
          </Box>
        )}
        {isInProgress && (
          <>
            {canSetOnHold && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='outlined'
                  onClick={() => changeState(GRIEVANCE_TICKET_STATES.ON_HOLD)}
                >
                  {t('Set On Hold')}
                </LoadingButton>
              </Box>
            )}
            {canSendForApproval && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                  }
                >
                  {t('Send For Approval')}
                </LoadingButton>
              </Box>
            )}
            {isFeedbackType && canClose && (
              <Button
                color='primary'
                variant='contained'
                onClick={() =>
                  confirm({
                    content: closingConfirmationText,
                    continueText: 'close ticket',
                  }).then(() => changeState(GRIEVANCE_TICKET_STATES.CLOSED))
                }
              >
                {t('Close Ticket')}
              </Button>
            )}
          </>
        )}
        {isOnHold && (
          <>
            {canSetInProgress && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)
                  }
                >
                  {t('Set to in progress')}
                </LoadingButton>
              </Box>
            )}
            {canSendForApproval && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                  }
                >
                  {t('Send For Approval')}
                </LoadingButton>
              </Box>
            )}
            {isFeedbackType && canClose && (
              <Button
                color='primary'
                variant='contained'
                onClick={() =>
                  confirm({
                    content: closingConfirmationText,
                    continueText: 'close ticket',
                  }).then(() => changeState(GRIEVANCE_TICKET_STATES.CLOSED))
                }
              >
                {t('Close Ticket')}
              </Button>
            )}
          </>
        )}
        {isForApproval && (
          <>
            {canSendBack && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)
                  }
                >
                  {t('Send Back')}
                </LoadingButton>
              </Box>
            )}
            {canClose && closeButton}
          </>
        )}
      </Box>
    </PageHeader>
  );
};
