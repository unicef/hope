import { Box, Grid } from '@material-ui/core';
import DeleteIcon from '@material-ui/icons/Delete';
import EditIcon from '@material-ui/icons/Edit';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { StyledBox, BlueText, LightGrey, DarkGrey } from '../LookUpStyles';

export const LookUpHouseholdIndividualDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
  disabled,
  setSelectedIndividual,
  setSelectedHousehold,
}: {
  values;
  setLookUpDialogOpen;
  onValueChange;
  disabled?: boolean;
  selectedIndividual?;
  selectedHousehold?;
  setSelectedIndividual?;
  setSelectedHousehold?;
}): React.ReactElement => {
  const { t } = useTranslation();
  const handleRemove = (): void => {
    onValueChange('selectedHousehold', null);
    setSelectedHousehold(null);
    onValueChange('selectedIndividual', null);
    setSelectedIndividual(null);
    onValueChange('identityVerified', false);
  };
  return (
    <StyledBox disabled={disabled}>
      <Grid container>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <span>
              {t('Household ID')}:
              <BlueText> {values?.selectedHousehold?.unicefId || '-'}</BlueText>
            </span>
            <span>
              {t('Individual ID')}:
              <BlueText>{values?.selectedIndividual?.unicefId || '-'}</BlueText>
            </span>
          </Box>
        </Grid>
        {!disabled && (
          <Grid item>
            <Box p={2}>
              <Grid container justifyContent='center' alignItems='center'>
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
