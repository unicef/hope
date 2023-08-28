import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Add } from '@material-ui/icons';
import { Field, Formik } from 'formik';
import moment from 'moment';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import {
  AllProgramsQuery,
  ProgramNode,
  ProgramStatus,
  useUpdateProgramMutation,
} from '../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../apollo/queries/program/AllPrograms';
import { PROGRAM_QUERY } from '../../../apollo/queries/program/Program';
import { AutoSubmitFormOnEnter } from '../../../components/core/AutoSubmitFormOnEnter';
import { GreyText } from '../../../components/core/GreyText';
import { LabelizedField } from '../../../components/core/LabelizedField';
import { LoadingButton } from '../../../components/core/LoadingButton';
import { Missing } from '../../../components/core/Missing';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikDateField } from '../../../shared/Formik/FormikDateField';
import { programCompare, today } from '../../../utils/utils';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';

interface AddNewProgramCycleProps {
  program: ProgramNode;
}

export const AddNewProgramCycle = ({
  program,
}: AddNewProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();
  const [step, setStep] = useState(1);

  const [mutate, { loading }] = useUpdateProgramMutation({
    update(cache, { data: { updateProgram } }) {
      cache.writeQuery({
        query: PROGRAM_QUERY,
        variables: {
          id: program.id,
        },
        data: { program: updateProgram.program },
      });
      const allProgramsData: AllProgramsQuery = cache.readQuery({
        query: ALL_PROGRAMS_QUERY,
        variables: { businessArea },
      });
      allProgramsData.allPrograms.edges.sort(programCompare);
      cache.writeQuery({
        query: ALL_PROGRAMS_QUERY,
        variables: { businessArea },
        data: allProgramsData,
      });
    },
  });

  //es-lint-disable-next-line
  const save = async (): Promise<void> => {
    const response = await mutate({
      variables: {
        programData: {
          id: program.id,
          status: ProgramStatus.Active,
        },
        version: program.version,
      },
    });
    if (!response.errors && response.data.updateProgram) {
      showMessage(t('Programme activated.'), {
        pathname: `/${baseUrl}/details/${response.data.updateProgram.program.id}`,
        dataCy: 'snackbar-program-activate-success',
      });
      setOpen(false);
    } else {
      showMessage(t('Programme activate action failed.'), {
        dataCy: 'snackbar-program-activate-failure',
      });
    }
  };

  const validationSchema = Yup.object().shape({
    title: Yup.string()
      .required(t('Programme Cycle title is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    newProgramCycleStartDate: Yup.date().required(t('Start Date is required')),
    newProgramCycleEndDate: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .when(
        'newProgramCycleStartDate',
        (newProgramCycleStartDate, schema) =>
          newProgramCycleStartDate &&
          schema.min(
            newProgramCycleStartDate,
            `${t('End date have to be greater than')} ${moment(
              newProgramCycleStartDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
    existingProgramCycleEndDate: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .when(
        'startDate',
        (startDate, schema) =>
          startDate &&
          schema.min(
            startDate,
            `${t('End date have to be greater than')} ${moment(
              startDate,
            ).format('YYYY-MM-DD')}`,
          ),
        '',
      ),
  });

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    title: '',
    existingProgramCycleStartDate: '',
    newProgramCycleStartDate: '',
    newProgramCycleEndDate: '',
  };

  return (
    <>
      <Button
        startIcon={<Add />}
        variant='outlined'
        color='primary'
        data-cy='button-add-new-program-cycle'
        onClick={() => setOpen(true)}
      >
        {t('Add New Programme Cycle')}
      </Button>
      <Dialog open={open} onClose={() => setOpen(false)} scroll='paper'>
        <Formik
          initialValues={initialValues}
          onSubmit={(values) => {
            console.log(values);
          }}
          validationSchema={validationSchema}
        >
          {({ submitForm }) => (
            <>
              {open && <AutoSubmitFormOnEnter />}
              <DialogTitleWrapper>
                <DialogTitle>
                  <Box display='flex' justifyContent='space-between'>
                    <Box>{t('Add New Programme Cycle')}</Box>
                    <Box>{step === 1 ? '1/2' : '2/2'}</Box>
                  </Box>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  <GreyText>
                    {step === 1
                      ? t(
                          'Before you create a new cycle, it is necessary to specify the end date of the existing cycle',
                        )
                      : t('Enter data for the new Programme Cycle')}
                  </GreyText>
                </DialogDescription>
                {step === 1 ? (
                  <Grid container spacing={3}>
                    <Grid item xs={6}>
                      <LabelizedField label={t('Programme Cycle Title')}>
                        {t('Default Programme Cycle')}
                      </LabelizedField>
                    </Grid>
                    <Grid item xs={6}>
                      <LabelizedField label={t('Start Date')}>
                        <Missing />
                      </LabelizedField>
                    </Grid>
                    <Grid item xs={6}>
                      <Field
                        name='existingProgramCycleEndDate'
                        label={t('End Date')}
                        component={FormikDateField}
                        required
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        data-cy='input-existing-end-date'
                      />
                    </Grid>
                  </Grid>
                ) : (
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Field
                        name='programCycleTitle'
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
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        data-cy='input-new-start-date'
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <Field
                        name='newProgramCycleEndDate'
                        label={t('End Date')}
                        component={FormikDateField}
                        fullWidth
                        decoratorEnd={
                          <CalendarTodayRoundedIcon color='disabled' />
                        }
                        data-cy='input-new-end-date'
                      />
                    </Grid>
                  </Grid>
                )}
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setOpen(false)}>{t('CANCEL')}</Button>
                  {step === 2 && (
                    <LoadingButton
                      loading={loading}
                      type='submit'
                      color='primary'
                      variant='contained'
                      onClick={submitForm}
                      data-cy='button-create'
                    >
                      {t('Create')}
                    </LoadingButton>
                  )}
                  {step === 1 && (
                    <Button
                      color='primary'
                      variant='contained'
                      onClick={() => setStep(2)}
                      data-cy='button-next'
                    >
                      {t('Next')}
                    </Button>
                  )}
                </DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </>
  );
};
