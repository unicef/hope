import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { Box, Typography } from '@mui/material';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { Field } from 'formik';
import type { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { ResponsiveGrid, ResponsiveGridContainer } from 'src/responsive';

const StyledBox = styled(Box)`
  width: 100%;
`;

export function PaymentPlanTargeting({
  targetPopulations,
  loading = false,
  disabled,
}: {
  targetPopulations: Array<{ id: string; name?: string }>;
  loading?: boolean;
  disabled?: boolean;
}): ReactElement {
  const { t } = useTranslation();
  if (loading) return <LoadingComponent />;

  const mappedTargetPopulations = targetPopulations.map((targetPopulation) => ({
    name: targetPopulation.name,
    value: targetPopulation.id,
  }));

  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Target Population')}</Typography>
      </Title>
      <OverviewContainer>
        <StyledBox
          sx={{
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <ResponsiveGridContainer spacing={3}>
            <ResponsiveGrid size="half">
              <Field
                name="paymentPlanId"
                label={t('Target Population')}
                fullWidth
                variant="outlined"
                required
                choices={mappedTargetPopulations}
                component={FormikSelectField}
                disabled={disabled}
                data-cy="input-target-population"
              />
            </ResponsiveGrid>
          </ResponsiveGridContainer>
        </StyledBox>
      </OverviewContainer>
    </PaperContainer>
  );
}
