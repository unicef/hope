import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import { TargetPopulationNode } from '../../../__generated__/graphql';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { FinalizeTargetPopulation } from '../../dialogs/targetPopulation/FinalizeTargetPopulation';

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

export interface ApprovedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationNode;
}

export function ApprovedTargetPopulationHeaderButtons({
  targetPopulation,
}: ApprovedTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const [openFinalize, setOpenFinalize] = useState(false);
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
          onClick={() => setOpenFinalize(true)}
        >
          Finalize
        </Button>
      </ButtonContainer>
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
      <FinalizeTargetPopulation open={openFinalize} setOpen={setOpenFinalize} />
    </div>
  );
}
