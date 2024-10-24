import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  Typography,
} from '@mui/material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Dialog } from '@containers/dialogs/Dialog';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { AllGrievanceTicketQuery } from '@generated/graphql';
import { useProgramContext } from '../../../../programContext';
import { Bold } from '@components/core/Bold';

export const StyledLink = styled.div`
  color: #000;
  text-decoration: underline;
  cursor: pointer;
  display: flex;
  align-content: center;
`;
const StyledTable = styled(Table)`
  min-width: 400px;
  max-width: 800px;
`;
const StyledDialog = styled(Dialog)`
  max-height: 800px;
`;

interface BulkBaseModalProps {
  selectedTickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][];
  icon: React.ReactElement;
  buttonTitle: string;
  title: string;
  children?: React.ReactNode;
  onSave: (
    tickets: AllGrievanceTicketQuery['allGrievanceTicket']['edges'][number]['node'][],
  ) => Promise<void>;
  disabledSave?: boolean;
}

export function BulkBaseModal({
  selectedTickets,
  icon,
  buttonTitle,
  title,
  children,
  onSave,
  disabledSave,
}: BulkBaseModalProps): React.ReactElement {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { t } = useTranslation();
  const { isActiveProgram } = useProgramContext();

  const renderButton = (): React.ReactElement => (
    <Button
      variant="outlined"
      color="primary"
      startIcon={icon}
      disabled={!selectedTickets.length || !isActiveProgram}
      onClick={() => setDialogOpen(true)}
      data-cy={`button-${buttonTitle}`}
    >
      {buttonTitle}
    </Button>
  );
  const onAccept = async (): Promise<void> => {
    try {
      await onSave(selectedTickets);
      setDialogOpen(false);
    } catch (e) {
      // handled by inner function
    }
  };

  return (
    <>
      {renderButton()}
      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle id="scroll-dialog-title">{title}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <Box mt={2} mb={6}>
            <StyledTable>
              <Typography>
                {t('Tickets ID')}:{' '}
                <Bold data-cy="selected-tickets">
                  {selectedTickets.map((ticket) => ticket.unicefId).join(', ')}
                </Bold>
              </Typography>
            </StyledTable>
          </Box>
          <StyledTable>
            <TableBody data-cy="dropdown">{children}</TableBody>
          </StyledTable>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button data-cy="button-cancel"
              onClick={() => {
                setDialogOpen(false);
              }}
            >
              {t('CANCEL')}
            </Button>
            <Button
              data-cy="button-save"
              variant="contained"
              color="primary"
              onClick={onAccept}
              disabled={disabledSave}
            >
              {t('SAVE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </StyledDialog>
    </>
  );
}
