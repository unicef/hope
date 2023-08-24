import { Box, Button, Grid } from '@material-ui/core';
import ListItem from '@material-ui/core/ListItem';
import makeStyles from '@material-ui/core/styles/makeStyles';
import { Delete } from '@material-ui/icons';
import { Field, Formik } from 'formik';
import React, { ReactElement } from 'react';
import { Draggable } from 'react-beautiful-dnd';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';
import {
  useAllDeliveryMechanismsQuery,
  useAvailableFspsForDeliveryMechanismsQuery,
} from '../../../__generated__/graphql';
import { FormikSelectField } from '../../../shared/Formik/FormikSelectField';
import { BaseSection } from '../../core/BaseSection';
import { ErrorButton } from '../../core/ErrorButton';
import { LoadingComponent } from '../../core/LoadingComponent';

type Item = {
  id: string;
};

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
  const { t } = useTranslation();
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
  if (!deliveryMechanismsData || !fspsData) return null;
  if (deliveryMechanismLoading || fspsLoading) return <LoadingComponent />;

  const initialValues = {
    id: item.id,
    deliveryMechanism: '',
    fsp: '',
  };

  return (
    <Formik
      initialValues={initialValues}
      onSubmit={(values) => {
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
              <Box mr={2}>
                <ErrorButton
                  variant='outlined'
                  onClick={() => handleDeletePaymentInstruction(item.id)}
                >
                  <Delete />
                </ErrorButton>
              </Box>
              <Button onClick={submitForm} variant='contained' color='primary'>
                {t('Save')}
              </Button>
            </Box>
          </>
        );
        return (
          <Draggable draggableId={item.id} index={index}>
            {(provided, snapshot) => (
              <ListItem
                ref={provided.innerRef}
                {...provided.draggableProps}
                {...provided.dragHandleProps}
                className={snapshot.isDragging ? classes.draggingListItem : ''}
              >
                <BaseSection
                  title={`Payment Instruction #${item.id}`}
                  buttons={buttons}
                >
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
                </BaseSection>
              </ListItem>
            )}
          </Draggable>
        );
      }}
    </Formik>
  );
};
