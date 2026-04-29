import { LoadingComponent } from '@core/LoadingComponent';
import { OverviewContainer } from '@core/OverviewContainer';
import { Title } from '@core/Title';
import { Box, Grid, Typography } from '@mui/material';
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

interface Group {
  id: string;
  name: string;
}

export function PaymentPlanTargeting({
  allTargetPopulations,
  loading,
  disabled,
  groups,
}: {
  allTargetPopulations: PaginatedTargetPopulationListList;
  loading: boolean;
  disabled?: boolean;
  groups?: Group[];
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
          <Grid container spacing={3}>
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
            {groups && (
              <Grid size={{ xs: 6 }}>
                <Field
                  name="paymentPlanGroupId"
                  label={t('Group')}
                  fullWidth
                  variant="outlined"
                  choices={groups.map((g) => ({ value: g.id, name: g.name }))}
                  component={FormikSelectField}
                  disabled={disabled}
                  data-cy="input-payment-plan-group"
                />
              </Grid>
            )}
          </Grid>
        </StyledBox>
      </OverviewContainer>
    </PaperContainer>
  );
}
