import { ReactElement, useState } from 'react';
import styled from 'styled-components';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { useTranslation } from 'react-i18next';
import { useBaseUrl } from '@hooks/useBaseUrl';
import TableRow from '@mui/material/TableRow';
import TableCell from '@mui/material/TableCell';
import { BlackLink } from '@core/BlackLink';
import { UniversalMoment } from '@core/UniversalMoment';
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
import { PaymentPlanList } from '@restgenerated/models/PaymentPlanList';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';

interface LinkedPaymentPlansModalProps {
  paymentPlan: PaymentPlanList;
  canViewDetails: boolean;
}

const BlackEyeIcon = styled(VisibilityIcon)`
  color: #000;
`;

export const LinkedPaymentPlansModal = ({
  paymentPlan,
  canViewDetails,
}: LinkedPaymentPlansModalProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { baseUrl } = useBaseUrl();

  // TODO (FE-6): once BE-UI-6 lands, replace with the two new separate fields:
  //   [...(paymentPlan.followUpPaymentPlans ?? []), ...(paymentPlan.topUpPaymentPlans ?? [])]
  // Then regenerate types with `bun run generate-rest-api-types-camelcase` and remove this comment.
  const linkedPlans = paymentPlan.followUps || [];

  if (!linkedPlans.length) return null;

  const mappedRows = linkedPlans.map((row) => {
    const linkedPlanPath =
      row.planType === PlanTypeEnum.FOLLOW_UP
        ? `/${baseUrl}/payment-module/followup-payment-plans/${row.id}`
        : `/${baseUrl}/payment-module/payment-plans/${row.id}`;
    return (
      <TableRow key={row.id}>
        <TableCell align="left">
          <BlackLink to={linkedPlanPath}>{row.unicefId}</BlackLink>
        </TableCell>
        <TableCell align="left">
          <UniversalMoment>{row.dispersionStartDate}</UniversalMoment>
        </TableCell>
        <TableCell align="left">
          <UniversalMoment>{row.dispersionEndDate}</UniversalMoment>
        </TableCell>
      </TableRow>
    );
  });

  return (
    <>
      <Box display="flex" alignItems="center" gap={0.5}>
        <span>{linkedPlans.length}</span>
        <IconButton
          color="primary"
          onClick={() => setOpen(true)}
          data-cy="button-eye-linked-plans"
        >
          <BlackEyeIcon />
        </IconButton>
      </Box>
      <Dialog open={open} onClose={() => setOpen(false)} scroll="paper">
        <DialogTitleWrapper>
          <DialogTitle>{t('Linked Payment Plans')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <Box mb={2}>
              <LabelizedField label={t('Original Payment Plan')}>
                {canViewDetails ? (
                  <BlackLink
                    to={`/${baseUrl}/payment-module/payment-plans/${paymentPlan.id}`}
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
                  data-cy="table-cell-linked-payment-plan-id"
                  align="left"
                >
                  {t('Linked Payment Plan ID')}
                </TableCell>
                <TableCell data-cy="table-cell-start-date" align="left">
                  {t('Dispersion Start Date')}
                </TableCell>
                <TableCell data-cy="table-cell-end-date" align="left">
                  {t('Dispersion End Date')}
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
