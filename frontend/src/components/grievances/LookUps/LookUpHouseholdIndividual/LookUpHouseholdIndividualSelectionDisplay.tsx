import { Box, Grid } from '@material-ui/core';
import DeleteIcon from '@material-ui/icons/Delete';
import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { StyledBox, BlueText, DarkGrey } from '../LookUpStyles';

const Types = { household: 'household', individual: 'individual' };

const Flex = styled.div`
  .MuiSvgIcon-root {
    display: flex;
  }
`;

export const LookUpHouseholdIndividualSelectionDisplay = ({
  onValueChange,
  disableUnselectIndividual,
  disableUnselectHousehold,
  selectedHousehold,
  setSelectedHousehold,
  selectedIndividual,
  setSelectedIndividual,
}: {
  onValueChange;
  disableUnselectIndividual: boolean;
  disableUnselectHousehold: boolean;
  selectedHousehold;
  setSelectedHousehold: Function;
  selectedIndividual;
  setSelectedIndividual: Function;
}): React.ReactElement => {
  const { t } = useTranslation();
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
          <Grid container alignItems='center' justifyContent='space-between'>
            <Grid item>
              <Box display='flex'>
                {t('Household ID')}:
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
                      color='inherit'
                      fontSize='small'
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
          <Grid container alignItems='center' justifyContent='space-between'>
            <Grid item>
              <Box display='flex'>
                {t('Individual ID')}:
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
                      color='inherit'
                      fontSize='small'
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
