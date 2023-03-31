import { Box, Grid } from '@material-ui/core';
import DeleteIcon from '@material-ui/icons/Delete';
import { useLocation } from 'react-router-dom';
import EditIcon from '@material-ui/icons/Edit';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BlueText, StyledBox, LightGrey, DarkGrey } from '../LookUpStyles';
import { LinkedTicketIdDisplay } from './LinkedTicketIdDisplay';

export const LookUpLinkedTicketsDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
}): React.ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const isEditTicket = location.pathname.indexOf('edit-ticket') !== -1;

  const handleRemove = (): void => {
    onValueChange('selectedLinkedTickets', []);
  };
  const renderLinkedTickets = (): React.ReactElement => {
    if (values.selectedLinkedTickets.length) {
      return values.selectedLinkedTickets.map((id) => (
        <LinkedTicketIdDisplay ticketId={id} />
      ));
    }
    return <BlueText>-</BlueText>;
  };
  return (
    <StyledBox>
      <Grid container justify='space-between'>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            {t('Ticket ID')}:{renderLinkedTickets()}
          </Box>
        </Grid>
        {!isEditTicket && (
          <Grid item>
            <Box p={2}>
              <Grid container justify='center' alignItems='center'>
                <Grid item>
                  <LightGrey>
                    <EditIcon
                      color='inherit'
                      fontSize='small'
                      onClick={() => setLookUpDialogOpen(true)}
                    />
                  </LightGrey>
                </Grid>
                <Grid item>
                  <DarkGrey>
                    <DeleteIcon
                      color='inherit'
                      fontSize='small'
                      onClick={() => handleRemove()}
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
