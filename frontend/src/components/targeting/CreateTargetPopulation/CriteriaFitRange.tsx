import { Box, Button, Collapse, Grid, Typography } from '@material-ui/core';
import KeyboardArrowDown from '@material-ui/icons/KeyboardArrowDown';
import KeyboardArrowUp from '@material-ui/icons/KeyboardArrowUp';
import { Field } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { FieldLabel } from '../../core/FieldLabel';
import { PaperContainer } from '../PaperContainer';

export function CriteriaFitRange({
  initialOpen = false,
}: {
  initialOpen?: boolean;
}): React.ReactElement {
  const [isCriteriaFitRangeOpen, setCriteriaFitRangeOpen] = useState(
    initialOpen,
  );
  const { t } = useTranslation();

  return (
    <PaperContainer>
      <Box display='flex' justifyContent='space-between'>
        <Typography variant='h6'>{t('Criteria Fit Range')}</Typography>
        <Button
          variant='outlined'
          color='primary'
          onClick={() => setCriteriaFitRangeOpen(!isCriteriaFitRangeOpen)}
          endIcon={
            isCriteriaFitRangeOpen ? <KeyboardArrowUp /> : <KeyboardArrowDown />
          }
        >
          {isCriteriaFitRangeOpen ? t('HIDE') : t('SHOW')}
        </Button>
      </Box>
      <Collapse in={isCriteriaFitRangeOpen}>
        <Box mt={2}>
          <Box mt={3}>
            <FieldLabel>
              {t(
                'How many individuals in the household should fit these criteria?',
              )}
            </FieldLabel>
            <Box mt={2} display='flex'>
              <Box mr={2}>
                <Field
                  name='criteriaFitRangeMin'
                  type='number'
                  label={t('From')}
                  color='primary'
                  component={FormikTextField}
                  variant='outlined'
                />
              </Box>
              <Field
                name='criteriaFitRangeMax'
                type='number'
                label={t('To')}
                color='primary'
                component={FormikTextField}
                variant='outlined'
              />
            </Box>
          </Box>
        </Box>
      </Collapse>
    </PaperContainer>
  );
}
