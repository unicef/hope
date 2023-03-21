import {
  Action,
  PaymentPlanDocument,
  useActionPpMutation,
} from '../__generated__/graphql';
import { useSnackbar } from './useSnackBar';

interface PaymentPlanAction {
  loading: boolean;
  mutatePaymentPlanAction: (comment?: string) => Promise<void>;
}

export const usePaymentPlanAction = (
  action: Action,
  paymentPlanId: string,
  onSuccess: () => void,
  onClose?: () => void,
): PaymentPlanAction => {
  const [mutate, { loading }] = useActionPpMutation();
  const { showMessage } = useSnackbar();
  const mutatePaymentPlanAction = async (comment?: string): Promise<void> => {
    try {
      await mutate({
        variables: {
          input: {
            paymentPlanId,
            action,
            comment,
          },
        },
        refetchQueries: () => [
          {
            query: PaymentPlanDocument,
            variables: { id: paymentPlanId },
            fetchPolicy: 'network-only',
          },
          'AllPaymentsForTable',
        ],
      });
      onSuccess();
    } catch (e) {
      e.graphQLErrors.map((x) => showMessage(x.message));
    }
    if (onClose) {
      onClose();
    }
  };
  return { loading, mutatePaymentPlanAction };
};
