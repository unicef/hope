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
import { FormikSelectField } from '../../../../shared/Formik/FormikSelectField';
import { DialogContainer } from '../../../../containers/dialogs/DialogContainer';
import { DialogFooter } from '../../../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../../../containers/dialogs/DialogTitleWrapper';
import {useSnackbar} from "../../../../hooks/useSnackBar";
import {PaymentPlanQuery, useSplitPpMutation} from "../../../../__generated__/graphql";
import {LoadingButton} from "../../../core/LoadingButton";
import {GRIEVANCE_TICKET_STATES} from "../../../../utils/constants";

interface FormValues {
  splitType: string;
  paymentParts: number;
}

const initialValues: FormValues = {
  splitType: '',
  paymentParts: 0,
};

const validationSchema = Yup.object().shape({
  splitType: Yup.string().required('Split Type is required'),
  paymentParts: Yup.number().when('splitType', {
    is: 'BY_RECORDS',
    then: Yup.number().required('Payment Parts number is required'),
  }),
});

interface SplitIntoPaymentListsProps {
  paymentPlan: PaymentPlanQuery['paymentPlan'];
  canSplit: boolean;
}


export const SplitIntoPaymentLists = ({
  paymentPlan,
  canSplit,
}: SplitIntoPaymentListsProps): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { t } = useTranslation();
  const { splitTypes, paymentParts } = paymentPlan.splitChoices;
  const paymentPartChoices = paymentParts.map((part) => ({
    value: part,
    name: part,
  }));
  const [mutate, { loading }] = useSplitPpMutation();
  const { showMessage } = useSnackbar();

  const handleSplit = async (values): Promise<void> => {
    try {
      const { errors } = await mutate({
        variables: {
          paymentPlanId: paymentPlan.id,
          splitType: values.splitType,
          paymentParts: values.paymentParts,
        },
      });
      if (!errors) {
        setDialogOpen(false);
        showMessage(t('Split was successful!'));
      }
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={async (values) => {
        await handleSplit(values);
      }}
    >
      {({ values , submitForm}) => (
        <Form>
          <Button
            variant='contained'
            color='primary'
            onClick={() => setDialogOpen(true)}
            endIcon={<ReorderIcon />}
            disabled={!canSplit}
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
                      name='splitType'
                      label='Split Type'
                      choices={splitTypes}
                      component={FormikSelectField}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    {values.splitType === 'BY_RECORDS' && (
                      <Field
                        name='paymentParts'
                        label='Payment Parts'
                        choices={paymentPartChoices}
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
                <LoadingButton
                  loading={loading}
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-split'
                >
                  {t('Split')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
      )}
    </Formik>
  );
};
