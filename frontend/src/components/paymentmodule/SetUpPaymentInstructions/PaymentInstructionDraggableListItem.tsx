import { Avatar, Box, Button, Grid } from '@material-ui/core';
import ListItem from '@material-ui/core/ListItem';
import makeStyles from '@material-ui/core/styles/makeStyles';
import { Field, FieldArray, Form, Formik } from 'formik';
import React, { ReactElement, useEffect, useState } from 'react';
import { Draggable } from 'react-beautiful-dnd';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';
import {
  useAllDeliveryMechanismsQuery,
  useAvailableFspsForDeliveryMechanismsQuery,
} from '../../../__generated__/graphql';
import { PERMISSIONS, hasPermissions } from '../../../config/permissions';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { useCachedImportedIndividualFieldsQuery } from '../../../hooks/useCachedImportedIndividualFields';
import { usePermissions } from '../../../hooks/usePermissions';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { associatedWith, isNot } from '../../../utils/utils';
import { BaseSection } from '../../core/BaseSection';
import { DividerLine } from '../../core/DividerLine';
import { LoadingComponent } from '../../core/LoadingComponent';
import { UniversalCriteriaPlainComponent } from '../../core/UniversalCriteriaComponent/UniversalCriteriaPlainComponent';
import { DeletePaymentInstruction } from './DeletePaymentInstruction';

type Item = {
  id: string;
};

const StyledAvatar = styled(Avatar)`
  color: #000 !important;
  background-color: #e6e6e6 !important;
`;

const AvatarTitle = styled(Box)`
  color: #000 !important;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1.5px;
`;

const AvatarId = styled(Box)`
  color: #000 !important;
  font-size: 20px;
  font-weight: 500;
`;

const useStyles = makeStyles({
  draggingListItem: {
    background: 'rgb(235,235,235)',
  },
});

export type PaymentInstructionDraggableListItemProps = {
  item: Item;
  index: number;
  handleDeletePaymentInstruction: (id: string) => void;
};

export const PaymentInstructionDraggableListItem = ({
  item,
  index,
  handleDeletePaymentInstruction,
}: PaymentInstructionDraggableListItemProps): ReactElement => {
  const classes = useStyles();
  const { id } = useParams();
  const [individualData, setIndividualData] = useState(null);
  const [householdData, setHouseholdData] = useState(null);
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const permissions = usePermissions();
  const canDeletePaymentInstruction = hasPermissions(
    PERMISSIONS.PM_DELETE_PAYMENT_INSTRUCTIONS,
    permissions,
  );
  const {
    data: deliveryMechanismsData,
    loading: deliveryMechanismLoading,
  } = useAllDeliveryMechanismsQuery({
    fetchPolicy: 'network-only',
  });

  const {
    data: fspsData,
    loading: fspsLoading,
  } = useAvailableFspsForDeliveryMechanismsQuery({
    variables: {
      input: {
        paymentPlanId: id,
      },
    },
    fetchPolicy: 'network-only',
  });

  const { data, loading } = useCachedImportedIndividualFieldsQuery(
    businessArea,
  );
  useEffect(() => {
    if (loading) return;
    const filteredIndividualData = {
      allFieldsAttributes: data?.allFieldsAttributes
        ?.filter(associatedWith('Individual'))
        .filter(isNot('IMAGE')),
    };
    setIndividualData(filteredIndividualData);

    const filteredHouseholdData = {
      allFieldsAttributes: data?.allFieldsAttributes?.filter(
        associatedWith('Household'),
      ),
    };
    setHouseholdData(filteredHouseholdData);
  }, [data, loading]);

  if (!deliveryMechanismsData || !fspsData) return null;
  if (deliveryMechanismLoading || fspsLoading) return <LoadingComponent />;

  const initialValues = {
    id: item.id,
    deliveryMechanism: '',
    fsp: '',
    criteria: [],
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
        // eslint-disable-next-line no-console
        console.log(values);
      }}
    >
      {({ submitForm, values, setFieldValue }) => {
        const deliveryMechanismsChoices = deliveryMechanismsData.allDeliveryMechanisms.map(
          (el) => ({
            name: el.name,
            value: el.value,
          }),
        );

        const computeFspsChoices = (): Array<{
          name: string;
          value: string;
        }> => {
          if (!values.deliveryMechanism || !fspsData) return [];

          const matchedDeliveryMechanism = fspsData.availableFspsForDeliveryMechanisms.find(
            (el) => el.deliveryMechanism === values.deliveryMechanism,
          );

          if (!matchedDeliveryMechanism) return [];

          return matchedDeliveryMechanism.fsps.map((el) => ({
            name: el.name,
            value: el.id,
          }));
        };

        const fspsChoices = computeFspsChoices();

        const buttons = (
          <>
            <Box display='flex' justifyContent='center' alignItems='center'>
              <Box mr={4}>
                <DeletePaymentInstruction
                  canDeletePaymentInstruction={canDeletePaymentInstruction}
                  handleDeletePaymentInstruction={
                    handleDeletePaymentInstruction
                  }
                  index={index}
                  program={null}
                  item={item}
                />
              </Box>
              <Button onClick={submitForm} variant='contained' color='primary'>
                {t('Save')}
              </Button>
            </Box>
          </>
        );

        const title = (
          <Box display='flex' alignItems='center'>
            <StyledAvatar data-cy='payment-instruction-index'>
              #{index + 1}
            </StyledAvatar>
            <Box ml={4} display='flex' flexDirection='column'>
              <AvatarTitle>{t('Payment Instruction')}</AvatarTitle>
              <AvatarId data-cy='payment-instruction-id'>
                ID: {item.id}
              </AvatarId>
            </Box>
          </Box>
        );

        return (
          <Form>
            <Draggable
              data-cy='draggable-payment-instruction-tile'
              draggableId={item.id}
              index={index}
            >
              {(provided, snapshot) => {
                return (
                  <ListItem
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                    className={
                      snapshot.isDragging ? classes.draggingListItem : ''
                    }
                  >
                    <BaseSection title={title} buttons={buttons}>
                      <>
                        <Box mt={2}>
                          <Grid container>
                            <Grid item xs={4}>
                              <Box mr={4}>
                                <Field
                                  name='deliveryMechanism'
                                  variant='outlined'
                                  label={t('Delivery Mechanism')}
                                  component={FormikSelectField}
                                  additionalOnChange={() => {
                                    setFieldValue('fsp', '');
                                  }}
                                  choices={deliveryMechanismsChoices}
                                />
                              </Box>
                            </Grid>
                            <Grid item xs={4}>
                              <Field
                                name='fsp'
                                variant='outlined'
                                label={t('FSP')}
                                component={FormikSelectField}
                                choices={fspsChoices}
                              />
                            </Grid>
                          </Grid>
                        </Box>
                        <DividerLine />
                        <Grid container>
                          <Box mb={2}>
                            <FieldArray
                              name='criteria'
                              render={(arrayHelpers) => (
                                <UniversalCriteriaPlainComponent
                                  isEdit
                                  arrayHelpers={arrayHelpers}
                                  rules={values.criteria}
                                  householdFieldsChoices={
                                    householdData?.allFieldsAttributes || []
                                  }
                                  individualFieldsChoices={
                                    individualData?.allFieldsAttributes || []
                                  }
                                />
                              )}
                            />
                          </Box>
                        </Grid>
                      </>
                    </BaseSection>
                  </ListItem>
                );
              }}
            </Draggable>
          </Form>
        );
      }}
    </Formik>
  );
};
