import {
  Button,
  DialogContent,
  DialogTitle,
  Grid,
  Paper,
  Typography,
} from '@material-ui/core';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Field, Form, Formik } from 'formik';
import get from 'lodash/get';
import moment from 'moment';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { ALL_REPORTS_QUERY } from '../../apollo/queries/reporting/AllReports';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { DialogFooter } from '../../containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '../../containers/dialogs/DialogTitleWrapper';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikAdminAreaAutocompleteMultiple } from '../../shared/Formik/FormikAdminAreaAutocomplete/FormikAdminAreaAutocompleteMultiple';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { REPORT_TYPES } from '../../utils/constants';
import {
  useAllProgramsQuery,
  useCreateReportMutation,
  useReportChoiceDataQuery,
} from '../../__generated__/graphql';
import { AutoSubmitFormOnEnter } from '../core/AutoSubmitFormOnEnter';
import { FieldLabel } from '../core/FieldLabel';
import { LoadingButton } from '../core/LoadingButton';
import { LoadingComponent } from '../core/LoadingComponent';

export const NewReportForm = (): React.ReactElement => {
  const { t } = useTranslation();
  const [dialogOpen, setDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();

  const validationSchema = Yup.object().shape({
    reportType: Yup.string().required(t('Report type is required')),
    dateFrom: Yup.date().required(t('Date From is required')),
    dateTo: Yup.date()
      .when(
        'dateFrom',
        (dateFrom, schema) =>
          dateFrom &&
          schema.min(
            dateFrom,
            `${t('End date have to be greater than')}
            ${moment(dateFrom).format('YYYY-MM-DD')}`,
          ),
        '',
      )
      .required(t('Date To is required')),
  });

  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsQuery({
    variables: { businessArea, status: ['ACTIVE'] },
    fetchPolicy: 'cache-and-network',
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();
  const [mutate, { loading }] = useCreateReportMutation();

  if (loadingPrograms || choicesLoading) return <LoadingComponent />;
  const allProgramsEdges = get(allProgramsData, 'allPrograms.edges', []);
  const mappedPrograms = allProgramsEdges.map((edge) => ({
    name: edge.node.name,
    value: edge.node.id,
  }));

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const initialValue: { [key: string]: any } = {
    reportType: '',
    dateFrom: '',
    dateTo: '',
    adminArea: [],
    program: '',
  };

  // eslint-disable-next-line @typescript-eslint/explicit-function-return-type
  const prepareVariables = (values) => {
    const shouldSendAdminAreaField =
      values.reportType === REPORT_TYPES.INDIVIDUALS ||
      values.reportType === REPORT_TYPES.HOUSEHOLD_DEMOGRAPHICS ||
      values.reportType === REPORT_TYPES.PAYMENTS;

    const shouldSendProgramField =
      values.reportType === REPORT_TYPES.CASH_PLAN_VERIFICATION ||
      values.reportType === REPORT_TYPES.PAYMENT_VERIFICATION ||
      values.reportType === REPORT_TYPES.CASH_PLAN;

    const shouldSendBothFields =
      values.reportType === REPORT_TYPES.INDIVIDUALS_AND_PAYMENT;

    let variables = null;

    const basicVariables = {
      businessAreaSlug: businessArea,
      reportType: values.reportType,
      dateFrom: values.dateFrom,
      dateTo: values.dateTo,
    };

    if (shouldSendAdminAreaField) {
      variables = {
        ...basicVariables,
        adminArea: values.adminArea.map((el) => el.node.id),
      };
    }
    if (shouldSendProgramField) {
      variables = {
        ...basicVariables,
        program: values.program,
      };
    }
    if (shouldSendBothFields) {
      variables = {
        ...basicVariables,
        program: values.program,
        adminArea: values.adminArea.map((el) => el.node.id),
      };
    }
    return variables || basicVariables;
  };

  const submitFormHandler = async (values): Promise<void> => {
    const response = await mutate({
      variables: {
        reportData: prepareVariables(values),
      },
      refetchQueries: () => [
        { query: ALL_REPORTS_QUERY, variables: { businessArea } },
      ],
    });
    if (!response.errors && response.data.createReport) {
      showMessage('Report created.', {
        pathname: `/${businessArea}/reporting/${response.data.createReport.report.id}`,
        historyMethod: 'push',
      });
    } else {
      showMessage('Report create action failed.');
    }
  };
  const renderConditionalFields = (values): React.ReactElement => {
    const adminAreaField = (
      <Grid item xs={12}>
        <Field
          name='adminArea'
          label={t('Administrative Level 2')}
          variant='outlined'
          component={FormikAdminAreaAutocompleteMultiple}
        />
      </Grid>
    );
    const programField = (
      <Grid item xs={12}>
        <Field
          name='program'
          label={t('Programme')}
          fullWidth
          variant='outlined'
          choices={mappedPrograms}
          component={FormikSelectField}
        />
      </Grid>
    );
    const showOnlyAdminAreaField =
      values.reportType === REPORT_TYPES.INDIVIDUALS ||
      values.reportType === REPORT_TYPES.HOUSEHOLD_DEMOGRAPHICS ||
      values.reportType === REPORT_TYPES.PAYMENTS;

    const showOnlyProgramField =
      values.reportType === REPORT_TYPES.CASH_PLAN_VERIFICATION ||
      values.reportType === REPORT_TYPES.PAYMENT_VERIFICATION ||
      values.reportType === REPORT_TYPES.CASH_PLAN;

    const showBothFields =
      values.reportType === REPORT_TYPES.INDIVIDUALS_AND_PAYMENT;

    let fields = null;

    if (showOnlyAdminAreaField) {
      fields = adminAreaField;
    }
    if (showOnlyProgramField) {
      fields = programField;
    }
    if (showBothFields) {
      fields = (
        <>
          {adminAreaField}
          {programField}
        </>
      );
    }
    return fields;
  };
  const renderTimeframeLabel = (reportType: string): string => {
    let label = '';
    switch (reportType) {
      case REPORT_TYPES.INDIVIDUALS:
      case REPORT_TYPES.HOUSEHOLD_DEMOGRAPHICS:
        label = t('Last Registration Date');
        break;
      case REPORT_TYPES.CASH_PLAN_VERIFICATION:
      case REPORT_TYPES.PAYMENT_VERIFICATION:
        label = t('Completion Date');
        break;
      case REPORT_TYPES.PAYMENTS:
      case REPORT_TYPES.INDIVIDUALS_AND_PAYMENT:
        label = t('Delivery Date');
        break;
      case REPORT_TYPES.CASH_PLAN:
      case REPORT_TYPES.PROGRAM:
        label = t('End Date');
        break;
      default:
        break;
    }
    return label;
  };

  return (
    <>
      <Button
        color='primary'
        variant='contained'
        onClick={() => setDialogOpen(true)}
      >
        {t('NEW REPORT')}
      </Button>
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        scroll='paper'
        PaperComponent={React.forwardRef((props, ref) => (
          <Paper
            {...{
              ...props,
              ref,
            }}
            data-cy='dialog-setup-new-report'
          />
        ))}
        aria-labelledby='form-dialog-title'
      >
        <Formik
          initialValues={initialValue}
          onSubmit={submitFormHandler}
          validationSchema={validationSchema}
        >
          {({ submitForm, values }) => (
            <>
              {dialogOpen && <AutoSubmitFormOnEnter />}
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>
                    {t('Generate New Report')}
                  </Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <Form>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Field
                        name='reportType'
                        label={t('Report Type')}
                        fullWidth
                        variant='outlined'
                        required
                        choices={choicesData.reportTypesChoices}
                        component={FormikSelectField}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <FieldLabel>
                        {renderTimeframeLabel(values.reportType)}
                      </FieldLabel>

                      <Grid container spacing={3}>
                        <Grid item xs={6}>
                          <Field
                            name='dateFrom'
                            label={t('From Date')}
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
                            name='dateTo'
                            label={t('To Date')}
                            component={FormikDateField}
                            required
                            disabled={!values.dateFrom}
                            initialFocusedDate={values.dateFrom}
                            fullWidth
                            decoratorEnd={
                              <CalendarTodayRoundedIcon color='disabled' />
                            }
                            minDate={values.dateFrom}
                          />
                        </Grid>
                      </Grid>
                    </Grid>
                    {renderConditionalFields(values)}
                  </Grid>
                </Form>
              </DialogContent>
              <DialogFooter>
                <DialogActions>
                  <Button onClick={() => setDialogOpen(false)}>
                    {t('CANCEL')}
                  </Button>
                  <LoadingButton
                    loading={loading}
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-submit'
                  >
                    {t('GENERATE')}
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
