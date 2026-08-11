import { DialogContainer } from '@containers/dialogs/DialogContainer';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DividerLine } from '@core/DividerLine';
import { FieldBorder } from '@core/FieldBorder';
import { DropzoneField } from '@core/DropzoneField';
import { GreyText } from '@core/GreyText';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { usePermissions } from '@hooks/usePermissions';
import { useSnackbar } from '@hooks/useSnackBar';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Typography,
} from '@mui/material';
import { PaymentPlanCreateTopUp } from '@restgenerated/models/PaymentPlanCreateTopUp';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { RestService } from '@restgenerated/services/RestService';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { useMutation } from '@tanstack/react-query';
import { showApiErrorMessages, today, tomorrow } from '@utils/utils';
import { format } from 'date-fns';
import { Field, Form, Formik } from 'formik';
import moment from 'moment';
import { ReactElement, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import * as Yup from 'yup';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useProgramContext } from '../../../programContext';
import { countTopUpAmountRows } from './countTopUpAmountRows';

type Variant = 'followup' | 'topup' | 'amendment';

export interface CreateChildPaymentPlanProps {
  paymentPlan: PaymentPlanDetail;
  variant: Variant;
}

/**
 * Shared dialog for creating a child Payment Plan from the current one:
 * Follow-up, Top-Up or Top-Up Amendment. The flows differ only in labels,
 * endpoint and navigation target. The withdrawn/unsuccessful warnings are
 * specific to Follow-up (it may only be started for unsuccessful payments).
 */
export function CreateChildPaymentPlan({
  paymentPlan,
  variant,
}: CreateChildPaymentPlanProps): ReactElement {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [fundedRows, setFundedRows] = useState<number | null>(null);
  const selectedFile = useRef<File | null>(null);
  const { baseUrl, businessArea, programId } = useBaseUrl();
  const permissions = usePermissions();
  const { isActiveProgram, selectedProgram } = useProgramContext();
  const { showMessage } = useSnackbar();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const isFollowUp = variant === 'followup';
  // The Amendment counts as a Top-Up here: both are funded the same way at creation.
  const isTopUp = variant === 'topup' || variant === 'amendment';
  const labels = {
    followup: {
      button: t('Create Follow-up PP'),
      title: t('Create Follow-up Payment Plan'),
    },
    topup: {
      button: t('Create Top-Up PP'),
      title: t('Create Top-Up Payment Plan'),
    },
    amendment: {
      button: t('Create Top-Up Amendment'),
      title: t('Create Top-Up Amendment Payment Plan'),
    },
  }[variant];
  const detailPath = isFollowUp ? 'followup-payment-plans' : 'payment-plans';

  const { mutateAsync: createChildPaymentPlan, isPending: loadingCreate } =
    useMutation({
      mutationFn: (requestBody: {
        dispersionStartDate: string;
        dispersionEndDate: string;
        fixedAmount?: string;
        file?: File;
      }) => {
        const params = {
          businessAreaSlug: businessArea,
          id: paymentPlan.id,
          programCode: programId,
          requestBody,
        };
        if (variant === 'followup') {
          return RestService.restBusinessAreasProgramsPaymentPlansCreateFollowUpCreate(
            params,
          );
        }
        const multipartParams = {
          businessAreaSlug: businessArea,
          id: paymentPlan.id,
          programCode: programId,
          // drf-spectacular types the multipart `file` as a string; the API takes a File.
          formData: requestBody as unknown as PaymentPlanCreateTopUp,
        };
        if (variant === 'amendment') {
          return RestService.restBusinessAreasProgramsPaymentPlansCreateTopUpAmendmentCreate(
            multipartParams,
          );
        }
        return RestService.restBusinessAreasProgramsPaymentPlansCreateTopUpCreate(
          multipartParams,
        );
      },
    });

  if (permissions === null) return null;

  const validationSchema = Yup.object().shape({
    dispersionStartDate: Yup.date().required(
      t('Dispersion Start Date is required'),
    ),
    dispersionEndDate: Yup.date()
      .required(t('Dispersion End Date is required'))
      .min(today, t('Dispersion End Date cannot be in the past'))
      .when(
        'dispersionStartDate',
        ([dispersionStartDate]: [Date | null | undefined], schema: Yup.DateSchema) =>
          dispersionStartDate
            ? schema.min(
                new Date(dispersionStartDate),
                `${t('Dispersion End Date has to be greater than')} ${moment(
                  dispersionStartDate,
                ).format('YYYY-MM-DD')}`,
              )
            : schema,
      ),
    // Only "neither" is checked: picking a file clears the fixed amount, so the two
    // funding modes can never both be set.
    fixedAmount: Yup.string().when('file', ([file]: [File | null], schema: Yup.StringSchema) =>
      isTopUp && !file
        ? schema
            .required(t('Enter a fixed amount or upload an amount file'))
            // Mirrors the serializer's min_value; keep the two in step.
            .test(
              'min-amount',
              t('Amount has to be at least 0.01'),
              (value) => Number(value) >= 0.01,
            )
        : schema,
    ),
    file: Yup.mixed().nullable(),
  });

  type FormValues = Yup.InferType<typeof validationSchema> & {
    fixedAmount?: string;
    file?: File | null;
  };
  const initialValues: FormValues = {
    dispersionStartDate: null,
    dispersionEndDate: null,
    fixedAmount: '',
    file: null,
  };

  const handleSubmit = async (values: FormValues): Promise<void> => {
    try {
      const dispersionStartDate = values.dispersionStartDate
        ? format(new Date(values.dispersionStartDate), 'yyyy-MM-dd')
        : null;
      const dispersionEndDate = values.dispersionEndDate
        ? format(new Date(values.dispersionEndDate), 'yyyy-MM-dd')
        : null;

      const res = await createChildPaymentPlan({
        dispersionStartDate,
        dispersionEndDate,
        ...(isTopUp && values.file
          ? { file: values.file }
          : {}),
        ...(isTopUp && !values.file && values.fixedAmount
          ? { fixedAmount: values.fixedAmount }
          : {}),
      });
      setDialogOpen(false);
      showMessage(t('Payment Plan Created'));
      navigate(`/${baseUrl}/payment-module/${detailPath}/${res.id}`);
    } catch (e) {
      showApiErrorMessages(e, showMessage);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      validateOnChange
      validateOnBlur
    >
      {({ submitForm, values, setValues, resetForm }) => {
        const closeDialog = (): void => {
          setDialogOpen(false);
          resetForm();
          selectedFile.current = null;
          setFundedRows(null);
        };
        return (
        <Form>
          <Box
            sx={{
              p: 2,
            }}
          >
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setDialogOpen(true)}
              data-cy={`button-create-${variant}`}
              data-perm={PERMISSIONS.PM_CREATE}
              disabled={
                !hasPermissions(PERMISSIONS.PM_CREATE, permissions) ||
                !isActiveProgram
              }
            >
              {labels.button}
            </Button>
          </Box>
          <Dialog
            open={dialogOpen}
            onClose={closeDialog}
            scroll="paper"
            maxWidth="md"
          >
            <DialogTitleWrapper>
              <DialogTitle>{labels.title}</DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogContainer>
                <Box
                  sx={{
                    p: 5,
                  }}
                >
                  {isFollowUp && (
                    <>
                      <Box
                        sx={{
                          display: 'flex',
                          flexDirection: 'column',
                        }}
                      >
                        {paymentPlan.unsuccessfulPaymentsCount === 0 && (
                          <Box
                            sx={{
                              mb: 2,
                            }}
                          >
                            <FieldBorder color="#FF0200">
                              <GreyText>
                                {t(
                                  'Follow-up Payment Plan might be started just for unsuccessful payments',
                                )}
                              </GreyText>
                            </FieldBorder>
                          </Box>
                        )}
                        {paymentPlan.totalWithdrawnHouseholdsCount > 0 && (
                          <Box
                            sx={{
                              mb: 4,
                            }}
                          >
                            <FieldBorder color="#FF0200">
                              <GreyText>
                                {t(
                                  `Withdrawn ${beneficiaryGroup?.groupLabel} cannot be added into follow-up payment plan`,
                                )}
                              </GreyText>
                            </FieldBorder>
                          </Box>
                        )}
                      </Box>
                      <Grid container spacing={3}>
                        <Grid size={{ xs: 6 }}>
                          <Box
                            sx={{
                              mt: 2,
                            }}
                          >
                            <Typography>
                              {t('Main Payment Plan Details')}
                            </Typography>
                          </Box>
                        </Grid>
                        <Grid size={{ xs: 6 }} />
                        <Grid size={{ xs: 6 }}>
                          <LabelizedField label={t('Unsuccessful payments')}>
                            {paymentPlan.unsuccessfulPaymentsCount}
                          </LabelizedField>
                        </Grid>
                        <Grid size={{ xs: 6 }}>
                          <LabelizedField
                            label={t(
                              `Withdrawn ${beneficiaryGroup?.groupLabelPlural}`,
                            )}
                          >
                            {paymentPlan.totalWithdrawnHouseholdsCount}
                          </LabelizedField>
                        </Grid>
                      </Grid>
                      <Grid size={{ xs: 12 }}>
                        <DividerLine />
                      </Grid>
                    </>
                  )}
                  {isTopUp && (
                    <>
                      <Box sx={{ mb: 3 }}>
                        <Typography>
                          {t('Configure Top-Up Amount')}
                        </Typography>
                      </Box>
                      <Grid container spacing={3} sx={{ alignItems: 'center' }}>
                        <Grid size={{ xs: 5 }}>
                          <Typography>{t('Fixed')}:</Typography>
                        </Grid>
                        <Grid size={{ xs: 7 }}>
                          <Field
                            name="fixedAmount"
                            type="number"
                            component={FormikTextField}
                            fullWidth
                            disabled={loadingCreate || Boolean(values.file)}
                          />
                        </Grid>
                        <Grid size={{ xs: 5 }}>
                          <Typography>{t('Custom / per Beneficiary')}:</Typography>
                        </Grid>
                        <Grid size={{ xs: 7 }}>
                          <Button
                            color="primary"
                            variant="contained"
                            component="a"
                            download
                            href={`/api/rest/business-areas/${businessArea}/programs/${programId}/payment-plans/${paymentPlan.id}/top-up-amount-template/`}
                            data-cy="button-download-top-up-template"
                          >
                            {t('Download template')}
                          </Button>
                        </Grid>
                        <Grid size={{ xs: 12 }}>
                          <DropzoneField
                            dontShowFilename={false}
                            loading={loadingCreate}
                            onChange={(files) => {
                              const file = files[0] ?? null;
                              // Updater form, not `...values`: DropzoneField memoises its
                              // onDrop with an empty dependency list, so this closure only
                              // ever sees the first render's values.
                              void setValues((previous) => ({
                                ...previous,
                                file,
                                // The file wins on submit, so drop whatever was typed above.
                                ...(file ? { fixedAmount: '' } : {}),
                              }));
                              selectedFile.current = file;
                              setFundedRows(null);
                              if (!file) return;
                              void countTopUpAmountRows(file)
                                .then((count) => {
                                  // Drop a result that lost the race to a newer pick.
                                  if (selectedFile.current === file)
                                    setFundedRows(count);
                                })
                                // A failed preview must not block the upload itself.
                                .catch(() => setFundedRows(null));
                            }}
                          />
                          {fundedRows !== null && (
                            <Box sx={{ mt: 1 }}>
                              <Typography data-cy="top-up-funded-rows">
                                {variant === 'amendment'
                                  ? t('New Top-Up Amendment will be created for')
                                  : t('New Top-Up will be created for')}{' '}
                                {fundedRows}{' '}
                                {fundedRows === 1
                                  ? t('payment')
                                  : t('payments')}
                              </Typography>
                            </Box>
                          )}
                          <GreyText>
                            {variant === 'amendment'
                              ? t(
                                  'Beneficiaries left empty or at zero are not part of this Top-Up Amendment and stay available for a later one.',
                                )
                              : t(
                                  'Beneficiaries left empty or at zero are not part of this Top-Up and stay available for a later one.',
                                )}
                          </GreyText>
                        </Grid>
                      </Grid>
                      <Grid size={{ xs: 12 }}>
                        <DividerLine />
                      </Grid>
                    </>
                  )}
                  <Box
                    sx={{
                      mb: 3,
                    }}
                  >
                    <Typography>{t('Set the Dispersion Dates')}</Typography>
                  </Box>
                  <Grid container spacing={3}>
                    <Grid size={{ xs: 6 }}>
                      <Field
                        name="dispersionStartDate"
                        label={t('Dispersion Start Date')}
                        component={FormikDateField}
                        required
                        disabled={loadingCreate}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color="disabled" />
                        }
                        data-cy="input-dispersion-start-date"
                        tooltip={t(
                          'The first day from which payments could be delivered.',
                        )}
                      />
                    </Grid>
                    <Grid size={{ xs: 6 }}>
                      <Field
                        name="dispersionEndDate"
                        label={t('Dispersion End Date')}
                        component={FormikDateField}
                        required
                        minDate={tomorrow}
                        disabled={!values.dispersionStartDate}
                        initialFocusedDate={values.dispersionStartDate}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color="disabled" />
                        }
                        data-cy="input-dispersion-end-date"
                        tooltip={t(
                          'The last day on which payments could be delivered.',
                        )}
                      />
                    </Grid>
                  </Grid>
                </Box>
              </DialogContainer>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button onClick={closeDialog} data-cy="button-cancel">
                {t('Cancel')}
              </Button>
                <LoadingButton
                  loading={loadingCreate}
                  type="submit"
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-submit"
                >
                  {t('Save')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </Dialog>
        </Form>
        );
      }}
    </Formik>
  );
}
