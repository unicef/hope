import { Box, Button } from '@mui/material';
import { FileCopy } from '@mui/icons-material';
import { ReactElement, useState } from 'react';
import styled from 'styled-components';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';

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

export interface FinalizedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationDetail;
  canDuplicate: boolean;
}

export function FinalizedTargetPopulationHeaderButtons({
  targetPopulation,
  canDuplicate,
}: FinalizedTargetPopulationHeaderButtonsPropTypes): ReactElement {
  const [openDuplicate, setOpenDuplicate] = useState(false);

  return (
    <Box display="flex" alignItems="center">
      {canDuplicate && (
        <IconContainer>
          <Button onClick={() => setOpenDuplicate(true)}>
            <FileCopy />
          </Button>
        </IconContainer>
      )}
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
    </Box>
  );
}
