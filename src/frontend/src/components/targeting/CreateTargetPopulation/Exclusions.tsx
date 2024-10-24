import { Box, Button, Collapse, Grid, Typography } from '@mui/material';
import KeyboardArrowDown from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUp from '@mui/icons-material/KeyboardArrowUp';
import { Field } from 'formik';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { PaperContainer } from '../PaperContainer';
import { useProgramContext } from '../../../programContext';

export function Exclusions({
  initialOpen = false,
}: {
  initialOpen?: boolean;
}): React.ReactElement {
  const [isExclusionsOpen, setExclusionsOpen] = useState(initialOpen);
  const { t } = useTranslation();
  const { isSocialDctType } = useProgramContext();
  return (
    <PaperContainer>
      <Box display="flex" justifyContent="space-between">
        <Typography data-cy="title-excluded-entries" variant="h6">
          {isSocialDctType
            ? t('Excluded Target Population Entries')
            : t(
                'Excluded Target Population Entries (Households or Individuals)',
              )}
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
            <Grid item xs={6}>
              <Field
                data-cy="input-excluded-ids"
                name="excludedIds"
                fullWidth
                variant="outlined"
                label={
                  isSocialDctType
                    ? t('Individual IDs to exclude')
                    : t('Household or Individual IDs to exclude')
                }
                component={FormikTextField}
              />
            </Grid>
          </Grid>
        </Box>
        <Box mt={2}>
          <Grid container>
            <Grid item xs={6}>
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
