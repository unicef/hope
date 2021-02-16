import React, { useState } from 'react';
import moment from 'moment';
import * as Yup from 'yup';
import get from 'lodash/get';
import { Field, Form, Formik } from 'formik';
import {
  Button,
  DialogContent,
  DialogTitle,
  Typography,
  Paper,
  Grid,
} from '@material-ui/core';
import styled from 'styled-components';
import CalendarTodayRoundedIcon from '@material-ui/icons/CalendarTodayRounded';
import { Dialog } from '../../containers/dialogs/Dialog';
import { DialogActions } from '../../containers/dialogs/DialogActions';
import { useSnackbar } from '../../hooks/useSnackBar';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikDateField } from '../../shared/Formik/FormikDateField';
import {
  useAllProgramsQuery,
  useCreateReportMutation,
  useReportChoiceDataQuery,
} from '../../__generated__/graphql';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { LoadingComponent } from '../LoadingComponent';
import { ALL_REPORTS_QUERY } from '../../apollo/queries/AllReports';
import { FormikAdminAreaAutocompleteMultiple } from '../../shared/Formik/FormikAdminAreaAutocomplete/FormikAdminAreaAutocompleteMultiple';
import { REPORT_TYPES } from '../../utils/constants';
import { FieldLabel } from '../FieldLabel';

const DialogTitleWrapper = styled.div`
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogFooter = styled.div`
  padding: 12px 16px;
  margin: 0;
  border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  text-align: right;
`;

const validationSchema = Yup.object().shape({
  reportType: Yup.string().required('Report type is required'),
  dateFrom: Yup.date().required('Date From is required'),
  dateTo: Yup.date()
    .when(
      'dateFrom',
      (dateFrom, schema) =>
        dateFrom &&
        schema.min(
          dateFrom,
          `End date have to be greater than
          ${moment(dateFrom).format('YYYY-MM-DD')}`,
        ),
      '',
    )
    .required('Date To is required'),
});
export const NewReportForm = (): React.ReactElement => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const {
    data: allProgramsData,
    loading: loadingPrograms,
  } = useAllProgramsQuery({
    variables: { businessArea, status: ['ACTIVE'] },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useReportChoiceDataQuery();
  const [mutate] = useCreateReportMutation();

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
          label='Administrative Level 2'
          variant='outlined'
          component={FormikAdminAreaAutocompleteMultiple}
        />
      </Grid>
    );
    const programField = (
      <Grid item xs={12}>
        <Field
          name='program'
          label='Programme'
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
        label = 'Last Registration Date';
        break;
      case REPORT_TYPES.CASH_PLAN_VERIFICATION:
      case REPORT_TYPES.PAYMENT_VERIFICATION:
        label = 'Completion Date';
        break;
      case REPORT_TYPES.PAYMENTS:
      case REPORT_TYPES.INDIVIDUALS_AND_PAYMENT:
        label = 'Delivery Date';
        break;
      case REPORT_TYPES.CASH_PLAN:
      case REPORT_TYPES.PROGRAM:
        label = 'End Date';
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
        NEW REPORT
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
              <DialogTitleWrapper>
                <DialogTitle id='scroll-dialog-title' disableTypography>
                  <Typography variant='h6'>Generate New Report</Typography>
                </DialogTitle>
              </DialogTitleWrapper>
              <DialogContent>
                <Form>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <Field
                        name='reportType'
                        label='Report Type'
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
                            label='From Date'
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
                            label='To Date'
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
                  <Button onClick={() => setDialogOpen(false)}>CANCEL</Button>
                  <Button
                    type='submit'
                    color='primary'
                    variant='contained'
                    onClick={submitForm}
                    data-cy='button-submit'
                  >
                    GENERATE
                  </Button>
                </DialogActions>
              </DialogFooter>
            </>
          )}
        </Formik>
      </Dialog>
    </>
  );
};
