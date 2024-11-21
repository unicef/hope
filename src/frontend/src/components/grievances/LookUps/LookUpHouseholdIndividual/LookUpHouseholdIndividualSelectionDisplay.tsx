import DeleteIcon from '@mui/icons-material/Delete';
import { Box, Grid } from '@mui/material';
import * as React from 'react';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { BlueText, DarkGrey, StyledBox } from '../LookUpStyles';

const Types = { household: 'household', individual: 'individual' };

const Flex = styled.div`
  .MuiSvgIcon-root {
    display: flex;
  }
`;
interface LookUpHouseholdIndividualSelectionDisplayProps {
  onValueChange;
  disableUnselectIndividual: boolean;
  disableUnselectHousehold: boolean;
  selectedHousehold;
  setSelectedHousehold: (value) => void;
  selectedIndividual;
  setSelectedIndividual: (value) => void;
}

export const LookUpHouseholdIndividualSelectionDisplay = ({
  onValueChange,
  disableUnselectIndividual,
  disableUnselectHousehold,
  selectedHousehold,
  setSelectedHousehold,
  selectedIndividual,
  setSelectedIndividual,
}: LookUpHouseholdIndividualSelectionDisplayProps): React.ReactElement => {
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const handleRemove = (type): void => {
    if (type === Types.household) {
      onValueChange('selectedHousehold', null);
      onValueChange('selectedIndividual', null);
      setSelectedHousehold(null);
      setSelectedIndividual(null);
    } else {
      onValueChange('selectedIndividual', null);
      setSelectedIndividual(null);
    }
    onValueChange('identityVerified', false);
  };
  return (
    <Grid container spacing={5}>
      <Grid item xs={4}>
        <StyledBox disabled={disableUnselectHousehold}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid item>
              <Box display="flex">
                {`${beneficiaryGroup?.groupLabel} ID`}:
                <BlueText>
                  &ensp;
                  {selectedHousehold?.unicefId || '-'}
                </BlueText>
              </Box>
            </Grid>
            {!disableUnselectHousehold && selectedHousehold?.unicefId && (
              <Grid item>
                <DarkGrey>
                  <Flex>
                    <DeleteIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => handleRemove(Types.household)}
                    />
                  </Flex>
                </DarkGrey>
              </Grid>
            )}
          </Grid>
        </StyledBox>
      </Grid>
      <Grid item xs={4}>
        <StyledBox disabled={disableUnselectIndividual}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid item>
              <Box display="flex">
                {`${beneficiaryGroup?.memberLabel} ID`}:
                <BlueText>
                  &ensp;
                  {selectedIndividual?.unicefId || '-'}
                </BlueText>
              </Box>
            </Grid>
            {!disableUnselectIndividual && selectedIndividual?.unicefId && (
              <Grid item>
                <DarkGrey>
                  <Flex>
                    <DeleteIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => handleRemove(Types.individual)}
                    />
                  </Flex>
                </DarkGrey>
              </Grid>
            )}
          </Grid>
        </StyledBox>
      </Grid>
    </Grid>
  );
};
