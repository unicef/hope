import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import AddIcon from '@mui/icons-material/Add';
import {
  Autocomplete,
  Button,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  TextField,
} from '@mui/material';
import { FollowUpInstructionCreate } from '@restgenerated/models/FollowUpInstructionCreate';
import { FollowUpInstructionDetail } from '@restgenerated/models/FollowUpInstructionDetail';
import { PaginatedPaymentPlanGroupListList } from '@restgenerated/models/PaginatedPaymentPlanGroupListList';
import { RestService } from '@restgenerated/services/RestService';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages } from '@utils/utils';
import { format } from 'date-fns';
import { Field, Form, Formik } from 'formik';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import * as Yup from 'yup';

interface FormValues {
  paymentPlanGroupIds: string[];
  dispersionStartDate: string | null;
  dispersionEndDate: string | null;
}

const validationSchema = Yup.object({
  paymentPlanGroupIds: Yup.array()
    .of(Yup.string())
    .min(1, 'At least one group is required'),
  dispersionStartDate: Yup.date()
    .nullable()
    .required('Dispersion Start Date is required'),
  dispersionEndDate: Yup.date()
    .nullable()
    .required('Dispersion End Date is required'),
});

const initialValues: FormValues = {
  paymentPlanGroupIds: [],
  dispersionStartDate: null,
  dispersionEndDate: null,
};

export function CreateFollowUpInstructionDialog(): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const { data: groupsData } = useQuery<PaginatedPaymentPlanGroupListList>({
    queryKey: ['paymentPlanGroupsList', businessArea, programId, 'all'],
    queryFn: () =>
      RestService.restBusinessAreasProgramsPaymentPlanGroupsList({
        businessAreaSlug: businessArea,
        programCode: programId,
        limit: 200,
      }),
    enabled: open && !!businessArea && !!programId,
  });

  const groupOptions = (groupsData?.results ?? []).map((g) => ({
    id: g.id,
    label: g.unicefId ?? g.name ?? g.id,
  }));

  const { mutateAsync: createInstruction, isPending } = useMutation<
    FollowUpInstructionDetail,
    Error,
    FollowUpInstructionCreate
  >({
    mutationFn: (requestBody: FollowUpInstructionCreate) =>
      RestService.restBusinessAreasProgramsFollowUpInstructionsCreate({
        businessAreaSlug: businessArea,
        programCode: programId,
        requestBody,
      }) as any,
  });

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const body: FollowUpInstructionCreate = {
        paymentPlanGroupIds: values.paymentPlanGroupIds,
        dispersionStartDate: values.dispersionStartDate
          ? format(new Date(values.dispersionStartDate), 'yyyy-MM-dd')
          : '',
        dispersionEndDate: values.dispersionEndDate
          ? format(new Date(values.dispersionEndDate), 'yyyy-MM-dd')
          : '',
      };
      const created = await createInstruction(body);
      await queryClient.invalidateQueries({
        queryKey: ['followUpInstructionsList', businessArea, programId],
      });
      setOpen(false);
      showMessage(t('Follow-up Instruction created'));
      navigate(
        `/${baseUrl}/payment-module/follow-up-instructions/${created.id}`,
      );
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        startIcon={<AddIcon />}
        onClick={() => setOpen(true)}
        data-cy="button-create-follow-up-instruction"
      >
        {t('Create Follow-up Instruction')}
      </Button>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        maxWidth="sm"
        fullWidth
      >
        <Formik
          initialValues={initialValues}
          validationSchema={validationSchema}
          onSubmit={handleSubmit}
        >
          {({ submitForm, values, setFieldValue, errors, touched }) => (
            <Form>
              <DialogTitleWrapper>
                <DialogTitle>{t('Create Follow-up Instruction')}</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <Grid container spacing={3}>
                  <Grid size={{ xs: 12 }}>
                    <Autocomplete
                      multiple
                      options={groupOptions}
                      value={groupOptions.filter((opt) =>
                        values.paymentPlanGroupIds.includes(opt.id),
                      )}
                      onChange={(_, selected) => {
                        setFieldValue(
                          'paymentPlanGroupIds',
                          selected.map((s) => s.id),
                        );
                      }}
                      getOptionLabel={(opt) => opt.label}
                      renderTags={(value, getTagProps) =>
                        value.map((opt, index) => (
                          <Chip
                            label={opt.label}
                            {...getTagProps({ index })}
                            key={opt.id}
                          />
                        ))
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label={t('Payment Plan Groups')}
                          required
                          error={
                            touched.paymentPlanGroupIds &&
                            Boolean(errors.paymentPlanGroupIds)
                          }
                          helperText={
                            touched.paymentPlanGroupIds &&
                            (errors.paymentPlanGroupIds as string)
                          }
                        />
                      )}
                    />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Field
                      name="dispersionStartDate"
                      label={t('Dispersion Start Date')}
                      component={FormikDateField}
                      required
                      fullWidth
                    />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Field
                      name="dispersionEndDate"
                      label={t('Dispersion End Date')}
                      component={FormikDateField}
                      required
                      fullWidth
                    />
                  </Grid>
                </Grid>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                  <LoadingButton
                    loading={isPending}
                    color="primary"
                    variant="contained"
                    onClick={submitForm}
                    data-cy="button-submit-create-follow-up-instruction"
                  >
                    {t('Create')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </Form>
          )}
        </Formik>
      </Dialog>
    </>
  );
}
