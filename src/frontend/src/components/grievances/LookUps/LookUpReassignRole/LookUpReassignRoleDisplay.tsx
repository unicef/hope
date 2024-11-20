import { Box, Grid } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import * as React from 'react';
import { StyledBox, BlueText, LightGrey } from '../LookUpStyles';
import { useProgramContext } from 'src/programContext';

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
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <StyledBox>
      <Grid container>
        <Grid item>
          <Box display="flex" flexDirection="column">
            <span>
              {`${beneficiaryGroup?.groupLabel} ID`}:
              <BlueText> {selectedHousehold?.unicefId || '-'}</BlueText>
            </span>
            <span>
              {`${beneficiaryGroup?.memberLabel} ID`}:
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
