import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { hasPermissions, PERMISSIONS } from '../../config/permissions';
import { UniversalActivityLogTable } from '@containers/tables/UniversalActivityLogTable';
import { PaymentPlanBuildStatus } from '@generated/graphql';
import { PaperContainer } from './PaperContainer';
import ResultsForHouseholds from './ResultsForHouseholds';
import TargetingHouseholds from './TargetingHouseholds';
import { TargetPopulationPeopleTable } from '@containers/tables/targeting/TargetPopulationPeopleTable';
import ResultsForPeople from '@components/targeting/ResultsForPeople';
import { useProgramContext } from 'src/programContext';
import { ReactElement } from 'react';
import AddFilterTargetingCriteriaDisplay from './TargetingCriteriaDisplay/AddFilterTargetingCriteriaDisplay';

const Label = styled.p`
  color: #b1b1b5;
`;

interface TargetPopulationCoreProps {
  id: string;
  targetPopulation;
  permissions: string[];
  screenBeneficiary: boolean;
  isStandardDctType: boolean;
  isSocialDctType: boolean;
}

export const TargetPopulationCore = ({
  id,
  targetPopulation,
  permissions,
  screenBeneficiary,
  isStandardDctType,
  isSocialDctType,
}: TargetPopulationCoreProps): ReactElement => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  if (!targetPopulation) return null;

  const ResultComponent = targetPopulation.program.isSocialWorkerProgram
    ? ResultsForPeople
    : ResultsForHouseholds;

  const recordsTable = targetPopulation.program.isSocialWorkerProgram ? (
    <TargetPopulationPeopleTable
      id={id}
      canViewDetails={hasPermissions(
        PERMISSIONS.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
        permissions,
      )}
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
    targetPopulation.buildStatus === PaymentPlanBuildStatus.Ok ? (
      recordsTable
    ) : (
      <PaperContainer>
        <Typography data-cy="target-population-building" variant="h6">
          {t('Target Population is building')}
        </Typography>
        <Label>
          {`Target population is processing, the list of ${beneficiaryGroup?.groupLabelPlural} will be
         available when the process is finished`}
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
          <AddFilterTargetingCriteriaDisplay
            rules={targetPopulation.targetingCriteria?.rules || []}
            targetPopulation={targetPopulation}
            screenBeneficiary={screenBeneficiary}
            isStandardDctType={isStandardDctType}
            isSocialDctType={isSocialDctType}
          />
        </PaperContainer>
      ) : null}
      {targetPopulation?.excludedIds ? (
        <PaperContainer>
          <Typography data-cy="title-excluded-entries" variant="h6">
            {isSocialDctType
              ? t('Excluded Target Population Entries')
              : t(
                  `Excluded Target Population Entries (${beneficiaryGroup?.groupLabelPlural} or ${beneficiaryGroup?.memberLabelPlural})`,
                )}
          </Typography>
          <Box mt={2}>
            <Grid container>
              <Grid size={{ xs:6 }}>
                {targetPopulation?.excludedIds}
              </Grid>
            </Grid>
          </Box>
          <Box mt={2}>
            <Grid container>
              <Grid size={{ xs:6 }}>
                {targetPopulation?.exclusionReason}
              </Grid>
            </Grid>
          </Box>
        </PaperContainer>
      ) : null}
      <ResultComponent targetPopulation={targetPopulation} />
      {recordInfo}
      {hasPermissions(PERMISSIONS.ACTIVITY_LOG_VIEW, permissions) && (
        <UniversalActivityLogTable objectId={targetPopulation.id} />
      )}
    </>
  );
};
