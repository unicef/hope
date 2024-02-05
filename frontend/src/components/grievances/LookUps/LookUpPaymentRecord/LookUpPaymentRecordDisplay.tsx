import { Box, Grid } from '@mui/material';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { BlueText, DarkGrey, LightGrey, StyledBox } from '../LookUpStyles';

export const LookUpPaymentRecordDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
  disabled,
}: {
  values;
  setLookUpDialogOpen;
  onValueChange;
  disabled?;
}): React.ReactElement => {
  const { t } = useTranslation();
  const handleRemove = (): void => {
    onValueChange('selectedPaymentRecords', []);
  };
  const renderPaymentRecords = (): React.ReactElement => {
    if (values.selectedPaymentRecords.length) {
      return values.selectedPaymentRecords.map((record) => (
        <BlueText>{record.caId}</BlueText>
      ));
    }
    return <BlueText>-</BlueText>;
  };
  return (
    <StyledBox disabled={disabled}>
      <Grid container>
        <Grid item>
          <Box display="flex" flexDirection="column">
            {t('Payment ID')}:{renderPaymentRecords()}
          </Box>
        </Grid>
        {disabled || (
          <Grid item>
            <Box p={2}>
              <Grid container justifyContent="center" alignItems="center">
                <Grid item>
                  <LightGrey>
                    <EditIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => setLookUpDialogOpen(true)}
                    />
                  </LightGrey>
                </Grid>
                <Grid item>
                  <DarkGrey>
                    <DeleteIcon
                      color="inherit"
                      fontSize="small"
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
