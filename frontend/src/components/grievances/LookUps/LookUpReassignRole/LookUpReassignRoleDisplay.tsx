import { Box, Grid } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { StyledBox, BlueText, LightGrey } from '../LookUpStyles';

export const LookUpReassignRoleDisplay = ({
  values,
  setLookUpDialogOpen,
  disabled,
}: {
  values;
  setLookUpDialogOpen;
  disabled?: boolean;
}): React.ReactElement => {
  const { t } = useTranslation();
  return (
    <StyledBox>
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
        <Grid item>
          <Box p={2}>
            <Grid container justify='center' alignItems='center'>
              <Grid item>
                {disabled ? null : (
                  <LightGrey>
                    <EditIcon
                      color='inherit'
                      fontSize='small'
                      onClick={() => setLookUpDialogOpen(true)}
                    />
                  </LightGrey>
                )}
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </StyledBox>
  );
};
