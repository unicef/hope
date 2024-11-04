import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { Box, Checkbox, FormControlLabel, Grid } from '@mui/material';
import styled from 'styled-components';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FC } from 'react';

const NoWrapCheckbox = styled(FormControlLabel)`
  white-space: nowrap;
`;

interface ExcludeCheckboxesProps {
  isStandardDctType: boolean;
  isSocialDctType: boolean;
  screenBeneficiary: boolean;
  isDetailsPage: boolean;
  targetPopulation: any;
}

export const ExcludeCheckboxes: FC<ExcludeCheckboxesProps> = ({
  isStandardDctType,
  isSocialDctType,
  screenBeneficiary,
  isDetailsPage,
  targetPopulation,
}) => {
  const { t } = useTranslation();

  return (
    <Box mt={3} p={3}>
      {isDetailsPage ? (
        <Box mt={3} p={3}>
          <Grid container spacing={3}>
            <Grid item xs={6}>
              {isStandardDctType && (
                <NoWrapCheckbox
                  disabled
                  control={
                    <Checkbox
                      name="flagExcludeIfActiveAdjudicationTicket"
                      color="primary"
                      data-cy="checkbox-exclude-if-active-adjudication-ticket"
                      checked={Boolean(
                        targetPopulation?.targetingCriteria
                          ?.flagExcludeIfActiveAdjudicationTicket,
                      )}
                    />
                  }
                  label={t(
                    'Exclude Households with Active Adjudication Ticket',
                  )}
                />
              )}
              {isSocialDctType && (
                <NoWrapCheckbox
                  disabled
                  control={
                    <Checkbox
                      name="flagExcludeIfActiveAdjudicationTicket"
                      color="primary"
                      data-cy="checkbox-exclude-people-if-active-adjudication-ticket"
                      checked={Boolean(
                        targetPopulation?.targetingCriteria
                          ?.flagExcludeIfActiveAdjudicationTicket,
                      )}
                    />
                  }
                  label={t('Exclude People with Active Adjudication Ticket')}
                />
              )}
            </Grid>
            <Grid item xs={6}>
              {screenBeneficiary && isSocialDctType && (
                <NoWrapCheckbox
                  disabled
                  control={
                    <Checkbox
                      name="flagExcludeIfOnSanctionList"
                      color="primary"
                      data-cy="checkbox-exclude-if-on-sanction-list"
                    />
                  }
                  checked={Boolean(
                    targetPopulation?.targetingCriteria
                      ?.flagExcludeIfOnSanctionList,
                  )}
                  label={t(
                    'Exclude People with an Active Sanction Screen Flag',
                  )}
                />
              )}
              {screenBeneficiary && isStandardDctType && (
                <NoWrapCheckbox
                  disabled
                  control={
                    <Checkbox
                      name="flagExcludeIfOnSanctionList"
                      color="primary"
                      data-cy="checkbox-exclude-if-on-sanction-list"
                    />
                  }
                  checked={Boolean(
                    targetPopulation?.targetingCriteria
                      ?.flagExcludeIfOnSanctionList,
                  )}
                  label={t(
                    'Exclude Households with an Active Sanction Screen Flag',
                  )}
                />
              )}
            </Grid>
          </Grid>
        </Box>
      ) : (
        <Box mt={3} p={3}>
          <Grid container spacing={3}>
            {isStandardDctType && (
              <Grid item xs={6}>
                <Field
                  name="flagExcludeIfActiveAdjudicationTicket"
                  label={t(
                    'Exclude Households with Active Adjudication Ticket',
                  )}
                  color="primary"
                  component={FormikCheckboxField}
                  data-cy="input-active-adjudication-ticket"
                />
              </Grid>
            )}
            {isSocialDctType && (
              <Grid item xs={6}>
                <Field
                  name="flagExcludePeopleWithActiveAdjudicationTicket"
                  label={t('Exclude People with Active Adjudication Ticket')}
                  color="primary"
                  component={FormikCheckboxField}
                  data-cy="input-active-adjudication-ticket"
                />
              </Grid>
            )}
            {screenBeneficiary && isStandardDctType && (
              <Grid item xs={6}>
                <Field
                  name="flagExcludeIfOnSanctionList"
                  label={t(
                    'Exclude Households with an Active Sanction Screen Flag',
                  )}
                  color="primary"
                  component={FormikCheckboxField}
                  data-cy="input-active-sanction-flag"
                />
              </Grid>
            )}
            {screenBeneficiary && isSocialDctType && (
              <Grid item xs={6}>
                <Field
                  name="flagExcludeIfOnSanctionList"
                  label={t(
                    'Exclude People with an Active Sanction Screen Flag',
                  )}
                  color="primary"
                  component={FormikCheckboxField}
                  data-cy="input-active-sanction-flag"
                />
              </Grid>
            )}
          </Grid>
        </Box>
      )}
    </Box>
  );
};
