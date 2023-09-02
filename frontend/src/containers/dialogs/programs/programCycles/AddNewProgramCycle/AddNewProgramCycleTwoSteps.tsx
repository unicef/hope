import {
  Box,
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik, FormikValues } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AutoSubmitFormOnEnter } from '../../../../../components/core/AutoSubmitFormOnEnter';
import { GreyText } from '../../../../../components/core/GreyText';
import { LabelizedField } from '../../../../../components/core/LabelizedField';
import { LoadingButton } from '../../../../../components/core/LoadingButton';
import { FormikDateField } from '../../../../../shared/Formik/FormikDateField';
import { FormikTextField } from '../../../../../shared/Formik/FormikTextField';
import { DialogDescription } from '../../../DialogDescription';
import { DialogFooter } from '../../../DialogFooter';
import { DialogTitleWrapper } from '../../../DialogTitleWrapper';

interface AddNewProgramCycleTwoStepsProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  loadingCreate: boolean;
  loadingUpdate: boolean;
  handleCreate: (values: FormikValues) => void;
  handleUpdate: (values: FormikValues) => void;
  previousProgramCycle;
  validationSchemaNewProgramCycle;
  validationSchemaPreviousProgramCycle;
}

export const AddNewProgramCycleTwoSteps = ({
  open,
  setOpen,
  loadingCreate,
  loadingUpdate,
  handleCreate,
  handleUpdate,
  previousProgramCycle,
  validationSchemaNewProgramCycle,
  validationSchemaPreviousProgramCycle,
}: AddNewProgramCycleTwoStepsProps): React.ReactElement => {
  const { t } = useTranslation();
  const [step, setStep] = useState(1);
  const { id, name, startDate } = previousProgramCycle;

  const initialValuesPreviousProgramCycle: {
    [key: string]: string | boolean | number;
  } = {
    previousProgramCycleId: id,
    previousProgramCycleName: name,
    previousProgramCycleStartDate: startDate,
    previousProgramCycleEndDate: undefined,
  };

  const initialValuesNewProgramCycle: {
    [key: string]: string | boolean | number;
  } = {
    newProgramCycleName: '',
    newProgramCycleStartDate: '',
    newProgramCycleEndDate: '',
  };

  return step === 1 ? (
    <Formik
      initialValues={initialValuesPreviousProgramCycle}
      onSubmit={(values) => {
        console.log('values', values);
        handleUpdate(values);
      }}
      validationSchema={validationSchemaPreviousProgramCycle}
    >
      {({ submitForm, values }) => (
        <Form>
          <>
            {open && <AutoSubmitFormOnEnter />}
            <DialogTitleWrapper>
              <DialogTitle>
                <Box display='flex' justifyContent='space-between'>
                  <Box>{t('Add New Programme Cycle')}</Box>
                  <Box>1/2</Box>
                </Box>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                <GreyText>
                  {t(
                    'Before you create a new cycle, it is necessary to specify the end date of the existing cycle',
                  )}
                </GreyText>
              </DialogDescription>
              <Grid container spacing={3}>
                <Grid item xs={6}>
                  <LabelizedField
                    data-cy='previous-program-cycle-name'
                    label={t('Programme Cycle Name')}
                  >
                    {values.previousProgramCycleName}
                  </LabelizedField>
                </Grid>
                <Grid item xs={6}>
                  <LabelizedField
                    data-cy='previous-program-cycle-start-date'
                    label={t('Start Date')}
                  >
                    {values.previousProgramCycleStartDate}
                  </LabelizedField>
                </Grid>
                <Grid item xs={6}>
                  <Field
                    name='previousProgramCycleEndDate'
                    label={t('End Date')}
                    component={FormikDateField}
                    required
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                    data-cy='input-previous-program-cycle-end-date'
                  />
                </Grid>
              </Grid>
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button
                  onClick={() => {
                    setOpen(false);
                    setStep(1);
                  }}
                  data-cy='button-cancel'
                >
                  {t('CANCEL')}
                </Button>
                <LoadingButton
                  loading={loadingUpdate}
                  color='primary'
                  variant='contained'
                  type='submit'
                  onClick={submitForm}
                  data-cy='button-next'
                >
                  {t('Next')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        </Form>
      )}
    </Formik>
  ) : (
    <Formik
      initialValues={initialValuesNewProgramCycle}
      onSubmit={(values) => {
        console.log('values', values);
        handleCreate(values);
      }}
      validationSchema={validationSchemaNewProgramCycle}
    >
      {({ submitForm }) => (
        <Form>
          <>
            <DialogTitleWrapper>
              <DialogTitle>
                <Box display='flex' justifyContent='space-between'>
                  <Box>{t('Add New Programme Cycle')}</Box>
                  <Box>2/2</Box>
                </Box>
              </DialogTitle>
            </DialogTitleWrapper>
            <DialogContent>
              <DialogDescription>
                <GreyText>
                  {t('Enter data for the new Programme Cycle')}
                </GreyText>
              </DialogDescription>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Field
                    name='newProgramCycleName'
                    fullWidth
                    variant='outlined'
                    label={t('Programme Cycle Title')}
                    component={FormikTextField}
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <Field
                    name='newProgramCycleStartDate'
                    label={t('Start Date')}
                    component={FormikDateField}
                    required
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Field
                    name='newProgramCycleEndDate'
                    label={t('End Date')}
                    component={FormikDateField}
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color='disabled' />}
                  />
                </Grid>
              </Grid>
              )
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button
                  onClick={() => {
                    setOpen(false);
                    setStep(1);
                  }}
                  data-cy='button-cancel'
                >
                  {t('CANCEL')}
                </Button>
                <LoadingButton
                  loading={loadingCreate}
                  type='submit'
                  color='primary'
                  variant='contained'
                  onClick={submitForm}
                  data-cy='button-create'
                >
                  {t('Create')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        </Form>
      )}
    </Formik>
  );
};
