import withErrorBoundary from '@components/core/withErrorBoundary';
import { DialogActions } from '@containers/dialogs/DialogActions';
import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { GreyText } from '@core/GreyText';
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
  Grid,
} from '@mui/material';
import { ProgramCycleCreate } from '@restgenerated/models/ProgramCycleCreate';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { RestService } from '@restgenerated/services/RestService';
import { FormikDateField } from '@shared/Formik/FormikDateField';
import { FormikTextField } from '@shared/Formik/FormikTextField';
import type { DefaultError } from '@tanstack/query-core';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { showApiErrorMessages, today } from '@utils/utils';
import { Field, Form, Formik, FormikValues } from 'formik';
import moment from 'moment/moment';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';

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
    endDate: endDate,
  });

  const initialValues: {
    [key: string]: string | boolean | number;
  } = {
    title: '',
    startDate: undefined,
    endDate: undefined,
  };

  const { mutateAsync, isPending, error } = useMutation<
    ProgramCycleCreate,
    MutationError,
    ProgramCycleCreate
  >({
    mutationFn: async (body) => {
      return RestService.restBusinessAreasProgramsCyclesCreate({
        businessAreaSlug: businessArea,
        programSlug: program.slug,
        requestBody: body,
      });
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['programCycles'],
        exact: false,
      });
      onSubmit();
    },
  });

  const handleSubmit = async (values: FormikValues) => {
    try {
      await mutateAsync({
        title: values.title,
        startDate: values.startDate,
        endDate: values.endDate,
      });
      showMessage(t('Programme Cycle Created'));
    } catch (e) {
      showApiErrorMessages(e, showMessage);
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
                <Grid size={12}>
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
                <Grid size={6} data-cy="start-date-cycle">
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
                <Grid size={6} data-cy="end-date-cycle">
                  <Field
                    name="endDate"
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
