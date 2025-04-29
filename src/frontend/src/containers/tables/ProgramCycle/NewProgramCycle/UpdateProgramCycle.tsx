import { ProgramQuery } from '@generated/graphql';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  FormHelperText,
} from '@mui/material';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { LoadingButton } from '@core/LoadingButton';
import { useTranslation } from 'react-i18next';
import { Field, Form, Formik, FormikValues } from 'formik';
import { decodeIdString, today } from '@utils/utils';
import moment from 'moment';
import * as Yup from 'yup';
import { GreyText } from '@core/GreyText';
import Grid from '@mui/material/Grid2';
import { LabelizedField } from '@core/LabelizedField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import {
  ProgramCycle,
  ProgramCycleUpdate,
  ProgramCycleUpdateResponse,
  updateProgramCycle,
} from '@api/programCycleApi';
import { useMutation } from '@tanstack/react-query';
import type { DefaultError } from '@tanstack/query-core';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import withErrorBoundary from '@components/core/withErrorBoundary';

interface UpdateProgramCycleProps {
  program: ProgramQuery['program'];
  programCycle?: ProgramCycle;
  onClose: () => void;
  onSubmit: () => void;
  step?: string;
}

interface MutationError extends DefaultError {
  data: any;
}

const UpdateProgramCycle = ({
  program,
  programCycle,
  onClose,
  onSubmit,
  step,
}: UpdateProgramCycleProps) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();

  let endDate = Yup.date()
    .required(t('End Date is required'))
    .min(today, t('End Date cannot be in the past'))
    .when('start_date', ([start_date], schema) =>
      start_date
        ? schema.min(
            new Date(start_date),
            `${t('End date have to be greater than')} ${moment(
              start_date,
            ).format('YYYY-MM-DD')}`,
          )
        : schema,
    );

  if (program.endDate) {
    endDate = endDate.max(
      new Date(program.endDate),
      t('End Date cannot be after Programme End Date'),
    );
  }
  const validationSchema = Yup.object().shape({
    end_date: endDate,
  });

  const initialValues: {
    [key: string]: string | boolean | number | null;
  } = {
    id: programCycle.id,
    title: programCycle.title,
    start_date: programCycle.start_date,
    end_date: undefined,
  };

  const { mutateAsync, isPending, error } = useMutation<
    ProgramCycleUpdateResponse,
    MutationError,
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
    onSuccess: () => {
      onSubmit();
    },
  });

  const handleSubmit = async (values: FormikValues) => {
    try {
      await mutateAsync({
        title: programCycle.title,
        start_date: programCycle.start_date,
        end_date: values.end_date,
      });
      showMessage(t('Programme Cycle Updated'));
    } catch (e) {
      /* empty */
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ submitForm, values }) => (
        <Form>
          <DialogTitleWrapper>
            <DialogTitle>
              <Box display="flex" justifyContent="space-between">
                <Box>{t('Add New Programme Cycle')}</Box>
                {step && <Box>{step}</Box>}
              </Box>
            </DialogTitle>
          </DialogTitleWrapper>
          <DialogContent>
            <DialogDescription>
              <GreyText>
                {t(
                  'Before you create a new Cycle, it is necessary to specify the end date of the existing Cycle',
                )}
              </GreyText>
            </DialogDescription>
            <Grid container spacing={3}>
              <Grid size={{ xs: 6 }}>
                <LabelizedField
                  data-cy="previous-program-cycle-title"
                  label={t('Programme Cycle Title')}
                >
                  {values.title}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 6 }}>
                <LabelizedField
                  data-cy="previous-program-cycle-start-date"
                  label={t('Start Date')}
                >
                  {values.start_date}
                </LabelizedField>
              </Grid>
              <Grid size={{ xs: 6 }}>
                <Field
                  name="end_date"
                  label={t('End Date')}
                  component={FormikDateField}
                  required
                  fullWidth
                  decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                  data-cy="input-previous-program-cycle-end-date"
                />
                {error?.data?.end_date && (
                  <FormHelperText error>{error.data.end_date}</FormHelperText>
                )}
              </Grid>
            </Grid>
          </DialogContent>
          <DialogFooter>
            <DialogActions>
              <Button data-cy="button-cancel" onClick={onClose}>
                {t('CANCEL')}
              </Button>
              <LoadingButton
                loading={isPending}
                color="primary"
                variant="contained"
                onClick={submitForm}
                data-cy="button-update-program-cycle-modal"
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

export default withErrorBoundary(UpdateProgramCycle, 'UpdateProgramCycle');
