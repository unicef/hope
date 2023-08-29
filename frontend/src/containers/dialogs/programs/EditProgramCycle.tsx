import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
} from '@material-ui/core';
import { Edit } from '@material-ui/icons';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
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
import { LoadingButton } from '../../../components/core/LoadingButton';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { FormikDateField } from '../../../shared/Formik/FormikDateField';
import { FormikTextField } from '../../../shared/Formik/FormikTextField';
import { programCompare, today } from '../../../utils/utils';
import { DialogDescription } from '../DialogDescription';
import { DialogFooter } from '../DialogFooter';
import { DialogTitleWrapper } from '../DialogTitleWrapper';

interface EditProgramCycleProps {
  program: ProgramNode;
  canEditProgramCycle: boolean;
}

export const EditProgramCycle = ({
  program,
  canEditProgramCycle,
}: EditProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { baseUrl, businessArea } = useBaseUrl();

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

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
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
    startDate: Yup.date().required(t('Start Date is required')),
    endDate: Yup.date()
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
    startDate: '',
    endDate: '',
  };

  return (
    <>
      <IconButton
        onClick={() => setOpen(true)}
        color='primary'
        data-cy='button-edit-program-cycle'
        disabled={!canEditProgramCycle}
      >
        <Edit />
      </IconButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll='paper'>
        <Formik
          initialValues={initialValues}
          onSubmit={(values) => {
            // eslint-disable-next-line no-console
            console.log(values);
          }}
          validationSchema={validationSchema}
        >
          {({ submitForm }) => (
            <>
              {open && <AutoSubmitFormOnEnter />}
              <DialogTitleWrapper>
                <DialogTitle>{t('Edit Programme Cycle')}</DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <DialogDescription>
                  <GreyText>
                    {t('Change details of the Programme Cycle')}
                  </GreyText>
                </DialogDescription>
                <Grid container spacing={3}>
                  <Grid item xs={12}>
                    <Field
                      name='title'
                      fullWidth
                      variant='outlined'
                      label={t('Programme Cycle Title')}
                      component={FormikTextField}
                      required
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Field
                      name='startDate'
                      label={t('Start Date')}
                      component={FormikDateField}
                      required
                      fullWidth
                      decoratorEnd={
                        <CalendarTodayRoundedIcon color='disabled' />
                      }
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Field
                      name='endDate'
                      label={t('End Date')}
                      component={FormikDateField}
                      fullWidth
                      decoratorEnd={
                        <CalendarTodayRoundedIcon color='disabled' />
                      }
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
                    loading={loading}
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-save'
                  >
                    {t('Save')}
                  </LoadingButton>
                </DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </>
  );
};
