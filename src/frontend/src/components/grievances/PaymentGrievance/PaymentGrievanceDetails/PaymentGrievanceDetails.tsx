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
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { useSnackbar } from '@hooks/useSnackBar';
import { GRIEVANCE_TICKET_STATES } from '@utils/constants';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useConfirmation } from '@core/ConfirmationDialog';
import { Title } from '@core/Title';
import { VerifyPaymentGrievance } from '../VerifyPaymentGrievance/VerifyPaymentGrievance';
import { ReactElement } from 'react';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';
import { GrievanceUpdateApproveStatus } from '@restgenerated/models/GrievanceUpdateApproveStatus';
import { RestService } from '@restgenerated/services/RestService';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { showApiErrorMessages } from '@utils/utils';

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
  ticket: GrievanceTicketDetail;
  canApprovePaymentVerification: boolean;
}): ReactElement {
  const { t } = useTranslation();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const { businessArea } = useBaseUrl();
  const confirm = useConfirmation();

  const { mutateAsync: mutate } = useMutation({
    mutationFn: ({
      grievanceTicketId,
      approveStatus,
    }: {
      grievanceTicketId: string;
      approveStatus: boolean;
    }) => {
      const requestBody: GrievanceUpdateApproveStatus = {
        approveStatus,
      };

      return RestService.restBusinessAreasGrievanceTicketsApprovePaymentDetailsCreate(
        {
          businessAreaSlug: businessArea,
          id: grievanceTicketId,
          requestBody,
        },
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: [
          'businessAreasGrievanceTicketsRetrieve',
          businessArea,
          ticket.id,
        ],
      });
    },
    onError: (error: any) => {
      showApiErrorMessages(error, showMessage);
    },
  });

  const approveStatus = ticket.ticketDetails?.approveStatus;
  const oldReceivedAmount = ticket.ticketDetails?.oldReceivedAmount;
  const newReceivedAmount = ticket.ticketDetails?.newReceivedAmount;
  const receivedAmount =
    ticket.ticketDetails?.paymentVerification?.receivedAmount;
  const deliveredQuantity = ticket.paymentRecord?.deliveredQuantity;
  const entitlementQuantity = ticket.paymentRecord?.entitlementQuantity;

  let dialogText = t('Are you sure you want to disapprove this payment?');
  if (!approveStatus) {
    dialogText = t('Are you sure you want to approve this payment?');
  }

  return (
    <StyledBox>
      <Title>
        <Box display="flex" justifyContent="space-between">
          <Typography variant="h6">{t('Payment Details')}</Typography>
          {ticket.status === GRIEVANCE_TICKET_STATES.IN_PROGRESS ? (
            <VerifyPaymentGrievance ticket={ticket} />
          ) : null}
          {canApprovePaymentVerification &&
          ticket.status === GRIEVANCE_TICKET_STATES.FOR_APPROVAL ? (
            <Button
              data-cy="grievance-approve"
              onClick={() =>
                confirm({
                  title: t('Approve'),
                  content: dialogText,
                }).then(async () => {
                  try {
                    await mutate({
                      grievanceTicketId: ticket.id,
                      approveStatus: !approveStatus,
                    });
                    if (approveStatus) {
                      showMessage(t('Changes Disapproved'));
                    }
                    if (!approveStatus) {
                      showMessage(t('Changes Approved'));
                    }
                  } catch (e) {
                    // Error is handled in the mutation's onError callback
                  }
                })
              }
              variant={approveStatus ? 'outlined' : 'contained'}
              color="primary"
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
            <TableCell align="right" />
            <TableCell align="right">{t('Entitlement Value')} ($)</TableCell>
            <TableCell align="right">{t('Delivered Value')} ($)</TableCell>
            <TableCell align="right">{t('Received Value')} ($)</TableCell>
            <TableCell align="right">{t('New Verified Value')} ($)</TableCell>
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
            <TableCell align="right">{entitlementQuantity}</TableCell>
            <TableCell align="right">{deliveredQuantity}</TableCell>
            <TableCell align="right">
              {oldReceivedAmount == null ? receivedAmount : oldReceivedAmount}
            </TableCell>
            <TableCell align="right">{newReceivedAmount ?? 0}</TableCell>
          </TableRow>
        </TableBody>
      </StyledTable>
    </StyledBox>
  );
}
