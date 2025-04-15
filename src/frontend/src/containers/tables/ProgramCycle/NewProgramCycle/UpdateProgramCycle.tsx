import {
  ProgramCycle,
  ProgramCycleUpdate,
  ProgramCycleUpdateResponse,
  updateProgramCycle,
} from '@api/programCycleApi';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { GreyText } from '@core/GreyText';
import { LabelizedField } from '@core/LabelizedField';
import { LoadingButton } from '@core/LoadingButton';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import {
  Box,
  Button,
  DialogContent,
  DialogTitle,
  FormHelperText,
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import type { DefaultError } from '@tanstack/query-core';
import { useMutation } from '@tanstack/react-query';
import { decodeIdString, today } from '@utils/utils';
import { Field, Form, Formik, FormikValues } from 'formik';
import moment from 'moment';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';

interface UpdateProgramCycleProps {
  program: ProgramDetail;
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
    startDate: programCycle.start_date,
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
        end_date: values.endDate,
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
                  {values.startDate}
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
                {error?.data?.endDate && (
                  <FormHelperText error>{error.data.endDate}</FormHelperText>
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
