import { Box, Grid2 as Grid, Typography } from '@mui/material';
import styled from 'styled-components';
import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { PaperContainer } from '../../../targeting/PaperContainer';
import { ReactElement } from 'react';
import { TargetPopulationList } from '@restgenerated/models/TargetPopulationList';

const StyledBox = styled(Box)`
  width: 100%;
`;

export function PaymentPlanTargeting({
  allTargetPopulations,
  loading,
  disabled,
}: {
  allTargetPopulations: TargetPopulationList[];
  loading: boolean;
  disabled?: boolean;
}): ReactElement {
  const { t } = useTranslation();
  if (loading) return <LoadingComponent />;

  const mappedTargetPopulations = allTargetPopulations.map((el) => ({
    name: el.name,
    value: el.id,
  }));

  return (
    <PaperContainer>
      <Title>
        <Typography variant="h6">{t('Target Population')}</Typography>
      </Title>
      <OverviewContainer>
        <StyledBox display="flex" flexDirection="column">
          <Grid container>
            <Grid size={{ xs: 6 }}>
              <Field
                name="targetingId"
                label={t('Target Population')}
                fullWidth
                variant="outlined"
                required
                choices={mappedTargetPopulations}
                component={FormikSelectField}
                disabled={disabled}
                data-cy="input-target-population"
              />
            </Grid>
          </Grid>
        </StyledBox>
      </OverviewContainer>
    </PaperContainer>
  );
}
