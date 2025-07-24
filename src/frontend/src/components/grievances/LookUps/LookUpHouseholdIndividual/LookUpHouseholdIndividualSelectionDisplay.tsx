import DeleteIcon from '@mui/icons-material/Delete';
import { Box, Grid2 as Grid } from '@mui/material';
import * as React from 'react';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { BlueText, DarkGrey, StyledBox } from '../LookUpStyles';
import { HouseholdDetail } from '@restgenerated/models/HouseholdDetail';

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
  selectedHousehold: HouseholdDetail;
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
  const { selectedProgram, isSocialDctType } = useProgramContext();
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
      {!isSocialDctType && (
        <Grid size={{ xs: 4 }}>
          <StyledBox disabled={disableUnselectHousehold}>
            <Grid container alignItems="center" justifyContent="space-between">
              <Grid>
                <Box display="flex">
                  {`${beneficiaryGroup?.groupLabel} ID`}:
                  <BlueText>
                    &ensp;
                    {selectedHousehold?.unicefId || '-'}
                  </BlueText>
                </Box>
              </Grid>
              {!disableUnselectHousehold && selectedHousehold?.unicefId && (
                <Grid>
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
      )}
      <Grid size={{ xs: 4 }}>
        <StyledBox disabled={disableUnselectIndividual}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid>
              <Box display="flex">
                {`${beneficiaryGroup?.memberLabel} ID`}:
                <BlueText>
                  &ensp;
                  {selectedIndividual?.unicefId || '-'}
                </BlueText>
              </Box>
            </Grid>
            {!disableUnselectIndividual && selectedIndividual?.unicefId && (
              <Grid>
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
