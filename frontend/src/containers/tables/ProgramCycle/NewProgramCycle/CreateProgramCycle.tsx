import * as Yup from 'yup';
import { today } from '@utils/utils';
import moment from 'moment/moment';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { LoadingButton } from '@core/LoadingButton';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramQuery } from '@generated/graphql';
import { Field, Form, Formik, FormikValues } from 'formik';
import { GreyText } from '@core/GreyText';
import Grid from '@mui/material/Grid';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createProgramCycle,
  ProgramCycleCreate,
  ProgramCycleCreateResponse,
} from '@api/programCycleApi';
import { DefaultError } from '@tanstack/query-core';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';

interface CreateProgramCycleProps {
  program: ProgramQuery['program'];
  onClose: () => void;
  onSubmit: () => void;
  step?: string;
}

export const CreateProgramCycle = ({
  program,
  onClose,
  onSubmit,
  step,
}: CreateProgramCycleProps) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const queryClient = useQueryClient();
  const { showMessage } = useSnackbar();

  const validationSchema = Yup.object().shape({
    title: Yup.string()
      .required(t('Programme Cycle name is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    start_date: Yup.date().required(t('Start Date is required')),
    end_date: Yup.date()
      .min(today, t('End Date cannot be in the past'))
      .max(program.endDate, t('End Date cannot be after Programme End Date'))
      .when(
        'start_date',
        ([start_date], schema) =>
          start_date &&
          schema.min(
            start_date,
            `${t('End date have to be greater than')} ${moment(
              start_date,
            ).format('YYYY-MM-DD')}`,
          ),
      ),
  });

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    title: '',
    start_date: undefined,
    end_date: undefined,
  };

  const { mutateAsync, isPending } = useMutation<
    ProgramCycleCreateResponse,
    DefaultError,
    ProgramCycleCreate
  >({
    mutationFn: async (body) => {
      return createProgramCycle(businessArea, program.id, body);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['programCycles', businessArea, program.id],
      });
      onSubmit();
    },
  });

  const handleSubmit = async (values: FormikValues) => {
    try {
      await mutateAsync({
        title: values.title,
        start_date: values.start_date,
        end_date: values.end_date,
      });
      showMessage(t('Programme Cycle Created'));
    } catch (e) {
      e.data?.forEach((message: string) => showMessage(message));
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm }) => (
        <Form>
          <>
            <DialogTitleWrapper>
              <DialogTitle>
                <Box display="flex" justifyContent="space-between">
                  <Box>{t('Add New Programme Cycles')}</Box>
                  {step && <Box>{step}</Box>}
                </Box>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                <GreyText>
                  {t('Are you sure you want to activate this Programme?')}
                </GreyText>
              </DialogDescription>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Field
                    name="title"
                    fullWidth
                    variant="outlined"
                    label={t('Programme Cycle Title')}
                    component={FormikTextField}
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <Field
                    name="start_date"
                    label={t('Start Date')}
                    component={FormikDateField}
                    required
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Field
                    name="end_date"
                    label={t('End Date')}
                    component={FormikDateField}
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button data-cy="button-cancel" onClick={onClose}>
                  {t('CANCEL')}
                </Button>
                <LoadingButton
                  loading={isPending}
                  color="primary"
                  variant="contained"
                  onClick={submitForm}
                  data-cy="button-create-program-cycle"
                >
                  {t('CREATE')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        </Form>
      )}
    </Formik>
  );
};
