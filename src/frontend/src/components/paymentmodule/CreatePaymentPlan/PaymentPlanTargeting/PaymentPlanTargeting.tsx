import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { Box, Grid2 as Grid, Typography } from '@mui/material';
import { PaginatedTargetPopulationListList } from '@restgenerated/models/PaginatedTargetPopulationListList';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { Field } from 'formik';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaperContainer } from '../../../targeting/PaperContainer';

const StyledBox = styled(Box)`
  width: 100%;
`;

export function PaymentPlanTargeting({
  allTargetPopulations,
  loading,
  disabled,
}: {
  allTargetPopulations: PaginatedTargetPopulationListList;
  loading: boolean;
  disabled?: boolean;
}): ReactElement {
  const { t } = useTranslation();
  if (loading) return <LoadingComponent />;

  const mappedTargetPopulations = allTargetPopulations.results.map((edge) => ({
    name: edge.name,
    value: edge.id,
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
            </Grid>
          </Grid>
        </StyledBox>
      </OverviewContainer>
    </PaperContainer>
  );
}
