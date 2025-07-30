import { Grid2 as Grid, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import {
  paymentPlanStatusToColor,
  targetPopulationStatusDisplayMap,
} from '@utils/utils';
import { ContainerColumnWithBorder } from '@core/ContainerColumnWithBorder';
import { LabelizedField } from '@core/LabelizedField';
import { OverviewContainer } from '@core/OverviewContainer';
import { StatusBox } from '@core/StatusBox';
import { Title } from '@core/Title';
import { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';

interface ProgramDetailsProps {
  targetPopulation : TargetPopulationDetail;
}

function TargetPopulationDetails({
  targetPopulation,
}: ProgramDetailsProps): ReactElement {
  const { createdBy, program, programCycle } = targetPopulation;
  const { t } = useTranslation();

  const programName = program?.name ? program.name : '-';
  return (
    <ContainerColumnWithBorder data-cy="target-population-details-container">
      <Title data-cy="details-title">
        <Typography variant="h6">{t('Details')}</Typography>
      </Title>
      <OverviewContainer>
        <Grid data-cy="details-grid" container spacing={6}>
          <Grid size={{ xs: 4 }}>
            <LabelizedField label={t('Status')}>
              <StatusBox
                dataCy="target-population-status"
                status={targetPopulation.status}
                statusToColor={paymentPlanStatusToColor}
                statusNameMapping={targetPopulationStatusDisplayMap}
              />
            </LabelizedField>
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              dataCy="created-by"
              label={t('created by')}
              value={createdBy}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              dataCy="program-name"
              label={t('Programme')}
              value={programName}
            />
          </Grid>
          <Grid size={{ xs: 4 }}>
            <LabelizedField
              dataCy="programme-cycle-title"
              label={t('Programme Cycle')}
              value={programCycle?.title ?? '-'}
            />
          </Grid>
        </Grid>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

export default withErrorBoundary(
  TargetPopulationDetails,
  'TargetPopulationDetails',
);
