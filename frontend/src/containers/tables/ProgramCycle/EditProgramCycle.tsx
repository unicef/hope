import ProgramCycle from '@containers/tables/ProgramCycle/ProgramCycle';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { today } from '@utils/utils';
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

interface EditProgramCycleProps {
  programCycle: ProgramCycle;
}

export const EditProgramCycle = ({
  programCycle,
}: EditProgramCycleProps): React.ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);

  const loading = false;

  // TODO connect with API
  const handleUpdate = (values): void => {
    console.log(values);
    setOpen(false);
  };

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    name: programCycle.name,
    startDate: programCycle.start_date,
    endDate: programCycle.end_date,
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
                      name="name"
                      fullWidth
                      variant="outlined"
                      label={t('Programme Cycle Title')}
                      component={FormikTextField}
                      required
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Field
                      name="startDate"
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
                      name="endDate"
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
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpen(false);
                    }}
                    data-cy="button-cancel"
                  >
                    {t('CANCEL')}
                  </Button>
                  <LoadingButton
                    loading={loading}
                    type="submit"
                    color="primary"
                    variant="contained"
                    onClick={(e) => {
                      e.stopPropagation();
                      void submitForm();
                    }}
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
