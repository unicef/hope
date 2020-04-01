import React from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { OpenInNewRounded } from '@material-ui/icons';
import { TargetPopulationNode } from '../../../__generated__/graphql';

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface FinalizedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
}

export function FinalizedTargetPopulationHeaderButtons({
  targetPopulation,
}: FinalizedTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  return (
    <div>
      <ButtonContainer>
        <Button
          variant='contained'
          color='primary'
          startIcon={<OpenInNewRounded />}
        >
          Open in cashassist
        </Button>
      </ButtonContainer>
    </div>
  );
}