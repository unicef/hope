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
  ProgramNode,
  useUpdateProgramMutation,
  AllProgramsQuery,
  ProgramStatus,
  useUpdateProgramCycleMutation,
} from '../../../../__generated__/graphql';
import { ALL_PROGRAMS_QUERY } from '../../../../apollo/queries/program/AllPrograms';
import { PROGRAM_QUERY } from '../../../../apollo/queries/program/Program';
import { AutoSubmitFormOnEnter } from '../../../../components/core/AutoSubmitFormOnEnter';
import { GreyText } from '../../../../components/core/GreyText';
import { LoadingButton } from '../../../../components/core/LoadingButton';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { useSnackbar } from '../../../../hooks/useSnackBar';
import { FormikDateField } from '../../../../shared/Formik/FormikDateField';
import { FormikTextField } from '../../../../shared/Formik/FormikTextField';
import { programCompare, today } from '../../../../utils/utils';
import { DialogDescription } from '../../DialogDescription';
import { DialogFooter } from '../../DialogFooter';
import { DialogTitleWrapper } from '../../DialogTitleWrapper';

interface EditProgramCycleProps {
  programCycle: ProgramNode;
  canEditProgramCycle: boolean;
}

export const EditProgramCycle = ({
  programCycle,
  canEditProgramCycle,
}: EditProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const { programId } = useBaseUrl();

  const [mutate, { loading }] = useUpdateProgramCycleMutation();

  const handleUpdate = async (values): Promise<void> => {
    const { name, startDate, endDate } = values;
    try {
      await mutate({
        variables: {
          programCycleData: {
            programCycleId: programCycle.id,
            name,
            startDate,
            endDate,
          },
        },
        refetchQueries: () => [
          {
            query: PROGRAM_QUERY,
            variables: { id: programId },
          },
        ],
      });
      showMessage('Programme Cycle deleted.');
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
  };

  const validationSchema = Yup.object().shape({
    name: Yup.string()
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
    name: '',
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
            handleUpdate(values);
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
                      name='name'
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
