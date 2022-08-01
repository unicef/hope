import {
  Action,
  PaymentPlanDocument,
  useActionPpMutation,
} from '../__generated__/graphql';

interface PaymentPlanAction {
  loading: boolean;
  mutatePaymentPlanAction: (comment?: string) => Promise<void>;
}

export const usePaymentPlanAction = (
  action: Action,
  paymentPlanId: string,
  onSuccess: () => void,
  onError: () => void,
): PaymentPlanAction => {
  const [mutate, { loading }] = useActionPpMutation();
  const mutatePaymentPlanAction = async (comment?: string) => {
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
          },
        ],
      });
      onSuccess();
    } catch (error) {
      /* eslint-disable-next-line no-console */
      console.log('error', error?.graphQLErrors);
      onError();
    }
  };
  return { loading, mutatePaymentPlanAction };
};
