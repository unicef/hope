import { Box, Button } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import React from 'react';
import { DropResult } from 'react-beautiful-dnd';
import { useTranslation } from 'react-i18next';
import { v4 as uuidv4 } from 'uuid';
import { PermissionDenied } from '../../../../components/core/PermissionDenied';
import { PaymentInstructionDraggableList } from '../../../../components/paymentmodule/SetUpPaymentInstructions/PaymentInstructionDraggableList';
import { SetUpPaymentInstructionsHeader } from '../../../../components/paymentmodule/SetUpPaymentInstructions/SetUpPaymentInstructionsHeader';
import { reorder } from '../../../../components/paymentmodule/SetUpPaymentInstructions/helpers';
import { PERMISSIONS, hasPermissions } from '../../../../config/permissions';
import { useBaseUrl } from '../../../../hooks/useBaseUrl';
import { usePermissions } from '../../../../hooks/usePermissions';

export const SetUpPaymentInstructionsPage = (): React.ReactElement => {
  const { baseUrl } = useBaseUrl();
  const { t } = useTranslation();
  const permissions = usePermissions();
  const [items, setItems] = React.useState([
    { id: '1' },
    { id: '2' },
    { id: '3' },
    { id: '4' },
  ]);

  const onDragEnd = ({ destination, source }: DropResult): void => {
    // dropped outside the list
    if (!destination) return;

    const newItems = reorder(items, source.index, destination.index);

    setItems(newItems);
  };

  const handleAddNewPaymentInstruction = (): void => {
    setItems([...items, { id: uuidv4() }]);
  };

  const handleDeletePaymentInstruction = (id: string): void => {
    setItems(items.filter((item) => item.id !== id));
  };

  const buttons = (
    <Box display='flex' justifyContent='center'>
      <Box mr={2}>
        <Button
          variant='outlined'
          color='primary'
          endIcon={<AddCircleOutline />}
          onClick={handleAddNewPaymentInstruction}
          data-cy='add-new-payment-instruction-button'
        >
          {t('Add New Payment Instruction')}
        </Button>
      </Box>
      <Button
        variant='contained'
        color='primary'
        data-cy='confirm-reorder-button'
        onClick={() =>
          // eslint-disable-next-line no-console
          console.log(
            'new order:',
            items.map((item) => item.id),
          )
        }
      >
        {t('Confirm Reorder')}
      </Button>
    </Box>
  );

  if (permissions === null) return null;
  if (!hasPermissions(PERMISSIONS.PM_SET_UP_PAYMENT_INSTRUCTIONS, permissions))
    return <PermissionDenied />;

  return (
    <>
      <SetUpPaymentInstructionsHeader
        baseUrl={baseUrl}
        permissions={permissions}
        buttons={buttons}
      />
      <PaymentInstructionDraggableList
        items={items}
        onDragEnd={onDragEnd}
        handleDeletePaymentInstruction={handleDeletePaymentInstruction}
      />
    </>
  );
};
