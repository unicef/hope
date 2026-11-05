import { Field } from 'formik';
import { useTranslation } from 'react-i18next';
import { Box, Checkbox, FormControlLabel, Grid } from '@mui/material';
import type { FormControlLabelProps } from '@mui/material';
import { FormikCheckboxField } from '@shared/Formik/FormikCheckboxField';
import type { FC, ReactElement } from 'react';
import { useProgramContext } from 'src/programContext';
import { responsiveGridSize, responsiveValue } from 'src/responsive';
import withErrorBoundary from '@components/core/withErrorBoundary';

// Long labels must wrap on phones, where the checkboxes stack.
const NoWrapCheckbox = (props: FormControlLabelProps): ReactElement => (
  <FormControlLabel
    sx={{ whiteSpace: responsiveValue('normal', 'nowrap') }}
    {...props}
  />
);

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
    <Box
      sx={{
        mt: 3,
        p: 3,
      }}
    >
      {isDetailsPage ? (
        <Box
          sx={{
            mt: 3,
            p: 3,
          }}
        >
          <Grid container spacing={3}>
            <Grid size={responsiveGridSize('half')}>
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
            <Grid size={responsiveGridSize('half')}>
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
        <Box
          sx={{
            mt: 3,
            p: 3,
          }}
        >
          <Grid container spacing={3}>
            {isStandardDctType && (
              <Grid size={responsiveGridSize('half')}>
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
              <Grid size={responsiveGridSize('half')}>
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
              <Grid size={responsiveGridSize('half')}>
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
              <Grid size={responsiveGridSize('half')}>
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
