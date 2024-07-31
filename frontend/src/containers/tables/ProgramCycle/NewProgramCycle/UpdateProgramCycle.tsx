import { ProgramQuery } from '@generated/graphql';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { Box, Button, DialogContent, DialogTitle } from '@mui/material';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { LoadingButton } from '@core/LoadingButton';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { Field, Form, Formik, FormikHelpers, FormikValues } from 'formik';
import { today } from '@utils/utils';
import moment from 'moment';
import * as Yup from 'yup';
import { GreyText } from '@core/GreyText';
import Grid from '@mui/material/Grid';
import { LabelizedField } from '@core/LabelizedField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { ProgramCycle } from '@api/programCycleApi';

interface UpdateProgramCycleProps {
  program: ProgramQuery['program'];
  programCycle?: ProgramCycle;
  onClose: () => void;
  onSubmit: () => void;
  step?: string;
}

export const UpdateProgramCycle = ({
  program,
  programCycle,
  onClose,
  onSubmit,
  step,
}: UpdateProgramCycleProps) => {
  const { t } = useTranslation();

  const validationSchemaPreviousProgramCycle = Yup.object().shape({
    previousProgramCycleEndDate: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .max(program.endDate, t('End Date cannot be after Programme End Date'))
      .when(
        'previousProgramCycleStartDate',
        (previousProgramCycleStartDate, schema) =>
          previousProgramCycleStartDate &&
          schema.min(
            previousProgramCycleStartDate,
            `${t('End date have to be greater than')} ${moment(
              previousProgramCycleStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
      ),
  });

  const initialValuesPreviousProgramCycle: {
    [key: string]: string | boolean | number | null;
  } = {
    previousProgramCycleId: programCycle.id,
    previousProgramCycleName: programCycle.title,
    previousProgramCycleStartDate: programCycle.start_date,
    previousProgramCycleEndDate: undefined,
  };

  // TODO connect with API
  const handleSubmit = (
    values: FormikValues,
    formikHelpers: FormikHelpers<FormikValues>,
  ) => {
    onSubmit();
  };

  return (
    <Formik
      initialValues={initialValuesPreviousProgramCycle}
      validationSchema={validationSchemaPreviousProgramCycle}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values }) => (
        <Form>
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
                {t(
                  'Before you create a new Cycles, it is necessary to specify the end date of the existing Cycles',
                )}
              </GreyText>
            </DialogDescription>
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <LabelizedField
                  data-cy="previous-program-cycle-name"
                  label={t('Programme Cycle Name')}
                >
                  {values.previousProgramCycleName}
                </LabelizedField>
              </Grid>
              <Grid item xs={6}>
                <LabelizedField
                  data-cy="previous-program-cycle-start-date"
                  label={t('Start Date')}
                >
                  {values.previousProgramCycleStartDate}
                </LabelizedField>
              </Grid>
              <Grid item xs={6}>
                <Field
                  name="previousProgramCycleEndDate"
                  label={t('End Date')}
                  component={FormikDateField}
                  required
                  fullWidth
                  decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                  data-cy="input-previous-program-cycle-end-date"
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
                loading={false}
                type="submit"
                color="primary"
                variant="contained"
                onClick={submitForm}
                data-cy="button-activate-program-modal"
              >
                {t('NEXT')}
              </LoadingButton>
            </DialogActions>
          </DialogFooter>
        </Form>
      )}
    </Formik>
  );
};
