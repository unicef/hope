import * as Yup from 'yup';
import { today } from '@utils/utils';
import moment from 'moment/moment';
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
import { GreyText } from '@core/GreyText';
import Grid from '@mui/material/Grid2';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import CalendarTodayRoundedIcon from '@mui/icons-material/CalendarTodayRounded';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createProgramCycle,
  ProgramCycleCreate,
  ProgramCycleCreateResponse,
} from '@api/programCycleApi';
import type { DefaultError } from '@tanstack/query-core';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';

interface CreateProgramCycleProps {
  program: ProgramDetail;
  onClose: () => void;
  onSubmit: () => void;
  step?: string;
}

interface MutationError extends DefaultError {
  data: any;
}

const CreateProgramCycle = ({
  program,
  onClose,
  onSubmit,
  step,
}: CreateProgramCycleProps) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const queryClient = useQueryClient();
  const { showMessage } = useSnackbar();

  let endDate = Yup.date()
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
    title: Yup.string()
      .required(t('Programme Cycle Title is required'))
      .min(2, t('Too short'))
      .max(150, t('Too long')),
    startDate: Yup.date()
      .required(t('Start Date is required'))
      .min(
        program.startDate,
        t('Start Date cannot be before Programme Start Date'),
      ),
    end_date: endDate,
  });

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    title: '',
    startDate: undefined,
    end_date: undefined,
  };

  const { mutateAsync, isPending, error } = useMutation<
    ProgramCycleCreateResponse,
    MutationError,
    ProgramCycleCreate
  >({
    mutationFn: async (body) => {
      return createProgramCycle(businessArea, program.id, body);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['programCycles', businessArea, program.id],
      });
      onSubmit();
    },
  });

  const handleSubmit = async (values: FormikValues) => {
    try {
      await mutateAsync({
        title: values.title,
        start_date: values.startDate,
        end_date: values.endDate,
      });
      showMessage(t('Programme Cycle Created'));
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
      {({ submitForm }) => (
        <Form>
          <>
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
                  {t('Enter data for the new Programme Cycle')}
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
                  {error?.data?.title && (
                    <FormHelperText error>{error.data.title}</FormHelperText>
                  )}
                </Grid>
                <Grid size={{ xs: 6 }} data-cy="start-date-cycle">
                  <Field
                    name="startDate"
                    label={t('Start Date')}
                    component={FormikDateField}
                    required
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
                  />
                  {error?.data?.startDate && (
                    <FormHelperText error>
                      {error.data.startDate}
                    </FormHelperText>
                  )}
                </Grid>
                <Grid size={{ xs: 6 }} data-cy="end-date-cycle">
                  <Field
                    name="end_date"
                    label={t('End Date')}
                    component={FormikDateField}
                    fullWidth
                    decoratorEnd={<CalendarTodayRoundedIcon color="disabled" />}
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
                  data-cy="button-create-program-cycle"
                >
                  {t('CREATE')}
                </LoadingButton>
              </DialogActions>
            </DialogFooter>
          </>
        </Form>
      )}
    </Formik>
  );
};

export default withErrorBoundary(CreateProgramCycle, 'CreateProgramCycle');
