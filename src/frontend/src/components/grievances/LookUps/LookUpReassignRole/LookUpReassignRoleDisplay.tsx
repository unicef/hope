import EditIcon from '@mui/icons-material/Edit';
import { Box, Grid2 as Grid } from '@mui/material';
import { ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';
import { BlueText, LightGrey, StyledBox } from '../LookUpStyles';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

export function LookUpReassignRoleDisplay({
  selectedHousehold,
  selectedIndividual,
  setLookUpDialogOpen,
  disabled,
}: {
  selectedHousehold?:
    | GrievanceTicketDetail['household']
    | GrievanceTicketDetail['individual']['rolesInHouseholds'][number]['household'];
  selectedIndividual;
  setLookUpDialogOpen;
  disabled?: boolean;
}): ReactElement {
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  return (
    <StyledBox>
      <Grid container>
        <Grid>
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
