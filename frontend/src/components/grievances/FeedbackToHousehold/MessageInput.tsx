import React from 'react';
import { useTranslation } from 'react-i18next';
import { Box, Grid } from '@material-ui/core';
import { Field, Form } from 'formik';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { LoadingButton } from '../../core/LoadingButton';
import { DescMargin } from './styled';

export function MessageInput({ loading, submitForm }): React.ReactElement {
  const { t } = useTranslation();
  return (
    <Grid container>
      <Grid item xs={12}>
        <DescMargin>
          <Form>
            <Field
              name='message'
              multiline
              fullWidth
              variant='filled'
              label={t('Send a message to household...')}
              component={FormikTextField}
            />
            <Box mt={2} display='flex' justifyContent='flex-end'>
              <LoadingButton
                loading={loading}
                color='primary'
                variant='contained'
                onClick={submitForm}
              >
                {t('Send')}
              </LoadingButton>
            </Box>
          </Form>
        </DescMargin>
      </Grid>
    </Grid>
  );
}
