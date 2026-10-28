import { Box, Chip, Typography } from '@mui/material';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';
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
import type { ReactElement } from 'react';
import withErrorBoundary from '@components/core/withErrorBoundary';
import type { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';

interface ProgramDetailsProps {
  targetPopulation: TargetPopulationDetail;
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
        <ResponsiveGridContainer data-cy="details-grid" spacing={6}>
          <ResponsiveGrid size="third" mobileSize="half">
            <LabelizedField label={t('Status')}>
              <StatusBox
                dataCy="target-population-status"
                status={targetPopulation.status}
                statusToColor={paymentPlanStatusToColor}
                statusNameMapping={targetPopulationStatusDisplayMap}
              />
            </LabelizedField>
          </ResponsiveGrid>
          <ResponsiveGrid size="third" mobileSize="half">
            <LabelizedField
              dataCy="created-by"
              label={t('created by')}
              value={createdBy}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third" mobileSize="half">
            <LabelizedField
              dataCy="program-name"
              label={t('Programme')}
              value={programName}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third" mobileSize="half">
            <LabelizedField
              dataCy="programme-cycle-title"
              label={t('Programme Cycle')}
              value={programCycle?.title ?? '-'}
            />
          </ResponsiveGrid>
          <ResponsiveGrid size="third" mobileSize="half">
            <LabelizedField
              dataCy="payment-plan-group-name"
              label={t('Payment Plan')}
              value={targetPopulation.paymentPlanGroup?.name ?? '-'}
            />
          </ResponsiveGrid>
          {targetPopulation.paymentPlanPurposes?.length > 0 && (
            <ResponsiveGrid size="third" mobileSize="half">
              <LabelizedField label={t('Purposes')}>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {targetPopulation.paymentPlanPurposes.map((p) => (
                    <Chip key={p.id} label={p.name} size="small" />
                  ))}
                </Box>
              </LabelizedField>
            </ResponsiveGrid>
          )}
        </ResponsiveGridContainer>
      </OverviewContainer>
    </ContainerColumnWithBorder>
  );
}

export default withErrorBoundary(
  TargetPopulationDetails,
  'TargetPopulationDetails',
);
