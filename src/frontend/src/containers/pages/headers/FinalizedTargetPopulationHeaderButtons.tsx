import { Box, Button } from '@mui/material';
import { FileCopy } from '@mui/icons-material';
import OpenInNewRoundedIcon from '@mui/icons-material/OpenInNewRounded';
import * as React from 'react';
import { useState } from 'react';
import styled from 'styled-components';
import {
  BusinessAreaDataQuery,
  TargetPopulationQuery,
  useCashAssistUrlPrefixQuery,
} from '@generated/graphql';
import { LoadingComponent } from '@components/core/LoadingComponent';
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

export interface FinalizedTargetPopulationHeaderButtonsPropTypes {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canDuplicate: boolean;
  businessAreaData: BusinessAreaDataQuery;
}

export function FinalizedTargetPopulationHeaderButtons({
  targetPopulation,
  canDuplicate,
  businessAreaData,
}: FinalizedTargetPopulationHeaderButtonsPropTypes): React.ReactElement {
  const [openDuplicate, setOpenDuplicate] = useState(false);
  const { data, loading } = useCashAssistUrlPrefixQuery({
    fetchPolicy: 'cache-first',
  });

  if (loading) return <LoadingComponent />;
  if (!data) return null;
  return (
    <Box display="flex" alignItems="center">
      {canDuplicate && (
        <IconContainer>
          <Button onClick={() => setOpenDuplicate(true)}>
            <FileCopy />
          </Button>
        </IconContainer>
      )}
      <Box m={2}>
        {!businessAreaData.businessArea.isPaymentPlanApplicable && (
          <Button
            variant="contained"
            color="primary"
            component="a"
            disabled={!targetPopulation.caHashId}
            target="_blank"
            href={`${data.cashAssistUrlPrefix}&pagetype=entityrecord&etn=progres_targetpopulation&id=${targetPopulation.caHashId}`}
            startIcon={<OpenInNewRoundedIcon />}
          >
            Open in CashAssist
          </Button>
        )}
      </Box>
      <DuplicateTargetPopulation
        open={openDuplicate}
        setOpen={setOpenDuplicate}
        targetPopulationId={targetPopulation.id}
      />
    </Box>
  );
}
