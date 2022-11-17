import { Box, Button, Paper, Typography } from '@material-ui/core';
import { Formik } from 'formik';
import camelCase from 'lodash/camelCase';
import mapKeys from 'lodash/mapKeys';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useSnackbar } from '../../hooks/useSnackBar';
import {
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '../../utils/constants';
import {
  GrievanceTicketNode,
  HouseholdNode,
  IndividualNode,
  IndividualRoleInHouseholdRole,
  useApproveIndividualDataChangeMutation,
} from '../../__generated__/graphql';
import { useConfirmation } from '../core/ConfirmationDialog';
import { Title } from '../core/Title';
import { RequestedIndividualDataChangeTable } from './RequestedIndividualDataChangeTable/RequestedIndividualDataChangeTable';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;

export type RoleReassignData = {
  role: IndividualRoleInHouseholdRole | string;
  individual: IndividualNode;
  household: HouseholdNode;
};

export function RequestedIndividualDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketNode;
  canApproveDataChange: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const individualData = {
    ...ticket.individualDataUpdateTicketDetails.individualData,
  };
  let allApprovedCount = 0;
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const documents = individualData?.documents || [];
  const documentsToRemove = individualData.documents_to_remove || [];
  const documentsToEdit = individualData.documents_to_edit || [];
  const identities = individualData?.identities || [];
  const identitiesToRemove = individualData.identities_to_remove || [];
  const identitiesToEdit = individualData.identities_to_edit || [];
  const paymentChannels = individualData?.payment_channels || [];
  const paymentChannelsToRemove =
    individualData.payment_channels_to_remove || [];
  const paymentChannelsToEdit = individualData.payment_channels_to_edit || [];
  const flexFields = individualData.flex_fields || {};
  delete individualData.flex_fields;
  delete individualData.documents;
  delete individualData.identities;
  delete individualData.documents_to_remove;
  delete individualData.payment_channels;
  delete individualData.payment_channels_to_remove;
  delete individualData.identities_to_remove;
  delete individualData.previous_documents;
  delete individualData.previous_identities;

  const entries = Object.entries(individualData);
  const entriesFlexFields = Object.entries(flexFields);
  allApprovedCount += documents.filter((el) => el.approve_status).length;
  allApprovedCount += documentsToRemove.filter((el) => el.approve_status)
    .length;
  allApprovedCount += documentsToEdit.filter((el) => el.approve_status).length;
  allApprovedCount += identities.filter((el) => el.approve_status).length;
  allApprovedCount += identitiesToRemove.filter((el) => el.approve_status)
    .length;
  allApprovedCount += identitiesToEdit.filter((el) => el.approve_status).length;
  allApprovedCount += paymentChannels.filter((el) => el.approve_status).length;
  allApprovedCount += paymentChannelsToRemove.filter((el) => el.approve_status)
    .length;
  allApprovedCount += paymentChannelsToEdit.filter((el) => el.approve_status)
    .length;
  allApprovedCount += entries.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;
  allApprovedCount += entriesFlexFields.filter(
    ([, value]: [string, { approve_status: boolean }]) => value.approve_status,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);
  const getConfirmationText = (allChangesLength): string => {
    return `You approved ${allChangesLength || 0} change${
      allChangesLength === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;
  };
  const [mutate] = useApproveIndividualDataChangeMutation();
  const selectedDocuments = [];
  const selectedDocumentsToRemove = [];
  const selectedDocumentsToEdit = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documents?.length; i++) {
    if (documents[i]?.approve_status) {
      selectedDocuments.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documentsToRemove?.length; i++) {
    if (documentsToRemove[i]?.approve_status) {
      selectedDocumentsToRemove.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documentsToEdit?.length; i++) {
    if (documentsToEdit[i]?.approve_status) {
      selectedDocumentsToEdit.push(i);
    }
  }
  const selectedIdentities = [];
  const selectedIdentitiesToRemove = [];
  const selectedIdentitiesToEdit = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identities?.length; i++) {
    if (identities[i]?.approve_status) {
      selectedIdentities.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identitiesToRemove?.length; i++) {
    if (identitiesToRemove[i]?.approve_status) {
      selectedIdentitiesToRemove.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identitiesToEdit?.length; i++) {
    if (identitiesToEdit[i]?.approve_status) {
      selectedIdentitiesToEdit.push(i);
    }
  }

  const selectedPaymentChannels = [];
  const selectedPaymentChannelsToRemove = [];
  const selectedPaymentChannelsToEdit = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < paymentChannels?.length; i++) {
    if (paymentChannels[i]?.approve_status) {
      selectedPaymentChannels.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < paymentChannelsToRemove?.length; i++) {
    if (paymentChannelsToRemove[i]?.approve_status) {
      selectedPaymentChannelsToRemove.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < paymentChannelsToEdit?.length; i++) {
    if (paymentChannelsToEdit[i]?.approve_status) {
      selectedPaymentChannelsToEdit.push(i);
    }
  }

  const isHeadOfHousehold =
    ticket.individual?.id === ticket.household?.headOfHousehold?.id;

  const primaryCollectorRolesCount =
    ticket?.individual?.householdsAndRoles.filter(
      (el) => el.role === IndividualRoleInHouseholdRole.Primary,
    ).length + (isHeadOfHousehold ? 1 : 0);
  const primaryColletorRolesReassignedCount = Object.values(
    JSON.parse(ticket.individualDataUpdateTicketDetails.roleReassignData),
  )?.filter(
    (el: RoleReassignData) =>
      el.role === IndividualRoleInHouseholdRole.Primary || el.role === 'HEAD',
  ).length;

  let approveEnabled = false;
  if (ticket.issueType.toString() === GRIEVANCE_ISSUE_TYPES.DELETE_INDIVIDUAL) {
    approveEnabled =
      isForApproval &&
      primaryCollectorRolesCount === primaryColletorRolesReassignedCount;
  } else {
    approveEnabled = isForApproval;
  }

  const shouldShowEditButton = (allChangesLength): boolean =>
    allChangesLength && !isEdit && isForApproval;

  const areAllApproved = (allSelected): boolean => {
    const countAll =
      entries.length +
      entriesFlexFields.length +
      documents.length +
      documentsToRemove.length +
      documentsToEdit.length +
      identities.length +
      identitiesToRemove.length +
      identitiesToEdit.length;
    return allSelected === countAll;
  };

  const getApprovalButton = (allSelected, submitForm): ReactElement => {
    if (areAllApproved(allSelected)) {
      return (
        <Button
          onClick={submitForm}
          variant='contained'
          color='primary'
          disabled={!approveEnabled}
        >
          {t('Approve')}
        </Button>
      );
    }
    return (
      <Button
        onClick={() =>
          confirm({
            title: t('Warning'),
            content: getConfirmationText(allSelected),
          }).then(() => {
            submitForm();
          })
        }
        variant='contained'
        color='primary'
        disabled={!approveEnabled}
      >
        {t('Approve')}
      </Button>
    );
  };

  return (
    <Formik
      initialValues={{
        selected: entries
          .filter((row) => {
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => camelCase(row[0])),
        selectedFlexFields: entriesFlexFields
          .filter((row) => {
            const valueDetails = mapKeys(row[1], (v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => row[0]),
        selectedDocuments,
        selectedDocumentsToRemove,
        selectedDocumentsToEdit,
        selectedIdentities,
        selectedIdentitiesToEdit,
        selectedIdentitiesToRemove,
        selectedPaymentChannels,
        selectedPaymentChannelsToEdit,
        selectedPaymentChannelsToRemove,
      }}
      onSubmit={async (values) => {
        const individualApproveData = values.selected.reduce((prev, curr) => {
          // eslint-disable-next-line no-param-reassign
          prev[curr] = true;
          return prev;
        }, {});
        const approvedDocumentsToCreate = values.selectedDocuments;
        const approvedDocumentsToRemove = values.selectedDocumentsToRemove;
        const approvedDocumentsToEdit = values.selectedDocumentsToEdit;
        const approvedIdentitiesToCreate = values.selectedIdentities;
        const approvedIdentitiesToRemove = values.selectedIdentitiesToRemove;
        const approvedIdentitiesToEdit = values.selectedIdentitiesToEdit;
        const approvedPaymentChannelsToCreate = values.selectedPaymentChannels;
        const approvedPaymentChannelsToRemove =
          values.selectedPaymentChannelsToRemove;
        const approvedPaymentChannelsToEdit =
          values.selectedPaymentChannelsToEdit;
        const flexFieldsApproveData = values.selectedFlexFields.reduce(
          (prev, curr) => {
            // eslint-disable-next-line no-param-reassign
            prev[curr] = true;
            return prev;
          },
          {},
        );
        try {
          await mutate({
            variables: {
              grievanceTicketId: ticket.id,
              individualApproveData: JSON.stringify(individualApproveData),
              approvedDocumentsToCreate,
              approvedDocumentsToRemove,
              approvedDocumentsToEdit,
              approvedIdentitiesToCreate,
              approvedIdentitiesToRemove,
              approvedIdentitiesToEdit,
              approvedPaymentChannelsToCreate,
              approvedPaymentChannelsToRemove,
              approvedPaymentChannelsToEdit,
              flexFieldsApproveData: JSON.stringify(flexFieldsApproveData),
            },
          });
          showMessage('Changes Approved');
          const sum = Object.values(values).flat().length;
          setEdit(sum === 0);
        } catch (e) {
          e.graphQLErrors.map((x) => showMessage(x.message));
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => {
        const allChangesLength = Object.values(values).flat().length;

        return (
          <StyledBox>
            <Title>
              <Box display='flex' justifyContent='space-between'>
                <Typography variant='h6'>Requested Data Change</Typography>
                {shouldShowEditButton(allChangesLength) ? (
                  <Button
                    onClick={() => setEdit(true)}
                    variant='outlined'
                    color='primary'
                    disabled={ticket.status === GRIEVANCE_TICKET_STATES.CLOSED}
                  >
                    {t('EDIT')}
                  </Button>
                ) : (
                  canApproveDataChange &&
                  getApprovalButton(allChangesLength, submitForm)
                )}
              </Box>
            </Title>
            <RequestedIndividualDataChangeTable
              values={values}
              ticket={ticket}
              setFieldValue={setFieldValue}
              isEdit={isEdit}
            />
          </StyledBox>
        );
      }}
    </Formik>
  );
}
