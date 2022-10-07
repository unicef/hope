import {
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@material-ui/core';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '../../../../utils/constants';
import {
  GrievanceTicketDocument,
  GrievanceTicketNode,
  useApprovePaymentDetailsMutation,
} from '../../../../__generated__/graphql';
import { useConfirmation } from '../../../core/ConfirmationDialog';
import { Title } from '../../../core/Title';
import { VerifyPaymentGrievance } from '../VerifyPaymentGrievance/VerifyPaymentGrievance';

const StyledBox = styled(Paper)`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;
export const StyledTable = styled(Table)`
  min-width: 100px;
`;
const GreenIcon = styled.div`
  color: #28cb15;
`;

export function PaymentGrievanceDetails({
  ticket,
  canApprovePaymentVerification,
}: {
  ticket: GrievanceTicketNode;
  canApprovePaymentVerification: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const [mutate] = useApprovePaymentDetailsMutation();
  const confirm = useConfirmation();
  const {
    approveStatus,
    newReceivedAmount,
    paymentVerification: {
      receivedAmount,
    },
  } = ticket.paymentVerificationTicketDetails;

  const deliveredQuantity = ticket.paymentRecord?.deliveredQuantity;

  let dialogText = t('Are you sure you want to disapprove this payment?');
  if (!approveStatus) {
    dialogText = t('Are you sure you want to approve this payment?');
  }

  return (
    <StyledBox>
      <Title>
        <Box display='flex' justifyContent='space-between'>
          <Typography variant='h6'>{t('Payment Details')}</Typography>
          {ticket.status === GRIEVANCE_TICKET_STATES.IN_PROGRESS ? (
            <VerifyPaymentGrievance ticket={ticket} />
          ) : null}
          {canApprovePaymentVerification &&
          ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL ? (
            <Button
              onClick={() =>
                confirm({
                  title: t('Approve'),
                  content: dialogText,
                }).then(async () => {
                  try {
                    await mutate({
                      variables: {
                        grievanceTicketId: ticket.id,
                        approveStatus: !approveStatus,
                      },
                      refetchQueries: () => [
                        {
                          query: GrievanceTicketDocument,
                          variables: { id: ticket.id },
                        },
                      ],
                    });
                    if (approveStatus) {
                      showMessage(t('Changes Disapproved'));
                    }
                    if (!approveStatus) {
                      showMessage(t('Changes Approved'));
                    }
                  } catch (e) {
                    e.graphQLErrors.map((x) => showMessage(x.message));
                  }
                })
              }
              variant={approveStatus ? 'outlined' : 'contained'}
              color='primary'
              disabled={ticket.status !== GRIEVANCE_TICKET_STATES.FOR_APPROVAL}
            >
              {approveStatus ? t('Disapprove') : t('Approve')}
            </Button>
          ) : null}
        </Box>
      </Title>
      <StyledTable>
        <TableHead>
          <TableRow>
            <TableCell align='right' />
            <TableCell align='right'>{t('Delivered Value')} ($)</TableCell>
            <TableCell align='right'>{t('Received Value')} ($)</TableCell>
            <TableCell align='right'>{t('New Verified Value')} ($)</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell>
              {approveStatus ? (
                <GreenIcon>
                  <CheckCircleIcon />
                </GreenIcon>
              ) : null}
            </TableCell>
            <TableCell align='right'>{deliveredQuantity}</TableCell>
            <TableCell align='right'>{receivedAmount}</TableCell>
            <TableCell align='right'>{newReceivedAmount}</TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </StyledBox>
  );
}
