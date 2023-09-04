import {
  Button,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik, FormikValues } from 'formik';
import React from 'react';
import { useTranslation } from 'react-i18next';
import { AutoSubmitFormOnEnter } from '../../../../../components/core/AutoSubmitFormOnEnter';
import { GreyText } from '../../../../../components/core/GreyText';
import { LoadingButton } from '../../../../../components/core/LoadingButton';
import { FormikDateField } from '../../../../../shared/Formik/FormikDateField';
import { FormikTextField } from '../../../../../shared/Formik/FormikTextField';
import { DialogDescription } from '../../../DialogDescription';
import { DialogFooter } from '../../../DialogFooter';
import { DialogTitleWrapper } from '../../../DialogTitleWrapper';

interface AddNewProgramCycleOneStepProps {
  setOpen: (open: boolean) => void;
  open: boolean;
  loadingCreate: boolean;
  handleCreate: (values: FormikValues) => void;
  previousProgramCycle;
  validationSchemaNewProgramCycle;
}

export const AddNewProgramCycleOneStep = ({
  setOpen,
  open,
  loadingCreate,
  handleCreate,
  validationSchemaNewProgramCycle,
  previousProgramCycle,
}: AddNewProgramCycleOneStepProps): React.ReactElement => {
  const { t } = useTranslation();
  const { id, name, startDate, endDate } = previousProgramCycle;

  const initialValuesCreate: {
    [key: string]: string | boolean | number;
  } = {
    newProgramCycleName: '',
    newProgramCycleStartDate: '',
    newProgramCycleEndDate: '',
    previousProgramCycleId: id,
    previousProgramCycleName: name,
    previousProgramCycleStartDate: startDate,
    previousProgramCycleEndDate: endDate,
  };

  return (
    <Formik
      initialValues={initialValuesCreate}
      onSubmit={(values) => {
        handleCreate(values);
      }}
      validationSchema={validationSchemaNewProgramCycle}
    >
      {({ submitForm }) => (
        <Form>
          <>
            {open && <AutoSubmitFormOnEnter />}
            <DialogTitleWrapper>
              <DialogTitle>{t('Add New Programme Cycle')}</DialogTitle>
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
            </DialogContent>
            <DialogFooter>
              <DialogActions>
                <Button
                  onClick={() => {
                    setOpen(false);
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
