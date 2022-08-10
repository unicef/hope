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
  values,
  onValueChange,
  disabled,
  setSelectedIndividual,
  setSelectedHousehold,
}: {
  values;
  onValueChange;
  disabled?: boolean;
  selectedIndividual?;
  selectedHousehold?;
  setSelectedIndividual?;
  setSelectedHousehold?;
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
        <StyledBox disabled={disabled}>
          <Grid container alignItems='center' justify='space-between'>
            <Grid item>
              <Box display='flex'>
                {t('Household ID')}:
                <BlueText>
                  &ensp;
                  {values?.selectedHousehold?.unicefId || '-'}
                </BlueText>
              </Box>
            </Grid>
            {!disabled && values?.selectedHousehold?.unicefId && (
              <Grid item>
                <DarkGrey>
                  <Flex>
                    <DeleteIcon
                      display='flex'
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
        <StyledBox disabled={disabled}>
          <Grid container alignItems='center' justify='space-between'>
            <Grid item>
              <Box display='flex'>
                {t('Individual ID')}:
                <BlueText>
                  &ensp;
                  {values?.selectedIndividual?.unicefId || '-'}
                </BlueText>
              </Box>
            </Grid>
            {!disabled && values?.selectedIndividual?.unicefId && (
              <Grid item>
                <DarkGrey>
                  <Flex>
                    <DeleteIcon
                      display='flex'
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
