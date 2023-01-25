import { Box, Grid, Typography } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { UniversalActivityLogTable } from '../../../containers/tables/UniversalActivityLogTable';
import {
  TargetPopulationBuildStatus,
  TargetPopulationQuery,
} from '../../../__generated__/graphql';
import { PaperContainer } from '../../targeting/PaperContainer';
import { Results } from '../../targeting/Results';
import { EnrollmentCriteria } from './EnrollmentCriteria/EnrollmentCriteria';
import { EnrollmentHouseholdTable } from './EnrollmentHouseholdTable';

const Label = styled.p`
  color: #b1b1b5;
`;

interface EnrollmentCoreProps {
  id: string;
  targetPopulation: TargetPopulationQuery['targetPopulation'];
  permissions: string[];
}

export const EnrollmentCore = ({
  id,
  targetPopulation,
  permissions,
}: EnrollmentCoreProps): React.ReactElement => {
  const { t } = useTranslation();
  if (!targetPopulation) return null;

  return (
    <>
      {targetPopulation.targetingCriteria ? (
        <EnrollmentCriteria
          rules={targetPopulation.targetingCriteria?.rules || []}
          targetPopulation={targetPopulation}
        />
      ) : null}
      {targetPopulation?.excludedIds ? (
        <PaperContainer>
          <Typography variant='h6'>
            {t('Excluded Enrollment Entries (Households or Individuals)')}
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
        <EnrollmentHouseholdTable
          id={id}
          canViewDetails={hasPermissions(
            PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
            permissions,
          )}
        />
      ) : (
        <PaperContainer>
          <Typography variant='h6'>{t('Enrollment is building')}</Typography>
          <Label>
            {t(
              'Enrollment is processing, the list of households will be available when the process is finished',
            )}
          </Label>
        </PaperContainer>
      )}

      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={targetPopulation.id} />
      )}
    </>
  );
};
