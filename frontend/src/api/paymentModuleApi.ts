import axios from 'axios';

export const fetchPaymentPlansManagerial = async (businessAreaSlug) => {
  const { data } = await axios.get(
    `/rest/${businessAreaSlug}/payments/payment-plans-managerial`,
  );
  return data;
};
