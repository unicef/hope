import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@material-ui/core';
import React, { Dispatch, SetStateAction, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { decodeIdString, grievanceTicketStatusToColor } from '../../../../../utils/utils';
import { BlackLink } from '../../../../../components/core/BlackLink';
import { Missing } from '../../../../../components/core/Missing';
import { ClickableTableRow } from '../../../../../components/core/Table/ClickableTableRow';
import { WarningTooltip } from '../../../../../components/core/WarningTooltip';
import { LabelizedField } from '../../../../../components/core/LabelizedField';
import { DialogFooter } from '../../../../dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../dialogs/DialogTitleWrapper';
import { PaymentPlanQuery, PaymentQuery } from '../../../../../__generated__/graphql';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;
const StyledTable = styled(Table)`
  min-width: 100px;
`;
const Bold = styled.div`
  font-weight: bold;
  padding: 0 5px;
`;

const GreyBox = styled(Box)`
  background-color: #f3f3f3;
`;

interface WarningTooltipTableProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  payment: PaymentQuery['payment'];
  setDialogOpen: (dialogOpen: boolean) => void;
}

export const WarningTooltipTable = ({
  paymentPlan,
  payment,
  setDialogOpen,
}: WarningTooltipTableProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <Dialog
      open={!!payment}
      onClose={() => setDialogOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
      maxWidth='md'
    >
      <DialogTitleWrapper>
        <DialogTitle id='scroll-dialog-title'>{t('Warning')}</DialogTitle>
      </DialogTitleWrapper>
      <DialogContent>
        <Box mt={4} mb={2} display='flex'>
          {t('Payment Plan ID')} <Bold>{decodeIdString(paymentPlan.id)}</Bold> {t('details')}:
        </Box>
        <GreyBox p={3}>
          <Grid container>
            <Grid item xs={6}>
              <LabelizedField label={t('Start Date')} value={new Date(paymentPlan.startDate).toLocaleDateString()} />
            </Grid>
            <Grid item xs={6}>
              <LabelizedField label={t('End Date')} value={new Date(paymentPlan.endDate).toLocaleDateString()} />
            </Grid>
          </Grid>
        </GreyBox>
        <Box mt={10} mb={10} display='flex'>
          {t('Household ID')} <Bold>Some ID 2222</Bold>{' '}
          {t('is also included in the following Payment Plans')}:
        </Box>
        <StyledTable>
          <TableHead>
            <TableRow>
              <TableCell align='left'>{t('Payment Plan ID')}</TableCell>
              <TableCell align='left'>{t('Start Date')}</TableCell>
              <TableCell align='left'>{t('End Date')}</TableCell>
              <TableCell align='left'>{t('Status')}</TableCell>
              <TableCell align='left'>{t('Payment ID')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <ClickableTableRow hover onClick={undefined}>
              <TableCell align='left'>
                <Missing />
              </TableCell>
              <TableCell align='left'>
                <Missing />
              </TableCell>
              <TableCell align='left'>
                <Missing />
              </TableCell>
              <TableCell align='left'>
                <Missing />
                {/* <StatusContainer>
                    <StatusBox
                      status={plan.status}
                      statusToColor={planStatusToColor}
                    />
                  </StatusContainer> */}
              </TableCell>
              <TableCell align='left'>
                <Missing />
              </TableCell>
            </ClickableTableRow>
          </TableBody>
        </StyledTable>
      </DialogContent>
      <DialogFooter>
        <DialogActions>
          <Button
            onClick={(e) => {
              e.stopPropagation();
              setDialogOpen(false);
            }}
          >
            {t('CANCEL')}
          </Button>
        </DialogActions>
      </DialogFooter>
    </Dialog>
  );
};
