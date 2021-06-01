import React, { useState } from 'react';
import styled from 'styled-components';
import { Button } from '@material-ui/core';
import OpenInNewRoundedIcon from '@material-ui/icons/OpenInNewRounded';
import { FileCopy } from '@material-ui/icons';
import {
  TargetPopulationNode,
  useCashAssistUrlPrefixQuery,
} from '../../../__generated__/graphql';
import { DuplicateTargetPopulation } from '../../dialogs/targetPopulation/DuplicateTargetPopulation';
import { LoadingComponent } from '../../../components/LoadingComponent';

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
  canDuplicate: boolean;
}

export function FinalizedTargetPopulationHeaderButtons({
  targetPopulation,
  canDuplicate,
}: FinalizedTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const { data, loading } = useCashAssistUrlPrefixQuery();
  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <div>
      {canDuplicate && (
        <IconContainer>
          <Button onClick={() => setOpenDuplicate(true)}>
            <FileCopy />
          </Button>
        </IconContainer>
      )}
      <ButtonContainer>
        <Button
          variant='contained'
          color='primary'
          component='a'
          disabled={!targetPopulation.caHashId}
          target="_blank"
          href={`${data.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_targetpopulation&id=${targetPopulation.caHashId}`}
          startIcon={<OpenInNewRoundedIcon />}
        >
          Open in CashAssist
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
