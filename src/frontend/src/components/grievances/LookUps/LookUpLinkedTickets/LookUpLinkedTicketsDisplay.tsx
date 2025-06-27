import { Box, Grid2 as Grid } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { useLocation } from 'react-router-dom';
import EditIcon from '@mui/icons-material/Edit';
import { useTranslation } from 'react-i18next';
import { BlueText, StyledBox, LightGrey, DarkGrey } from '../LookUpStyles';
import { LinkedTicketIdDisplay } from './LinkedTicketIdDisplay';
import { ReactElement } from 'react';

interface LookUpLinkedTicketsDisplayProps {
  values;
  setLookUpDialogOpen: (open: boolean) => void;
  onValueChange;
  disabled?: boolean;
}

export const LookUpLinkedTicketsDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
  disabled = false,
}: LookUpLinkedTicketsDisplayProps): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;

  const handleRemove = (): void => {
    onValueChange('selectedLinkedTickets', []);
  };
  const renderLinkedTickets = (): ReactElement => {
    if (values.selectedLinkedTickets.length) {
      return values.selectedLinkedTickets.map((id) => (
        <LinkedTicketIdDisplay key={id} ticketId={id} data-cy="linked-ticket" />
      ));
    }
    return <BlueText>-</BlueText>;
  };
  return (
    <StyledBox disabled={disabled}>
      <Grid container justifyContent="space-between">
        <Grid>
          <Box display="flex" flexDirection="column">
            {t('Ticket ID')}:{renderLinkedTickets()}
          </Box>
        </Grid>
        {!isEditTicket && (
          <Grid>
            <Box p={2}>
              <Grid container justifyContent="center" alignItems="center">
                <Grid>
                  <LightGrey>
                    <EditIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => setLookUpDialogOpen(true)}
                      data-cy="button-edit"
                    />
                  </LightGrey>
                </Grid>
                <Grid>
                  <DarkGrey>
                    <DeleteIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => handleRemove()}
                      data-cy="button-delete"
                    />
                  </DarkGrey>
                </Grid>
              </Grid>
            </Box>
          </Grid>
        )}
      </Grid>
    </StyledBox>
  );
};
