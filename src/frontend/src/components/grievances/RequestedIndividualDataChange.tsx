/* eslint-disable react-hooks/rules-of-hooks */

import { Box, Button, Typography } from '@mui/material';
import { Formik } from 'formik';
import camelCase from 'lodash/camelCase';
import mapKeys from 'lodash/mapKeys';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useSnackbar } from '@hooks/useSnackBar';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  GRIEVANCE_ISSUE_TYPES,
  GRIEVANCE_TICKET_STATES,
} from '@utils/constants';
import { useConfirmation } from '@core/ConfirmationDialog';
import { Title } from '@core/Title';
import { RequestedIndividualDataChangeTable } from './RequestedIndividualDataChangeTable/RequestedIndividualDataChangeTable';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { GrievanceIndividualDataChangeApprove } from '@restgenerated/models/GrievanceIndividualDataChangeApprove';
import { RestService } from '@restgenerated/services/RestService';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';
import { ApproveBox } from '@components/grievances/GrievancesApproveSection/ApproveSectionStyles';

export type RoleReassignData = {
  role: string;
  individual: IndividualDetail;
  household: HouseholdDetail;
};

export function RequestedIndividualDataChange({
  ticket,
  canApproveDataChange,
}: {
  ticket: GrievanceTicketDetail;
  canApproveDataChange: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const confirm = useConfirmation();
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();
  const individualData = {
    ...ticket.ticketDetails.individualData,
  };
  let allApprovedCount = 0;
  const isForApproval = ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL;
  const documents = individualData?.documents || [];
  const documentsToRemove = individualData.documentsToRemove || [];
  const documentsToEdit = individualData.documentsToEdit || [];
  const identities = individualData?.identities || [];
  const identitiesToRemove = individualData.identitiesToRemove || [];
  const identitiesToEdit = individualData.identitiesToEdit || [];
  const paymentChannels = individualData?.paymentChannels || [];
  const paymentChannelsToRemove = individualData.paymentChannelsToRemove || [];
  const paymentChannelsToEdit = individualData.paymentChannelsToEdit || [];
  const flexFields = individualData.flexFields || {};

  delete individualData.flexFields;
  delete individualData.documents;
  delete individualData.identities;
  delete individualData.documentsToRemove;
  delete individualData.documentsToEdit;
  delete individualData.paymentChannels;
  delete individualData.paymentChannelsToRemove;
  delete individualData.paymentChannelsToEdit;
  delete individualData.identitiesToRemove;
  delete individualData.identitiesToEdit;
  delete individualData.previousDocuments;
  delete individualData.previousIdentities;
  delete individualData.previousPaymentChannels;

  const entries = Object.entries(individualData);
  const entriesFlexFields = Object.entries(flexFields);
  allApprovedCount += documents.filter((el) => el.approveStatus).length;
  allApprovedCount += documentsToRemove.filter((el) => el.approveStatus).length;
  allApprovedCount += documentsToEdit.filter((el) => el.approveStatus).length;
  allApprovedCount += identities.filter((el) => el.approveStatus).length;
  allApprovedCount += identitiesToRemove.filter(
    (el) => el.approveStatus,
  ).length;
  allApprovedCount += identitiesToEdit.filter((el) => el.approveStatus).length;
  allApprovedCount += paymentChannels.filter((el) => el.approveStatus).length;
  allApprovedCount += paymentChannelsToRemove.filter(
    (el) => el.approveStatus,
  ).length;
  allApprovedCount += paymentChannelsToEdit.filter(
    (el) => el.approveStatus,
  ).length;
  allApprovedCount += entries.filter(
    ([, value]: [string, { approveStatus: boolean }]) => value.approveStatus,
  ).length;
  allApprovedCount += entriesFlexFields.filter(
    ([, value]: [string, { approveStatus: boolean }]) => value.approveStatus,
  ).length;

  const [isEdit, setEdit] = useState(allApprovedCount === 0);
  const getConfirmationText = (allChangesLength): string =>
    `You approved ${allChangesLength || 0} change${
      allChangesLength === 1 ? '' : 's'
    }, remaining proposed changes will be automatically rejected upon ticket closure.`;

  const { mutateAsync: mutate } = useMutation({
    mutationFn: ({
      individualApproveData,
      approvedDocumentsToCreate,
      approvedDocumentsToRemove,
      approvedDocumentsToEdit,
      approvedIdentitiesToCreate,
      approvedIdentitiesToRemove,
      approvedIdentitiesToEdit,
      approvedPaymentChannelsToCreate,
      approvedPaymentChannelsToRemove,
      approvedPaymentChannelsToEdit,
      flexFieldsApproveData,
    }: {
      individualApproveData: any;
      approvedDocumentsToCreate?: number[];
      approvedDocumentsToRemove?: number[];
      approvedDocumentsToEdit?: number[];
      approvedIdentitiesToCreate?: number[];
      approvedIdentitiesToRemove?: number[];
      approvedIdentitiesToEdit?: number[];
      approvedPaymentChannelsToCreate?: number[];
      approvedPaymentChannelsToRemove?: number[];
      approvedPaymentChannelsToEdit?: number[];
      flexFieldsApproveData?: any;
    }) => {
      const requestBody: GrievanceIndividualDataChangeApprove = {
        individualApproveData,
        approvedDocumentsToCreate,
        approvedDocumentsToRemove,
        approvedDocumentsToEdit,
        approvedIdentitiesToCreate,
        approvedIdentitiesToRemove,
        approvedIdentitiesToEdit,
        approvedPaymentChannelsToCreate,
        approvedPaymentChannelsToRemove,
        approvedPaymentChannelsToEdit,
        flexFieldsApproveData,
      };

      return RestService.restBusinessAreasGrievanceTicketsApproveIndividualDataChangeCreate(
        {
          businessAreaSlug: businessArea,
          id: ticket.id,
          requestBody,
        },
      );
    },
    onSuccess: () => {
      showMessage('Changes Approved');
      queryClient.invalidateQueries({
        queryKey: ['GrievanceTicketDetail', ticket.id],
      });
    },
    onError: (error: any) => {
      if (error?.body?.errors) {
        Object.values(error.body.errors)
          .flat()
          .forEach((msg: string) => {
            showMessage(msg);
          });
      } else {
        showMessage('An error occurred while approving changes');
      }
    },
  });
  const selectedDocuments = [];
  const selectedDocumentsToRemove = [];
  const selectedDocumentsToEdit = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documents?.length; i++) {
    if (documents[i]?.approveStatus) {
      selectedDocuments.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documentsToRemove?.length; i++) {
    if (documentsToRemove[i]?.approveStatus) {
      selectedDocumentsToRemove.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < documentsToEdit?.length; i++) {
    if (documentsToEdit[i]?.approveStatus) {
      selectedDocumentsToEdit.push(i);
    }
  }
  const selectedIdentities = [];
  const selectedIdentitiesToRemove = [];
  const selectedIdentitiesToEdit = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identities?.length; i++) {
    if (identities[i]?.approveStatus) {
      selectedIdentities.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identitiesToRemove?.length; i++) {
    if (identitiesToRemove[i]?.approveStatus) {
      selectedIdentitiesToRemove.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < identitiesToEdit?.length; i++) {
    if (identitiesToEdit[i]?.approveStatus) {
      selectedIdentitiesToEdit.push(i);
    }
  }

  const selectedPaymentChannels = [];
  const selectedPaymentChannelsToRemove = [];
  const selectedPaymentChannelsToEdit = [];
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < paymentChannels?.length; i++) {
    if (paymentChannels[i]?.approveStatus) {
      selectedPaymentChannels.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < paymentChannelsToRemove?.length; i++) {
    if (paymentChannelsToRemove[i]?.approveStatus) {
      selectedPaymentChannelsToRemove.push(i);
    }
  }
  // eslint-disable-next-line no-plusplus
  for (let i = 0; i < paymentChannelsToEdit?.length; i++) {
    if (paymentChannelsToEdit[i]?.approveStatus) {
      selectedPaymentChannelsToEdit.push(i);
    }
  }

  const isHeadOfHousehold =
    ticket.individual?.id === ticket.household?.headOfHousehold?.id;

  const primaryCollectorRolesCount =
    ticket?.individual?.rolesInHouseholds.filter((el) => el.role === 'PRIMARY')
      .length + (isHeadOfHousehold ? 1 : 0);
  const primaryColletorRolesReassignedCount = Object.values(
    ticket.ticketDetails.roleReassignData,
  )?.filter(
    (el: RoleReassignData) => el.role === 'PRIMARY' || el.role === 'HEAD',
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
      identitiesToEdit.length +
      paymentChannels.length +
      paymentChannelsToRemove.length +
      paymentChannelsToEdit.length;

    return allSelected === countAll;
  };

  const getApprovalButton = (allSelected, submitForm): ReactElement => {
    if (areAllApproved(allSelected)) {
      return (
        <Button
          onClick={submitForm}
          variant="contained"
          color="primary"
          disabled={!approveEnabled}
          data-cy="button-approve"
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
        variant="contained"
        color="primary"
        disabled={!approveEnabled}
        data-cy="button-approve"
      >
        {t('Approve')}
      </Button>
    );
  };

  return (
    <Formik
      initialValues={{
        selected: entries
          .filter((row: [string, Record<string, unknown>]) => {
            const valueDetails = mapKeys(row[1], (_v, k) => camelCase(k)) as {
              value: string;
              approveStatus: boolean;
            };
            return valueDetails.approveStatus;
          })
          .map((row) => camelCase(row[0])),
        selectedFlexFields: entriesFlexFields
          .filter((row: [string, Record<string, unknown>]) => {
            const valueDetails = mapKeys(row[1], (_v, k) => camelCase(k)) as {
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
            individualApproveData,
            approvedDocumentsToCreate,
            approvedDocumentsToRemove,
            approvedDocumentsToEdit,
            approvedIdentitiesToCreate,
            approvedIdentitiesToRemove,
            approvedIdentitiesToEdit,
            approvedPaymentChannelsToCreate,
            approvedPaymentChannelsToRemove,
            approvedPaymentChannelsToEdit,
            flexFieldsApproveData,
          });
          const sum = Object.values(values).flat().length;
          setEdit(sum === 0);
        } catch (e) {
          // Error handling is already in the mutation onError callback
        }
      }}
    >
      {({ submitForm, setFieldValue, values }) => {
        const allChangesLength = Object.values(values).flat().length;

        return (
          <ApproveBox>
            <Title>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="h6">Requested Data Change</Typography>
                {shouldShowEditButton(allChangesLength) ? (
                  <Button
                    onClick={() => setEdit(true)}
                    variant="outlined"
                    color="primary"
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
          </ApproveBox>
        );
      }}
    </Formik>
  );
}
