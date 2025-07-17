import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import ReorderIcon from '@mui/icons-material/Reorder';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
} from '@mui/material';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { SplitPaymentPlan } from '@restgenerated/models/SplitPaymentPlan';
import { RestService } from '@restgenerated/services/RestService';
import { FormikSelectField } from '@shared/Formik/FormikSelectField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';

interface FormValues {
  splitType: string;
  paymentsNo: number;
}

const initialValues: FormValues = {
  splitType: '',
  paymentsNo: 0,
};

interface SplitIntoPaymentListsProps {
  paymentPlan: PaymentPlanDetail;
  canSplit: boolean;
}

export const SplitIntoPaymentLists = ({
  paymentPlan,
  canSplit,
}: SplitIntoPaymentListsProps): ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { businessArea, programId } = useBaseUrl();
  const { t } = useTranslation();
  const { mutateAsync: mutate, isPending: loading } = useMutation({
    mutationFn: ({
      businessAreaSlug,
      id,
      programSlug,
      requestBody,
    }: {
      businessAreaSlug: string;
      id: string;
      programSlug: string;
      requestBody: SplitPaymentPlan;
    }) =>
      RestService.restBusinessAreasProgramsPaymentPlansSplitCreate({
        businessAreaSlug,
        id,
        programSlug,
        requestBody,
      }),
    onSuccess: () => {
      showMessage(t('Payment Plan has been split successfully.'));
      setDialogOpen(false);
    },
  });

  let minPaymentsNoMessage = 'Payments Number must be greater than 10';
  let maxPaymentsNoMessage = `Payments Number must be less than ${paymentPlan.eligiblePaymentsCount}`;

  if (paymentPlan.eligiblePaymentsCount <= 10) {
    const msg = `There are too few payments (${paymentPlan.eligiblePaymentsCount}) to split`;
    minPaymentsNoMessage = msg;
    maxPaymentsNoMessage = msg;
  }

  const validationSchema = Yup.object().shape({
    splitType: Yup.string().required('Split Type is required'),
    paymentsNo: Yup.number().when('splitType', {
      is: 'BY_RECORDS',
      then: (schema) =>
        schema
          .required('Payments Number is required')
          .min(10, minPaymentsNoMessage)
          .max(paymentPlan.eligiblePaymentsCount, maxPaymentsNoMessage),
    }),
  });

  const handleSplit = async (values): Promise<void> => {
    try {
      await mutate({
        businessAreaSlug: businessArea,
        id: paymentPlan.id,
        programSlug: programId,
        requestBody: {
          splitType: values.splitType,
          paymentsNo: values.paymentsNo,
        },
      });
      setDialogOpen(false);
      showMessage(t('Split was successful!'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
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
      {({ values, submitForm }) => (
        <Form>
          <Button
            variant="contained"
            color="primary"
            onClick={() => setDialogOpen(true)}
            endIcon={<ReorderIcon />}
            disabled={!canSplit}
          >
            {t('Split')}
          </Button>
          <Dialog
            open={dialogOpen}
            onClose={() => setDialogOpen(false)}
            scroll="paper"
            aria-labelledby="form-dialog-title"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{t('Split into Payment Lists')}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12 }}>
                    <Field
                      name="splitType"
                      label="Split Type"
                      choices={paymentPlan.splitChoices}
                      component={FormikSelectField}
                    />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    {values.splitType === 'BY_RECORDS' && (
                      <Field
                        name="paymentsNo"
                        label="Payments Number"
                        component={FormikTextField}
                        type="number"
                        variant="outlined"
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
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-split"
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
