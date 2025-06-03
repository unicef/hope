import { Box, Button, Collapse, Grid2 as Grid, Typography } from '@mui/material';
import KeyboardArrowDown from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUp from '@mui/icons-material/KeyboardArrowUp';
import { Field } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { PaperContainer } from '../PaperContainer';
import { useProgramContext } from '../../../programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';

function Exclusions({
  initialOpen = false,
}: {
  initialOpen?: boolean;
}): ReactElement {
  const [isExclusionsOpen, setExclusionsOpen] = useState(initialOpen);
  const { t } = useTranslation();
  const { isSocialDctType } = useProgramContext();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  return (
    <PaperContainer>
      <Box display="flex" justifyContent="space-between">
        <Typography data-cy="title-excluded-entries" variant="h6">
          {isSocialDctType
            ? t('Excluded Target Population Entries')
            : `Excluded Target Population Entries (${beneficiaryGroup?.groupLabelPlural} or ${beneficiaryGroup?.memberLabelPlural})`}
        </Typography>
        <Button
          variant="outlined"
          color="primary"
          data-cy="button-show-hide-exclusions"
          onClick={() => setExclusionsOpen(!isExclusionsOpen)}
          endIcon={
            isExclusionsOpen ? <KeyboardArrowUp /> : <KeyboardArrowDown />
          }
        >
          {isExclusionsOpen ? t('HIDE') : t('SHOW')}
        </Button>
      </Box>
      <Collapse in={isExclusionsOpen}>
        <Box mt={2}>
          <Grid container>
            <Grid size={{ xs:6 }}>
              <Field
                data-cy="input-excluded-ids"
                name="excludedIds"
                fullWidth
                variant="outlined"
                label={
                  isSocialDctType
                    ? t(`${beneficiaryGroup?.memberLabel} IDs to exclude`)
                    : t(
                        `${beneficiaryGroup?.groupLabel} or ${beneficiaryGroup?.memberLabel} IDs to exclude`,
                      )
                }
                component={FormikTextField}
              />
            </Grid>
          </Grid>
        </Box>
        <Box mt={2}>
          <Grid container>
            <Grid size={{ xs:6 }}>
              <Field
                data-cy="input-exclusion-reason"
                name="exclusionReason"
                fullWidth
                multiline
                variant="outlined"
                label={t('Exclusion Reason')}
                component={FormikTextField}
              />
            </Grid>
          </Grid>
        </Box>
      </Collapse>
    </PaperContainer>
  );
}

export default withErrorBoundary(Exclusions, 'Exclusions');
