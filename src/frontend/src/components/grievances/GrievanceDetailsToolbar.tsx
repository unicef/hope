import { Box, Button } from '@mui/material';
import EditIcon from '@mui/icons-material/EditRounded';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import {
  GrievanceTicketQuery,
  useGrievanceTicketStatusChangeMutation,
} from '@generated/graphql';
import { useSnackbar } from '@hooks/useSnackBar';
import { MiśTheme } from '../../theme';
import {
  GRIEVANCE_CATEGORIES,
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '@utils/constants';
import { BreadCrumbsItem } from '@core/BreadCrumbs';
import { ButtonDialog } from '@core/ButtonDialog';
import { useConfirmation } from '@core/ConfirmationDialog';
import { LoadingButton } from '@core/LoadingButton';
import { PageHeader } from '@core/PageHeader';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from '../../programContext';
import { getGrievanceEditPath } from './utils/createGrievanceUtils';
import { AdminButton } from '@core/AdminButton';

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
  const { showMessage } = useSnackbar();
  const { baseUrl } = useBaseUrl();
  const confirm = useConfirmation();
  const navigate = useNavigate();
  const { isActiveProgram } = useProgramContext();

  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Grievance and Feedback'),
      to: `/${baseUrl}/grievance/tickets/user-generated`,
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
      const filterData = (data: any) => {
        const excludedKeys = [
          'previous_documents',
          'previous_identities',
          'previous_payment_channels',
          'flex_fields',
        ];

        return Object.keys(data)
          .filter((key) => !excludedKeys.includes(key))
          .reduce((obj, key) => ({ ...obj, [key]: data[key] }), {});
      };

      const generateConfirmationText = (
        approved: number,
        notApproved: number,
      ): string => {
        if (!notApproved) {
          return '';
        }

        if (!approved) {
          return t(
            'You approved 0 changes, remaining proposed changes will be automatically rejected upon ticket closure.',
          );
        }

        const approvedText = `${approved} change${approved > 1 ? 's' : ''}`;
        return `You approved ${approvedText}. Remaining change requests (${notApproved}) will be automatically rejected.`;
      };

      const filteredData = filterData(allData);

      const { approved, notApproved } = countApprovedAndUnapproved(
        Object.values(filteredData),
      );

      return generateConfirmationText(approved, notApproved);
    };

  const getClosingConfirmationExtraTextForOtherTypes = (): string => {
    const isDataChangeCategory =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.DATA_CHANGE;
    const isDeduplicationCategory =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION;
    const isSystemFlaggingCategory =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING;

    const hasApproveOption =
      isDataChangeCategory ||
      isDeduplicationCategory ||
      isSystemFlaggingCategory;

    if (!hasApproveOption) {
      return '';
    }

    const isDeleteIndividualIssue =
      ticket.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL;
    const isAddIndividualIssue =
      ticket.issueType?.toString() === GRIEVANCE_ISSUE_TYPES.ADD_INDIVIDUAL;

    const notApprovedDeleteIndividualChanges =
      isDeleteIndividualIssue &&
      ticket.deleteIndividualTicketDetails?.approveStatus === false;
    const notApprovedAddIndividualChanges =
      isAddIndividualIssue &&
      ticket.addIndividualTicketDetails?.approveStatus === false;
    const notApprovedSystemFlaggingChanges =
      isSystemFlaggingCategory &&
      ticket.systemFlaggingTicketDetails?.approveStatus === false;

    let confirmationMessage = '';
    if (notApprovedDeleteIndividualChanges) {
      confirmationMessage = t(
        'You did not approve any changes. Are you sure you want to close the ticket?',
      );
    } else if (notApprovedAddIndividualChanges) {
      confirmationMessage = t('You did not approve any changes.');
    } else if (notApprovedSystemFlaggingChanges) {
      confirmationMessage = '';
    } else if (isDeduplicationCategory) {
      confirmationMessage = t(
        'By continuing you acknowledge that individuals in this ticket were reviewed and all were deemed either distinct or duplicates in the system.',
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

  const closingConfirmationText = t(
    'Are you sure you want to close the ticket?',
  );

  const closingWarningText =
    ticket?.businessArea.postponeDeduplication === true
      ? t(
          'This ticket will be closed without running the deduplication process.',
        )
      : null;

  const changeState = async (status): Promise<void> => {
    try {
      await mutate({
        variables: {
          grievanceTicketId: ticket.id,
          status,
        },
      });
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const getClosingConfirmationText = (): string => {
    const isDeduplicationCategory =
      ticket.category.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION;
    const isSystemFlaggingCategory =
      ticket.category?.toString() === GRIEVANCE_CATEGORIES.SYSTEM_FLAGGING;

    let additionalContent = '';
    const notApprovedSystemFlaggingChanges =
      isSystemFlaggingCategory &&
      ticket.systemFlaggingTicketDetails?.approveStatus === false;

    if (notApprovedSystemFlaggingChanges) {
      additionalContent = t(
        ' By continuing you acknowledge that individuals in this ticket was compared with sanction list. No matches were found',
      );
    }

    const householdHasOneIndividual =
      ticket.household?.activeIndividualsCount === 1;
    if (
      (isDeduplicationCategory || isSystemFlaggingCategory) &&
      householdHasOneIndividual
    ) {
      additionalContent += t(
        ' When you close this ticket, the household that this Individual is a member of will be deactivated.',
      );
    }

    if (isDeduplicationCategory) {
      return getClosingConfirmationExtraText() + additionalContent;
    }

    return `${closingConfirmationText}${additionalContent}`;
  };

  const isDeduplicationCategory =
    ticket.category.toString() === GRIEVANCE_CATEGORIES.NEEDS_ADJUDICATION;
  const hasDuplicatedDocument =
    ticket?.needsAdjudicationTicketDetails?.hasDuplicatedDocument;
  const isMultipleDuplicatesVersion =
    ticket?.needsAdjudicationTicketDetails?.isMultipleDuplicatesVersion;
  const selectedIndividual =
    ticket?.needsAdjudicationTicketDetails?.selectedIndividual;
  const selectedIndividualsLength =
    ticket?.needsAdjudicationTicketDetails?.selectedDuplicates.length;

  const shouldShowButtonDialog =
    isDeduplicationCategory &&
    hasDuplicatedDocument &&
    ((isMultipleDuplicatesVersion && selectedIndividualsLength) ||
      (!isMultipleDuplicatesVersion && selectedIndividual));

  const closeButton = shouldShowButtonDialog ? (
    <ButtonDialog
      title={t('Duplicate Document Conflict')}
      buttonText={t('Close Ticket')}
      message={t(
        'The individuals have matching document numbers. HOPE requires that document numbers are unique. Please resolve before closing the ticket.',
      )}
    />
  ) : (
    <LoadingButton
      loading={loading}
      color="primary"
      variant="contained"
      onClick={() =>
        confirm({
          title: t('Close ticket'),
          extraContent: isDeduplicationCategory
            ? closingConfirmationText
            : getClosingConfirmationExtraText(),
          content: getClosingConfirmationText(),
          warningContent: closingWarningText,
          continueText: t('close ticket'),
        }).then(async () => {
          try {
            await changeState(GRIEVANCE_TICKET_STATES.CLOSED);
          } catch (e) {
            e.graphQLErrors.map((x) => showMessage(x.message));
          }
        })
      }
      data-cy="button-close-ticket"
      disabled={!isActiveProgram}
    >
      {t('Close Ticket')}
    </LoadingButton>
  );

  const canCreateDataChange = (): boolean =>
    [
      GRIEVANCE_ISSUE_TYPES.PAYMENT_COMPLAINT,
      GRIEVANCE_ISSUE_TYPES.FSP_COMPLAINT,
    ].includes(ticket.issueType?.toString());

  const grievanceEditPath = getGrievanceEditPath(
    ticket.id,
    ticket.category,
    baseUrl,
  );

  return (
    <PageHeader
      title={`Ticket ID: ${ticket.unicefId}`}
      breadCrumbs={breadCrumbsItems}
      flags={<AdminButton adminUrl={ticket.adminUrl} />}
    >
      <Box display="flex" alignItems="center">
        {isEditable && canEdit && (
          <Box mr={3}>
            <Button
              color="primary"
              variant="outlined"
              component={Link}
              to={grievanceEditPath}
              startIcon={<EditIcon />}
              data-cy="button-edit"
              disabled={!isActiveProgram}
            >
              {t('Edit')}
            </Button>
          </Box>
        )}
        {isNew && canEdit && canAssign && <Separator />}
        {isNew && canEdit && canAssign && (
          <LoadingButton
            loading={loading}
            color="primary"
            variant="contained"
            onClick={() => changeState(GRIEVANCE_TICKET_STATES.ASSIGNED)}
            data-cy="button-assign-to-me"
            disabled={!isActiveProgram}
          >
            {t('ASSIGN TO ME')}
          </LoadingButton>
        )}
        {isAssigned && canSetInProgress && (
          <Box mr={3}>
            <LoadingButton
              loading={loading}
              color="primary"
              variant="contained"
              onClick={() => {
                changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS);
              }}
              data-cy="button-set-to-in-progress"
              disabled={!isActiveProgram}
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
                  color="primary"
                  variant="outlined"
                  onClick={() => changeState(GRIEVANCE_TICKET_STATES.ON_HOLD)}
                  data-cy="button-set-on-hold"
                  disabled={!isActiveProgram}
                >
                  {t('Set On Hold')}
                </LoadingButton>
              </Box>
            )}
            {canSendForApproval && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color="primary"
                  variant="contained"
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                  }
                  data-cy="button-send-for-approval"
                  disabled={!isActiveProgram}
                >
                  {t('Send For Approval')}
                </LoadingButton>
              </Box>
            )}
            {isFeedbackType && canClose && (
              <Button
                color="primary"
                variant="contained"
                onClick={() =>
                  confirm({
                    content: closingConfirmationText,
                    continueText: 'close ticket',
                  }).then(() => changeState(GRIEVANCE_TICKET_STATES.CLOSED))
                }
                data-cy="button-close-ticket"
                disabled={!isActiveProgram}
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
                  color="primary"
                  variant="contained"
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)
                  }
                  data-cy="button-set-to-in-progress"
                  disabled={!isActiveProgram}
                >
                  {t('Set to in progress')}
                </LoadingButton>
              </Box>
            )}
            {canSendForApproval && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color="primary"
                  variant="contained"
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.FOR_APPROVAL)
                  }
                  data-cy="button-send-for-approval"
                  disabled={!isActiveProgram}
                >
                  {t('Send For Approval')}
                </LoadingButton>
              </Box>
            )}
            {isFeedbackType && canClose && (
              <LoadingButton
                loading={loading}
                color="primary"
                variant="contained"
                onClick={() =>
                  confirm({
                    content: closingConfirmationText,
                    continueText: 'close ticket',
                  }).then(() => changeState(GRIEVANCE_TICKET_STATES.CLOSED))
                }
                data-cy="button-close-ticket"
                disabled={!isActiveProgram}
              >
                {t('Close Ticket')}
              </LoadingButton>
            )}
          </>
        )}
        {isForApproval && (
          <>
            {canSendBack && (
              <Box mr={3}>
                <LoadingButton
                  loading={loading}
                  color="primary"
                  variant="contained"
                  onClick={() =>
                    changeState(GRIEVANCE_TICKET_STATES.IN_PROGRESS)
                  }
                  data-cy="button-send-back"
                  disabled={!isActiveProgram}
                >
                  {t('Send Back')}
                </LoadingButton>
              </Box>
            )}
            {canCreateDataChange() && (
              <Box mr={3}>
                <Button
                  onClick={() =>
                    navigate(`/${baseUrl}/grievance/new-ticket`, {
                      state: {
                        category: GRIEVANCE_CATEGORIES.DATA_CHANGE,
                        selectedIndividual: ticket.individual,
                        selectedHousehold: ticket.household,
                        linkedTicketId: ticket.id,
                      },
                    })
                  }
                  variant="outlined"
                  color="primary"
                  data-cy="button-create-data-change"
                  disabled={!isActiveProgram}
                >
                  {t('Create a Data Change ticket')}
                </Button>
              </Box>
            )}
            {canClose && closeButton}
          </>
        )}
      </Box>
    </PageHeader>
  );
};
