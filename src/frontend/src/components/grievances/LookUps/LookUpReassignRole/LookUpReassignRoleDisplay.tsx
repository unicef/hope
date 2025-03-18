import EditIcon from '@mui/icons-material/Edit';
import { Box, Grid2 as Grid } from '@mui/material';
import { ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';
import { BlueText, LightGrey, StyledBox } from '../LookUpStyles';

export function LookUpReassignRoleDisplay({
  selectedHousehold,
  selectedIndividual,
  setLookUpDialogOpen,
  disabled,
}: {
  selectedHousehold;
  //TODO: add correct type
  // selectedHousehold: HouseholdDetail;
  selectedIndividual;
  setLookUpDialogOpen;
  disabled?: boolean;
}): ReactElement {
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiary_group;

  return (
    <StyledBox>
      <Grid container>
        <Grid>
          <Box display="flex" flexDirection="column">
            <span>
              {`${beneficiaryGroup?.group_label} ID`}:
              <BlueText> {selectedHousehold?.unicef_id || '-'}</BlueText>
            </span>
            <span>
              {`${beneficiaryGroup?.member_label} ID`}:
              <BlueText>{selectedIndividual?.unicefId || '-'}</BlueText>
            </span>
          </Box>
        </Grid>
        <Grid>
          <Box p={2}>
            <Grid container justifyContent="center" alignItems="center">
              <Grid>
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
