import { Box, Button, Grid } from '@material-ui/core';
import { Link, useParams } from 'react-router-dom';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';
import styled from 'styled-components';
import { AddCircleOutline } from '@material-ui/icons';
import { FieldArray, Form, Formik } from 'formik';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as Yup from 'yup';
import { ContainerColumnWithBorder } from '../../../components/core/ContainerColumnWithBorder';
import { PermissionDenied } from '../../../components/core/PermissionDenied';
import { DeliveryMechanismRow } from '../../../components/paymentmodule/CreateSetUpFsp/DeliveryMechanismRow';
import { EditSetUpFspHeader } from '../../../components/paymentmodule/EditSetUpFsp/EditSetUpFspHeader';
import { hasPermissions, PERMISSIONS } from '../../../config/permissions';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { usePermissions } from '../../../hooks/usePermissions';
import { useSnackbar } from '../../../hooks/useSnackBar';
import { getTargetingCriteriaVariables } from '../../../utils/targetingUtils';
import { handleValidationErrors } from '../../../utils/utils';
import { useCreateTpMutation } from '../../../__generated__/graphql';

const StyledBox = styled(Box)`
  width: 100%;
`;

export const EditSetUpFspPage = (): React.ReactElement => {
  const { t } = useTranslation();
  const { id } = useParams();
  const [activeStep, setActiveStep] = useState(0);
  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };
  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };
  const initialValues = {
    deliveryMechanisms: [
      {
        deliveryMechanism: '',
        fsp: '',
      },
    ],
  };
  const [mutate] = useCreateTpMutation();
  const { showMessage } = useSnackbar();
  const businessArea = useBusinessArea();
  const permissions = usePermissions();

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.TARGETING_CREATE, permissions))
    return <PermissionDenied />;

  const validationSchema = Yup.object().shape({});

  const handleSubmit = async (values, { setFieldError }): Promise<void> => {
    try {
      const res = await mutate({
        variables: {
          input: {
            programId: values.program,
            name: values.name,
            excludedIds: values.excludedIds,
            exclusionReason: values.exclusionReason,
            businessAreaSlug: businessArea,
            ...getTargetingCriteriaVariables(values),
          },
        },
      });
      showMessage(t('Target Population Created'), {
        pathname: `/${businessArea}/target-population/${res.data.createTargetPopulation.targetPopulation.id}`,
        historyMethod: 'push',
      });
    } catch (e) {
      const { nonValidationErrors } = handleValidationErrors(
        'createTargetPopulation',
        e,
        setFieldError,
        showMessage,
      );
      if (nonValidationErrors.length > 0) {
        showMessage(t('Unexpected problem while creating Target Population'));
      }
    }
  };

  const steps = [
    t('Choose Delivery Mechanism Order'),
    t('Assign FSP per Delivery Mechanism'),
  ];

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={(values) => console.log(values)}
    >
      {({ submitForm, values }) => {
        return (
          <Form>
            <EditSetUpFspHeader
              handleSubmit={submitForm}
              businessArea={businessArea}
              permissions={permissions}
            />
            <Box m={5}>
              <ContainerColumnWithBorder>
                <StyledBox>
                  <Stepper activeStep={activeStep}>
                    {steps.map((step) => {
                      return (
                        <Step key={step}>
                          <StepLabel>{step}</StepLabel>
                        </Step>
                      );
                    })}
                  </Stepper>
                </StyledBox>
                <FieldArray
                  name='deliveryMechanisms'
                  render={(arrayHelpers) => {
                    return (
                      <>
                        {values.deliveryMechanisms.map((item, index) => (
                          <DeliveryMechanismRow
                            baseName='mobileMoney'
                            index={index}
                            step={activeStep}
                            values={values}
                          />
                        ))}
                        {activeStep === 0 && (
                          <Grid container>
                            <Grid item xs={12}>
                              <Box>
                                <Button
                                  color='primary'
                                  startIcon={<AddCircleOutline />}
                                  onClick={() => {
                                    arrayHelpers.push({
                                      deliveryMechanism: '',
                                      fsp: '',
                                    });
                                  }}
                                >
                                  {t('Add Delivery Mechanism')}
                                </Button>
                              </Box>
                            </Grid>
                          </Grid>
                        )}
                      </>
                    );
                  }}
                />
                <Box display='flex'>
                  <Box mr={3}>
                    {activeStep === 0 && (
                      <Button
                        component={Link}
                        to={`/${businessArea}/payment-module/payment-plan/${id}`}
                      >
                        {t('Cancel')}
                      </Button>
                    )}
                    {activeStep === 1 && (
                      <Button onClick={handleBack}>{t('Back')}</Button>
                    )}
                  </Box>
                  <Button
                    variant='contained'
                    color='primary'
                    onClick={handleNext}
                  >
                    {t('Next')}
                  </Button>
                </Box>
              </ContainerColumnWithBorder>
            </Box>
          </Form>
        );
      }}
    </Formik>
  );
};
