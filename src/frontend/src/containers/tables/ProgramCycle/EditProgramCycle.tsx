import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { showApiErrorMessages, today } from '@utils/utils';
import moment from 'moment';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  IconButton,
} from '@mui/material';
import EditIcon from '@mui/icons-material/EditRounded';
import { Field, Formik } from 'formik';
import { AutoSubmitFormOnEnter } from '@core/AutoSubmitFormOnEnter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { GreyText } from '@core/GreyText';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { LoadingButton } from '@core/LoadingButton';
import { RestService } from '@restgenerated/services/RestService';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { ProgramCycleList } from '@restgenerated/models/ProgramCycleList';

interface EditProgramCycleProps {
  programCycle: ProgramCycleList;
  program: ProgramDetail;
}

const EditProgramCycle = ({
  programCycle,
  program,
}: EditProgramCycleProps): ReactElement => {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const queryClient = useQueryClient();

  const { mutateAsync, isPending } = useMutation<
    any,
    any,
    { title: string; startDate: string; endDate?: string }
  >({
    mutationFn: async (body) => {
      return RestService.restBusinessAreasProgramsCyclesPartialUpdate({
        businessAreaSlug: businessArea,
        id: programCycle.id,
        programSlug: program.slug ?? program.id,
        requestBody: body,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['programCycles', businessArea, program.slug],
      });
      setOpen(false);
    },
  });

  const isEndDateRequired = !!programCycle.endDate;

  const handleUpdate = async (values: any): Promise<void> => {
    try {
      await mutateAsync({
        title: values.title,
        startDate: values.startDate,
        endDate: values.endDate,
      });
      showMessage(t('Programme Cycle Updated'));
    } catch (e) {
      showApiErrorMessages(e, showMessage, t('Error updating Programme Cycle'));
    }
  };

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    title: programCycle.title,
    startDate: programCycle.startDate,
    endDate: programCycle.endDate ?? undefined,
  };

  const endDateValidationSchema = () => {
    let validation = Yup.date()
      .min(today, t('End Date cannot be in the past'))
      .when('startDate', ([startDate], schema) =>
        startDate
          ? schema.min(
              new Date(startDate),
              `${t('End date have to be greater than')} ${moment(
                startDate,
              ).format('YYYY-MM-DD')}`,
            )
          : schema,
      );

    if (program.endDate) {
      validation = validation.max(
        new Date(program.endDate),
        t('End Date cannot be after Programme End Date'),
      );
    }

    if (isEndDateRequired) {
      validation = validation.required(t('End Date is required'));
    }

    return validation;
  };

  const validationSchema = Yup.object().shape({
    title: Yup.string()
      .required(t('Programme Cycle title is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    startDate: Yup.date()
      .required(t('Start Date is required'))
      .min(
        program.startDate,
        t('Start Date cannot be before Programme Start Date'),
      ),
    end_date: endDateValidationSchema(),
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
                  <Grid size={{ xs: 12 }}>
                    <Field
                      name="title"
                      fullWidth
                      variant="outlined"
                      label={t('Programme Cycle Title')}
                      component={FormikTextField}
                      required
                    />
                  </Grid>
                  <Grid size={{ xs: 6 }} data-cy="start-date-cycle">
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
                  <Grid size={{ xs: 6 }} data-cy="end-date-cycle">
                    <Field
                      name="end_date"
                      label={t('End Date')}
                      component={FormikDateField}
                      required={isEndDateRequired}
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

export default withErrorBoundary(EditProgramCycle, 'EditProgramCycle');
