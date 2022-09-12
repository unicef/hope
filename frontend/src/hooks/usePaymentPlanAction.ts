import {
  Action,
  AllPaymentsForTableDocument,
  PaymentPlanDocument,
  useActionPpMutation,
} from '../__generated__/graphql';
import { useBusinessArea } from './useBusinessArea';
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
  const businessArea = useBusinessArea();
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
            variables: { paymentPlanId, fspChoices: [] },
          },
          {
            query: AllPaymentsForTableDocument,
            variables: { paymentPlanId, businessArea },
          },
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
