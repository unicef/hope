import { Box, IconButton } from '@material-ui/core';
import { FileCopy } from '@material-ui/icons';
import React, { useState } from 'react';
import { DuplicateTargetPopulation } from '../../../containers/dialogs/targetPopulation/DuplicateTargetPopulation';
import { TargetPopulationQuery } from '../../../__generated__/graphql';

export interface EnrolledEnrollementHeaderButtonsProps {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canDuplicate: boolean;
}

export const EnrolledEnrollementHeaderButtons = ({
  targetPopulation,
  canDuplicate,
}: EnrolledEnrollementHeaderButtonsProps): React.ReactElement => {
  const [openDuplicate, setOpenDuplicate] = useState(false);
  return (
    <Box display='flex' alignItems='center'>
      {canDuplicate && (
        <IconButton
          onClick={() => setOpenDuplicate(true)}
          data-cy='button-enrollment-duplicate'
        >
          <FileCopy />
        </IconButton>
      )}
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
    </Box>
  );
};
