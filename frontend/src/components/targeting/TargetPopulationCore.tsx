import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
} from '../../__generated__/graphql';
import { PaperContainer } from './PaperContainer';
import { Results } from './Results';
import { TargetingCriteria } from './TargetingCriteria';
import { TargetingHouseholds } from './TargetingHouseholds';

const Label = styled.p`
  color: #b1b1b5;
`;

interface TargetPopulationCoreProps {
  id: string;
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  canViewHouseholdDetails: boolean;
}

export function TargetPopulationCore({
  id,
  targetPopulation,
  canViewHouseholdDetails,
}: TargetPopulationCoreProps): React.ReactElement {
  const { t } = useTranslation();
  if (!targetPopulation) return null;
  const { rules } = targetPopulation.targetingCriteria;
  return (
    <>
      <TargetingCriteria
        candidateListRules={rules}
        targetPopulation={targetPopulation}
      />
      {targetPopulation?.excludedIds ? (
        <PaperContainer>
          <Typography variant='h6'>
            {t(
              'Excluded Target Population Entries (Households or Individuals)',
            )}
          </Typography>
          <Box mt={2}>
            <Grid container>
              <Grid item xs={6}>
                {targetPopulation?.excludedIds}
              </Grid>
            </Grid>
          </Box>
          <Box mt={2}>
            <Grid container>
              <Grid item xs={6}>
                {targetPopulation?.exclusionReason}
              </Grid>
            </Grid>
          </Box>
        </PaperContainer>
      ) : null}
      <Results targetPopulation={targetPopulation} />

      {targetPopulation.buildStatus === TargetPopulationBuildStatus.Ok ? (
        <TargetingHouseholds
          id={id}
          canViewDetails={canViewHouseholdDetails}
        />
      ) : (
        <PaperContainer>
          <Typography variant='h6'>
            {t('Target Population is building')}
          </Typography>
          <Label>
            Target population is processing, list of household will be available
            when process will be finished
          </Label>
        </PaperContainer>
      )}
      <UniversalActivityLogTable objectId={targetPopulation.id} />
    </>
  );
}
