import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@material-ui/core';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import styled from 'styled-components';
import { grievanceTicketStatusToColor } from '../../../../../utils/utils';
import { BlackLink } from '../../../../core/BlackLink';
import {
  DialogTitleWrapper,
  DialogFooter,
} from '../../../../core/ConfirmationDialog/ConfirmationDialog';
import { FlagTooltip } from '../../../../core/FlagTooltip';
import { Missing } from '../../../../core/Missing';
import { StatusBox } from '../../../../core/StatusBox';
import { ClickableTableRow } from '../../../../core/Table/ClickableTableRow';

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
const StatusContainer = styled.div`
  min-width: 120px;
  max-width: 200px;
`;

interface WarningTooltipTableProps {
  businessArea: string;
}

export const WarningTooltipTable = ({
  businessArea,
}: WarningTooltipTableProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { t } = useTranslation();

  return (
    <>
      <FlagTooltip
        handleClick={() => setDialogOpen(true)}
        message={t(
          'This household is also included in other Payment Plans. Click this icon to view details.',
        )}
      />
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
        maxWidth='md'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            {t('Linked Tickets')}
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
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
                  {/* <UniversalMoment></UniversalMoment> */}
                </TableCell>
                <TableCell align='left'>
                  {/* <UniversalMoment></UniversalMoment>{ */}
                </TableCell>
                <TableCell align='left'>
                  {/* <StatusContainer>
                    <StatusBox
                      status={plan.status}
                      statusToColor={planStatusToColor}
                    />
                  </StatusContainer> */}
                  <TableCell align='left'>
                    <Missing />
                  </TableCell>
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
    </>
  );
};
