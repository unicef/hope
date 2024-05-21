import { Box, Grid, Typography } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
  useTargetPopulationHouseholdsQuery,
} from '@generated/graphql';
import { PaperContainer } from './PaperContainer';
import { Results } from './Results';
import { TargetingCriteria } from './TargetingCriteria';
import { TargetingHouseholds } from './TargetingHouseholds';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { TargetPopulationPeopleTable } from '@containers/tables/targeting/TargetPopulationPeopleTable';

const Label = styled.p`
  color: #b1b1b5;
`;

const IdContainer = styled.div`
  background-color: #e6ecf4;
  border: 1px solid #2f95fb;
  border-radius: 5px;
  padding: 10px;
  white-space: pre-wrap;
`;

interface TargetPopulationCoreProps {
  id: string;
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  permissions: string[];
  screenBeneficiary: boolean;
  isStandardDctType: boolean;
  isSocialDctType: boolean;
  category: string;
}

export const TargetPopulationCore = ({
  id,
  targetPopulation,
  permissions,
  screenBeneficiary,
  isStandardDctType,
  isSocialDctType,
  category,
}: TargetPopulationCoreProps): React.ReactElement => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  if (!targetPopulation) return null;
  const householdIds = targetPopulation.targetingCriteria?.householdIds;
  const individualIds = targetPopulation.targetingCriteria?.individualIds;

  const recordsTable = targetPopulation.program.isSocialWorkerProgram ? (
    <TargetPopulationPeopleTable
      id={id}
      query={useTargetPopulationHouseholdsQuery}
      queryObjectName="targetPopulationHouseholds"
      canViewDetails={hasPermissions(
        PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
        permissions,
      )}
      variables={{ businessArea }}
    />
  ) : (
    <TargetingHouseholds
      id={id}
      canViewDetails={hasPermissions(
        PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
        permissions,
      )}
    />
  );

  const recordInfo =
    targetPopulation.buildStatus === TargetPopulationBuildStatus.Ok ? (
      recordsTable
    ) : (
      <PaperContainer>
        <Typography data-cy="target-population-building" variant="h6">
          {t('Target Population is building')}
        </Typography>
        <Label>
          Target population is processing, the list of households will be
          available when the process is finished
        </Label>
      </PaperContainer>
    );

  return (
    <>
      {targetPopulation.targetingCriteria ? (
        <PaperContainer>
          <Box pt={3} pb={3}>
            <Typography variant="h6">{t('Targeting Criteria')}</Typography>
          </Box>
          <Box mb={2}>
            {householdIds.length > 0 && (
              <IdContainer>{householdIds}</IdContainer>
            )}
          </Box>
          {individualIds.length > 0 && (
            <IdContainer>{individualIds}</IdContainer>
          )}
          <TargetingCriteria
            rules={targetPopulation.targetingCriteria?.rules || []}
            targetPopulation={targetPopulation}
            screenBeneficiary={screenBeneficiary}
            isStandardDctType={isStandardDctType}
            isSocialDctType={isSocialDctType}
            category={category}
          />
        </PaperContainer>
      ) : null}
      {targetPopulation?.excludedIds ? (
        <PaperContainer>
          <Typography data-cy="title-excluded-entries" variant="h6">
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
      {recordInfo}
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={targetPopulation.id} />
      )}
    </>
  );
};
