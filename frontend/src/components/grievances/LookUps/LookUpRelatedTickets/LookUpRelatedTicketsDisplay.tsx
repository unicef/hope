import { Box, Grid } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BlueText, StyledBox, LightGrey, DarkGrey } from '../LookUpStyles';
import { RelatedTicketIdDisplay } from './RelatedTicketIdDisplay';

export const LookUpRelatedTicketsDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
}): React.ReactElement => {
  const { t } = useTranslation();
  const handleRemove = (): void => {
    onValueChange('selectedRelatedTickets', []);
  };
  const renderRelatedTickets = (): React.ReactElement => {
    if (values.selectedRelatedTickets.length) {
      return values.selectedRelatedTickets.map((id) => (
        <RelatedTicketIdDisplay ticketId={id} />
      ));
    }
    return <BlueText>-</BlueText>;
  };
  return (
    <StyledBox>
      <Grid container justify='space-between'>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            {t('Ticket ID')}:{renderRelatedTickets()}
          </Box>
        </Grid>
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
      </Grid>
    </StyledBox>
  );
};
