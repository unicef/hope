import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { decodeIdString, today } from '@utils/utils';
import moment from 'moment';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
} from '@mui/material';
import EditIcon from '@mui/icons-material/EditRounded';
import { Field, Formik } from 'formik';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { GreyText } from '@core/GreyText';
import Grid from '@mui/material/Grid';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { LoadingButton } from '@core/LoadingButton';
import {
  ProgramCycle,
  ProgramCycleUpdate,
  ProgramCycleUpdateResponse,
  updateProgramCycle,
} from '@api/programCycleApi';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ProgramQuery } from '@generated/graphql';
import type { DefaultError } from '@tanstack/query-core';
import { useSnackbar } from '@hooks/useSnackBar';

interface EditProgramCycleProps {
  programCycle: ProgramCycle;
  program: ProgramQuery['program'];
}

export const EditProgramCycle = ({
  programCycle,
  program,
}: EditProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation<
    ProgramCycleUpdateResponse,
    DefaultError,
    ProgramCycleUpdate
  >({
    mutationFn: async (body) => {
      return updateProgramCycle(
        businessArea,
        program.id,
        decodeIdString(programCycle.id),
        body,
      );
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['programCycles', businessArea, program.id],
      });
      setOpen(false);
    },
  });

  const handleUpdate = async (values: any): Promise<void> => {
    try {
      await mutateAsync(values);
      showMessage(t('Programme Cycle Updated'));
    } catch (e) {
      showMessage(e.message);
    }
  };

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    title: programCycle.title,
    start_date: programCycle.start_date,
    end_date: programCycle.end_date,
  };

  const validationSchema = Yup.object().shape({
    title: Yup.string()
      .required(t('Programme Cycle title is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    start_date: Yup.date().required(t('Start Date is required')),
    end_date: Yup.date()
      .required(t('End Date is required'))
      .min(today, t('End Date cannot be in the past'))
      .when(
        'start_date',
        (start_date, schema) =>
          start_date &&
          schema.min(
            start_date,
            `${t('End date have to be greater than')} ${moment(
              start_date,
            ).format('YYYY-MM-DD')}`,
          ),
      ),
  });

  return (
    <>
      <IconButton
        onClick={() => {
          setOpen(true);
        }}
        color="primary"
        data-cy="button-edit-program-cycle"
      >
        <EditIcon />
      </IconButton>
      <Dialog open={open} onClose={() => setOpen(false)} scroll="paper">
        <Formik
          initialValues={initialValues}
          onSubmit={handleUpdate}
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
                      decoratorEnd={
                        <CalendarTodayRoundedIcon color="disabled" />
                      }
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Field
                      name="end_date"
                      label={t('End Date')}
                      component={FormikDateField}
                      fullWidth
                      decoratorEnd={
                        <CalendarTodayRoundedIcon color="disabled" />
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
                    data-cy="button-cancel"
                  >
                    {t('CANCEL')}
                  </Button>
                  <LoadingButton
                    loading={isPending}
                    color="primary"
                    variant="contained"
                    onClick={submitForm}
                    data-cy="button-save"
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
