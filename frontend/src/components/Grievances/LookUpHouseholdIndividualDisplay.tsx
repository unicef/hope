import { Box, Button, Grid } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import EditIcon from '@material-ui/icons/Edit';
import DeleteIcon from '@material-ui/icons/Delete';

const StyledBox = styled.div`
  border: 1.5px solid #043e91;
  border-radius: 5px;
  font-size: 16px;
  padding: 16px;
  background-color: #f7faff;
`;

const BlueText = styled.span`
  color: #033f91;
  font-weight: 500;
  font-size: 16px;
`;

const LightGrey = styled.span`
  color: #949494;
  margin-right: 10px;
`;
const DarkGrey = styled.span`
  color: #757575;
`;

export const LookUpHouseholdIndividualDisplay = ({
  values,
  setLookUpDialogOpen,
  onValueChange,
}): React.ReactElement => {
  const handleRemove = (): void => {
    onValueChange('selectedHousehold', '');
    onValueChange('selectedIndividual', '');
  };
  return (
    <StyledBox>
      <Grid container>
        <Grid item>
          <Box display='flex' flexDirection='column'>
            <span>
              Household ID:
              <BlueText>{values.selectedHousehold || '-'}</BlueText>
            </span>
            <span>
              Individual ID:
              <BlueText>{values.selectedIndividual || '-'}</BlueText>
            </span>
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
