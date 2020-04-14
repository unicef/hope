import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { OpenInNewRounded, FileCopy } from '@material-ui/icons';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';

const IconContainer = styled.span`
  button {
    color: #949494;
    min-width: 40px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

const ButtonContainer = styled.span`
  margin: 0 ${({ theme }) => theme.spacing(2)}px;
`;

export interface FinalizedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
}

export function FinalizedTargetPopulationHeaderButtons({
  targetPopulation,
}: FinalizedTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  const [openDuplicate, setOpenDuplicate] = useState(false);
  return (
    <div>
      <IconContainer>
        <Button onClick={() => setOpenDuplicate(true)}>
          <FileCopy />
        </Button>
      </IconContainer>
      <ButtonContainer>
        <Button
          variant='contained'
          color='primary'
          startIcon={<OpenInNewRounded />}
        >
          Open in cashassist
        </Button>
      </ButtonContainer>
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
    </div>
  );
}
