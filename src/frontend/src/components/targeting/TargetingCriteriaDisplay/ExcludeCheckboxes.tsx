import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { Box, Checkbox, FormControlLabel, Grid2 as Grid } from '@mui/material';
import styled from 'styled-components';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import { FC } from 'react';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';

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

const ExcludeCheckboxes: FC<ExcludeCheckboxesProps> = ({
  isStandardDctType,
  isSocialDctType,
  screenBeneficiary,
  isDetailsPage,
  targetPopulation,
}) => {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <Box mt={3} p={3}>
      {isDetailsPage ? (
        <Box mt={3} p={3}>
          <Grid container spacing={3}>
            <Grid size={{ xs:6 }}>
              {isStandardDctType && (
                <NoWrapCheckbox
                  disabled
                  control={
                    <Checkbox
                      name="flagExcludeIfActiveAdjudicationTicket"
                      color="primary"
                      data-cy="checkbox-exclude-if-active-adjudication-ticket"
                      checked={Boolean(
                        targetPopulation?.flagExcludeIfActiveAdjudicationTicket,
                      )}
                    />
                  }
                  label={t(
                    `Exclude ${beneficiaryGroup?.groupLabelPlural} with Active Adjudication Ticket`,
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
                        targetPopulation?.flagExcludeIfActiveAdjudicationTicket,
                      )}
                    />
                  }
                  label={t('Exclude People with Active Adjudication Ticket')}
                />
              )}
            </Grid>
            <Grid size={{ xs:6 }}>
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
                    targetPopulation?.flagExcludeIfOnSanctionList,
                  )}
                  label={t(
                    `Exclude ${beneficiaryGroup?.memberLabelPlural} with an Active Sanction Screen Flag`,
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
                    targetPopulation?.flagExcludeIfOnSanctionList,
                  )}
                  label={t(
                    `Exclude ${beneficiaryGroup?.groupLabelPlural} with an Active Sanction Screen Flag`,
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
              <Grid size={{ xs:6 }}>
                <Field
                  name="flagExcludeIfActiveAdjudicationTicket"
                  label={t(
                    `Exclude ${beneficiaryGroup?.groupLabelPlural} with Active Adjudication Ticket`,
                  )}
                  color="primary"
                  component={FormikCheckboxField}
                  data-cy="input-active-adjudication-ticket"
                />
              </Grid>
            )}
            {isSocialDctType && (
              <Grid size={{ xs:6 }}>
                <Field
                  name="flagExcludeIfActiveAdjudicationTicket"
                  label={t(
                    `Exclude ${beneficiaryGroup?.memberLabelPlural} with Active Adjudication Ticket`,
                  )}
                  color="primary"
                  component={FormikCheckboxField}
                  data-cy="input-active-adjudication-ticket"
                />
              </Grid>
            )}
            {screenBeneficiary && isStandardDctType && (
              <Grid size={{ xs:6 }}>
                <Field
                  name="flagExcludeIfOnSanctionList"
                  label={t(
                    `Exclude ${beneficiaryGroup?.groupLabelPlural} with an Active Sanction Screen Flag`,
                  )}
                  color="primary"
                  component={FormikCheckboxField}
                  data-cy="input-active-sanction-flag"
                />
              </Grid>
            )}
            {screenBeneficiary && isSocialDctType && (
              <Grid size={{ xs:6 }}>
                <Field
                  name="flagExcludeIfOnSanctionList"
                  label={t(
                    `Exclude ${beneficiaryGroup?.memberLabelPlural} with an Active Sanction Screen Flag`,
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

export default withErrorBoundary(ExcludeCheckboxes, 'ExcludeCheckboxes');
