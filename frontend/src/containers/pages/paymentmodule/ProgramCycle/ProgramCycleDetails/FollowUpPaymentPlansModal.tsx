import React, { useState } from 'react';
import { PaymentPlanQuery } from '@generated/graphql';
import styled from 'styled-components';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import { BlackLink } from '@core/BlackLink';
import { UniversalMoment } from '@core/UniversalMoment';
import { Missing } from '@core/Missing';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { LabelizedField } from '@core/LabelizedField';
import { StyledTable } from '@components/grievances/GrievancesApproveSection/ApproveSectionStyles';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import { DialogFooter } from '@containers/dialogs/DialogFooter';

interface FollowUpPaymentPlansModalProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canViewDetails: boolean;
}

const BlackEyeIcon = styled(VisibilityIcon)`
  color: #000;
`;

export const FollowUpPaymentPlansModal = ({
  paymentPlan,
  canViewDetails,
}: FollowUpPaymentPlansModalProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { baseUrl } = useBaseUrl();

  const followUps =
    paymentPlan.followUps?.edges?.map((edge) => edge?.node) || [];

  if (!followUps.length) return null;

  const mappedRows = followUps.map((row) => (
    <TableRow key={row.id}>
      <TableCell align="left">
        <BlackLink
          to={`/${baseUrl}/payment-module/followup-payment-plans/${row.id}`}
        >
          {row.unicefId}
        </BlackLink>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{row.dispersionStartDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <UniversalMoment>{row.dispersionEndDate}</UniversalMoment>
      </TableCell>
      <TableCell align="left">
        <Missing />
      </TableCell>
      <TableCell align="left">
        <Missing />
      </TableCell>
    </TableRow>
  ));

  return (
    <>
      <IconButton
        color="primary"
        onClick={() => setOpen(true)}
        data-cy="button-eye-follow-ups"
      >
        <BlackEyeIcon />
      </IconButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll="paper">
        <DialogTitleWrapper>
          <DialogTitle>{t('Follow-up Payment Plans')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <Box mb={2}>
              <LabelizedField label={t('Original Payment Plan')}>
                {canViewDetails ? (
                  <BlackLink
                    to={`/${baseUrl}/payment-module/payment-plans
                /${paymentPlan.id}`}
                  >
                    {paymentPlan.unicefId}
                  </BlackLink>
                ) : (
                  paymentPlan.unicefId
                )}
              </LabelizedField>
            </Box>
          </DialogDescription>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell
                  data-cy="table-cell-follow-up-payment-plan-id"
                  align="left"
                >
                  {t('Follow-up Payment Plan ID')}
                </TableCell>
                <TableCell data-cy="table-cell-start-date" align="left">
                  {t('Dispersion Start Date')}
                </TableCell>
                <TableCell data-cy="table-cell-end-date" align="left">
                  {t('Dispersion End Date')}
                </TableCell>
                <TableCell
                  data-cy="table-cell-reconciliation-status"
                  align="left"
                >
                  {t('Reconciliation Status')}
                </TableCell>
                <TableCell data-cy="table-cell-payment-id" align="left">
                  {t('Payment ID')}
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>{mappedRows}</TableBody>
          </StyledTable>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button data-cy="button-close" onClick={() => setOpen(false)}>
              {t('Close')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
