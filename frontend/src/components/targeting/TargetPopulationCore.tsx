import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalActivityLogTable } from '../../containers/tables/UniversalActivityLogTable';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { PaperContainer } from './PaperContainer';
import { Results } from './Results';
import { TargetingCriteria } from './TargetingCriteria';
import { TargetingHouseholds } from './TargetingHouseholds';

const Label = styled.p`
  color: #b1b1b5;
`;

export function TargetPopulationCore({
  candidateList,
  id,
  status,
  targetPopulation,
  permissions,
}): React.ReactElement {
  const { t } = useTranslation();
  if (!candidateList) return null;
  const { rules: candidateListRules } = candidateList;
  return (
    <>
      <TargetingCriteria
        candidateListRules={candidateListRules}
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
      <Results
        resultsData={targetPopulation.candidateStats}
        totalNumOfHouseholds={targetPopulation.candidateListTotalHouseholds}
        totalNumOfIndividuals={targetPopulation.candidateListTotalIndividuals}
      />

      {candidateListRules.length ? (
        <TargetingHouseholds
          id={id}
          status={status}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            permissions,
          )}
        />
      ) : (
        <PaperContainer>
          <Typography variant='h6'>
            {t('Target Population Entries (Households)')}
          </Typography>
          <Label>{t('Add targeting criteria to see results.')}</Label>
        </PaperContainer>
      )}
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={targetPopulation.id} />
      )}
    </>
  );
}
