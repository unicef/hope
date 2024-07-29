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
import { Field, Form, Formik, FormikHelpers, FormikValues } from 'formik';
import { GreyText } from '@core/GreyText';
import Grid from '@mui/material/Grid';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';

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

  const validationSchema = Yup.object().shape({
    newProgramCycleName: Yup.string()
      .required(t('Programme Cycle name is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    newProgramCycleStartDate: Yup.date().required(t('Start Date is required')),
    newProgramCycleEndDate: Yup.date()
      .min(today, t('End Date cannot be in the past'))
      .max(program.endDate, t('End Date cannot be after Programme End Date'))
      .when(
        'newProgramCycleStartDate',
        ([newProgramCycleStartDate], schema) =>
          newProgramCycleStartDate &&
          schema.min(
            newProgramCycleStartDate,
            `${t('End date have to be greater than')} ${moment(
              newProgramCycleStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
      ),
  });

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    newProgramCycleName: '',
    newProgramCycleStartDate: undefined,
    newProgramCycleEndDate: undefined,
  };

  // TODO connect with API
  const handleSubmit = (
    values: FormikValues,
    formikHelpers: FormikHelpers<FormikValues>,
  ) => {
    onSubmit();
  };

  const loading = false;

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
                    name="newProgramCycleName"
                    fullWidth
                    variant="outlined"
                    label={t('Programme Cycle Title')}
                    component={FormikTextField}
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <Field
                    name="newProgramCycleStartDate"
                    label={t('Start Date')}
                    component={FormikDateField}
                    required
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Field
                    name="newProgramCycleEndDate"
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
                  loading={loading}
                  type="submit"
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
