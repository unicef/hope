import { Box, Grid } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { StyledBox, BlueText, LightGrey } from '../LookUpStyles';

export function LookUpReassignRoleDisplay({
  selectedHousehold,
  selectedIndividual,
  setLookUpDialogOpen,
  disabled,
}: {
  selectedHousehold;
  selectedIndividual;
  setLookUpDialogOpen;
  disabled?: boolean;
}): React.ReactElement {
  const { t } = useTranslation();
  return (
    <StyledBox>
      <Grid container>
        <Grid item>
          <Box display="flex" flexDirection="column">
            <span>
              {t('Household ID')}:
              <BlueText> {selectedHousehold?.unicefId || '-'}</BlueText>
            </span>
            <span>
              {t('Individual ID')}:
              <BlueText>{selectedIndividual?.unicefId || '-'}</BlueText>
            </span>
          </Box>
        </Grid>
        <Grid item>
          <Box p={2}>
            <Grid container justifyContent="center" alignItems="center">
              <Grid item>
                {disabled ? null : (
                  <LightGrey>
                    <EditIcon
                      color="inherit"
                      fontSize="small"
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
}
