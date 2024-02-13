import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@material-ui/core';
import ReorderIcon from '@material-ui/icons/Reorder';
import { Field, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { PaymentPlanQuery } from '../../../../__generated__/graphql';
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';

interface FormValues {
  splitBy: string;
  numberOfRecords: number;
}

const initialValues: FormValues = {
  splitBy: '',
  numberOfRecords: 0,
};

const validationSchema = Yup.object().shape({
  splitBy: Yup.string().required('Split By is required'),
  numberOfRecords: Yup.number().when('splitBy', {
    is: 'Number of Records',
    then: Yup.number().required('Number of Records is required'),
  }),
});

interface SplitIntoPaymentListsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
}

export const SplitIntoPaymentLists = ({
  paymentPlan,
}: SplitIntoPaymentListsProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { t } = useTranslation();

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={(values) => {
        console.log(values);
        console.log(paymentPlan);
      }}
    >
      {({ values }) => (
        <Form>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setDialogOpen(true)}
            endIcon={<ReorderIcon />}
          >
            {t('Split')}
          </Button>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll='paper'
            aria-labelledby='form-dialog-title'
            maxWidth='md'
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Split into Payment Lists')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Field
                      name='splitBy'
                      label='Split By'
                      choices={[
                        { value: 'admin2', name: 'Admin Area 2' },
                        { value: 'collector', name: 'Collector' },
                        {
                          value: 'numberOfRecords',
                          name: 'Number of Records per Payment List',
                        },
                      ]}
                      component={FormikSelectField}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    {values.splitBy === 'numberOfRecords' && (
                      <Field
                        name='numberOfRecords'
                        label='Number of Records'
                        choices={[
                          { value: 10, name: '10' },
                          { value: 20, name: '20' },
                        ]}
                        component={FormikSelectField}
                      />
                    )}
                  </Grid>
                </Grid>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={() => setDialogOpen(false)}>
                  {t('Cancel')}
                </Button>
                <Button type='submit' color='primary' variant='contained'>
                  {t('Split')}
                </Button>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
};
