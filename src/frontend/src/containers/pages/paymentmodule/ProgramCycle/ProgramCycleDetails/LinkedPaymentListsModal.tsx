import type { ReactElement } from 'react';
import { useState } from 'react';
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
import type { PaymentListList } from '@restgenerated/models/PaymentListList';
import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';

interface LinkedPaymentListsModalProps {
  paymentList: PaymentListList;
  canViewDetails: boolean;
}

export const LinkedPaymentListsModal = ({
  paymentList,
  canViewDetails,
}: LinkedPaymentListsModalProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { baseUrl } = useBaseUrl();

  // TODO (FE-6): once BE-UI-6 lands, replace with the two new separate fields:
  //   [...(paymentList.followUpPaymentLists ?? []), ...(paymentList.topUpPaymentLists ?? [])]
  // Then regenerate types with `bun run generate-rest-api-types-camelcase` and remove this comment.
  const linkedPlans = paymentList.followUps || [];

  if (!linkedPlans.length) return null;

  const mappedRows = linkedPlans.map((row) => {
    const linkedPlanPath =
      row.planType === PlanTypeEnum.FOLLOW_UP
        ? `/${baseUrl}/payment-module/followup-payment-lists/${row.id}`
        : `/${baseUrl}/payment-module/payment-lists/${row.id}`;
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
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
        }}
      >
        <span>{linkedPlans.length}</span>
        <IconButton
          color="primary"
          onClick={(e) => {
            e.stopPropagation();
            setOpen(true);
          }}
          data-cy="button-eye-linked-plans"
        >
          <VisibilityIcon />
        </IconButton>
      </Box>
      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        onClick={(e) => e.stopPropagation()}
        scroll="paper"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Linked Payment Lists')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <Box
              sx={{
                mb: 2,
              }}
            >
              <LabelizedField label={t('Original Payment List')}>
                {canViewDetails ? (
                  <BlackLink
                    to={`/${baseUrl}/payment-module/payment-lists/${paymentList.id}`}
                  >
                    {paymentList.unicefId}
                  </BlackLink>
                ) : (
                  paymentList.unicefId
                )}
              </LabelizedField>
            </Box>
          </DialogDescription>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell
                  data-cy="table-cell-linked-payment-list-id"
                  align="left"
                >
                  {t('Linked Payment List ID')}
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
            <Button
              data-cy="button-close"
              onClick={(e) => {
                e.stopPropagation();
                setOpen(false);
              }}
            >
              {t('Close')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
